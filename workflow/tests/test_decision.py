import copy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest

import decision as d


class DecisionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.inputs = d.load_json('workflow/demo/inputs.json')
        self.item_count = len(self.inputs['items'])
        self.rubric = d.load_json('rubric/rubric.json')
        self.refs = d.load_json('rubric/examples.json')
        self.response = d.load_json('workflow/demo/demo-results.json')

    def prepare(self):
        return d.prepare(self.root, self.inputs, self.rubric, self.refs, 'test-evaluator')

    def accepted(self):
        batch = self.prepare(); d.accept(self.root, batch, self.response); return batch

    def choice(self, action, **extra):
        row = d.read_state(self.root)['items']['mail-demo-a']
        return {'id':'mail-demo-a','decision_id':row['decision']['id'], 'receipt_id':action, 'action':action, **extra}

    def test_actual_approved_references_and_no_answer_leak(self):
        self.inputs['items'][0].update(expected='SECRET', prior_rating='SECRET', feedback='SECRET')
        proposed = copy.deepcopy(self.refs['references'][0]); proposed.update(id='proposal',status='proposed',content='SECRET')
        self.refs['references'].append(proposed)
        retired = copy.deepcopy(proposed); retired.update(id='retired',status='retired'); self.refs['references'].append(retired)
        same = copy.deepcopy(proposed); same.update(id='self',status='approved',source_id='mail-demo-a'); self.refs['references'].append(same)
        request = self.prepare()['requests'][0]['request']
        serialized = json.dumps(request)
        self.assertNotIn('SECRET',serialized)
        other = copy.deepcopy(self.refs['references'][0]); other.update(id='other-kind',kind='unsupported',content='SECRET')
        self.refs['references'].append(other)
        self.assertNotIn('other-kind', json.dumps(self.prepare()))
        self.assertIn('Please approve the launch copy by April 9',serialized)
        self.assertEqual(request['references'][0]['label'],'act')
        self.assertEqual(request['references'][0]['contrast_ids'],['email-confirmed'])
        self.assertEqual(request['rubric']['rules'],self.rubric['rules'])

    def test_three_treatments_and_uncertainty_survive_review_and_reuse(self):
        import inline_review
        batch = self.prepare()
        self.response['results'][0].update(label='read', uncertainty='The scope of the requested task is missing.')
        self.response['results'][1]['label'] = 'read'
        self.response['results'][2]['label'] = 'skip'
        d.accept(self.root, batch, self.response)
        self.assertEqual(d.summary(self.root)['items'][0]['uncertainty'], 'The scope of the requested task is missing.')
        self.assertEqual(self.prepare()['requests'], [])
        page = d.render(self.root).read_text()
        self.assertIn('Worth seeing', page); self.assertIn('Skip', page)
        self.assertIn('Needs context:', page)
        fragment = inline_review.render(self.root, self.root/'inline.html').read_text()
        self.assertIn('The scope of the requested task is missing.', fragment)
        before = (self.root/'state.json').read_bytes()
        with self.assertRaises(d.Hold):
            d.review(self.root, self.choice('correct', label='skip', note='Ignore it.'))
        self.assertEqual(before, (self.root/'state.json').read_bytes())

    def test_uncertain_suppression_and_obsolete_category_fail_atomically(self):
        batch = self.prepare()
        before = (self.root/'state.json').read_bytes()
        old = copy.deepcopy(batch); old['contract'] = 'coding-agent-v1'
        with self.assertRaises(d.Hold): d.accept(self.root, old, self.response)
        self.assertEqual(before, (self.root/'state.json').read_bytes())
        for change in ({'label':'skip','uncertainty':'Unresolved obligation.'},
                       {'label':'unknown'}, {'uncertainty':True}):
            bad = copy.deepcopy(self.response); bad['results'][-1].update(change)
            with self.assertRaises(d.Hold): d.accept(self.root, batch, bad)
            self.assertEqual(before, (self.root/'state.json').read_bytes())

    def test_uncertain_teaching_reaches_other_targets(self):
        batch = self.prepare()
        self.response['results'][0]['uncertainty'] = 'Confirm the owner.'
        d.accept(self.root, batch, self.response)
        d.review(self.root, self.choice('correct', label='read', note='Clarify who owns this first.'))
        ref_id = d.teach(self.root, self.approval(), self.refs, self.inputs['items'][0])
        batch = d.prepare(self.root, self.inputs, self.rubric, d.load_json(self.root/'references.json'), 'test-evaluator')
        ref = next(r for r in batch['requests'][0]['request']['references'] if r['id']==ref_id)
        self.assertEqual(ref['uncertainty'], 'Confirm the owner.')

    def test_review_persists_and_deduplicates_unchanged_run(self):
        self.accepted()
        choice=self.choice('correct',label='read',note='Wait for the host to specify the adapter.')
        self.assertEqual(d.review(self.root,choice),'saved')
        self.assertEqual(d.review(self.root,choice),'already saved')
        self.assertEqual(self.prepare()['requests'],[])
        item=d.summary(self.root)['items'][0]
        self.assertEqual(item['label'],'read'); self.assertFalse(item['new_review'])
        self.assertEqual(len(d.read_state(self.root)['items']['mail-demo-a']['reviews']),1)

    def test_rubric_update_request_preserves_receipt_without_changing_rubric_or_examples(self):
        self.accepted()
        for name, data in [('rubric.json', self.rubric), ('references.json', self.refs)]:
            (self.root/name).write_text(json.dumps(data))
        before = {name: (self.root/name).read_bytes() for name in ('rubric.json', 'references.json')}
        choice = self.choice('correct', label='read', note='This is wanted reading.', update_rubric=True)
        self.assertEqual(d.review(self.root, choice), 'saved')
        self.assertEqual(d.review(self.root, choice), 'already saved')
        state = d.read_state(self.root)
        self.assertEqual(state['receipts'][choice['receipt_id']], choice)
        self.assertEqual(state['items'][choice['id']]['reviews'], [choice])
        self.assertNotIn('propose_teaching', state['receipts'][choice['receipt_id']])
        for name, content in before.items():
            self.assertEqual((self.root/name).read_bytes(), content)
        # A request alone cannot authorize storing a full-source teaching example.
        with self.assertRaises(d.Hold):
            d.teach(self.root, {'receipt_id': choice['receipt_id']}, self.refs, self.inputs['items'][0])
        self.assertEqual(self.prepare()['requests'], [])
        self.assertIn('Use to update rubric', d.render(self.root).read_text())

    def test_invalid_rubric_update_requests_do_not_write(self):
        self.accepted()
        before = (self.root/'state.json').read_bytes()
        for flag in ('yes', 1, None, {}):
            with self.subTest(flag=flag), self.assertRaises(d.Hold):
                d.review(self.root, self.choice('correct', label='read', note='Wanted reading.', update_rubric=flag))
            self.assertEqual((self.root/'state.json').read_bytes(), before)
        with self.assertRaises(d.Hold):
            d.review(self.root, self.choice('seen', update_rubric=True))
        self.assertEqual((self.root/'state.json').read_bytes(), before)

    def test_changed_inputs_rubric_reference_and_evaluator_reassess(self):
        self.accepted()
        stale=self.choice('seen')
        self.inputs['items'][0]['content']+=' Host now requests a response today.'
        batch=self.prepare(); self.assertEqual(len(batch['requests']),1)
        with self.assertRaises(d.Hold): d.review(self.root,stale)
        response=copy.deepcopy(self.response);response['results']=response['results'][:1]
        d.accept(self.root,batch,response)
        self.assertEqual(len(d.read_state(self.root)['items']['mail-demo-a']['history']),2)
        self.rubric['rules'].append('Require an explicit deadline.')
        self.assertEqual(len(self.prepare()['requests']),self.item_count)
        d.accept(self.root,self.prepare(),self.response)
        self.refs['references'][0]['content']+=' Additional context.'
        self.assertEqual(len(self.prepare()['requests']),self.item_count)
        d.accept(self.root,self.prepare(),self.response)
        self.assertEqual(len(d.prepare(self.root,self.inputs,self.rubric,self.refs,'different-evaluator')['requests']),self.item_count)

    def test_acknowledgment_is_not_completion_and_task_survives_change(self):
        self.accepted();d.review(self.root,self.choice('assign',note='Draft a question; do not send.'))
        d.review(self.root,self.choice('seen'))
        self.assertEqual(d.summary(self.root)['items'][0]['follow_up']['status'],'open')
        self.rubric['version']='next'; batch=self.prepare();d.accept(self.root,batch,self.response)
        self.assertEqual(d.summary(self.root)['items'][0]['follow_up']['status'],'open')
        d.review(self.root,self.choice('complete',note='Reader confirms the draft was completed.'))
        self.assertEqual(d.summary(self.root)['items'][0]['follow_up']['status'],'complete')

    def test_reminder_persists_without_acknowledging_or_completing_and_is_due_at_exact_instant(self):
        self.accepted()
        d.review(self.root, self.choice('assign', note='Draft a reply.'))
        choice = self.choice('remind', reminder={'when': 'at', 'at': '2030-04-09T09:00:00-05:00'})
        self.assertEqual(d.review(self.root, choice), 'saved')
        self.assertEqual(d.review(self.root, choice), 'already saved')
        before = (self.root/'state.json').read_bytes()
        row = d.read_state(self.root)['items']['mail-demo-a']
        self.assertFalse(row['decision']['acknowledged'])
        self.assertEqual(row['task']['status'], 'open')
        self.assertEqual(row['decision']['label'], 'act')
        due = datetime(2030, 4, 9, 14, tzinfo=timezone.utc)
        self.assertFalse(d.summary(self.root, due - timedelta(microseconds=1))['items'][0]['new_review'])
        self.assertTrue(d.summary(self.root, due)['items'][0]['new_review'])
        self.assertTrue(d.summary(self.root, due + timedelta(days=10))['items'][0]['new_review'])
        self.assertEqual((self.root/'state.json').read_bytes(), before)
        with self.assertRaises(d.Hold):
            d.review(self.root, dict(choice, reminder={'when': 'next_review'}))
        self.assertEqual(self.prepare()['requests'], [])
        self.assertEqual(d.read_state(self.root)['receipts']['remind'], choice)

    def test_next_review_replaces_deferral_and_explicit_choices_clear_reminder(self):
        self.accepted()
        for index, (action, extra) in enumerate((('seen', {}), ('assign', {'note': 'Draft a reply.'}),
                                               ('correct', {'label': 'read', 'note': 'Wanted reading.'}))):
            d.review(self.root, self.choice('remind', receipt_id=f'later-{index}', reminder={'when': 'at', 'at': '2099-01-01T00:00:00Z'}))
            self.assertFalse(d.summary(self.root)['items'][0]['new_review'])
            d.review(self.root, self.choice('remind', receipt_id=f'next-{index}', reminder={'when': 'next_review'}))
            self.assertTrue(d.summary(self.root)['items'][0]['new_review'])
            d.review(self.root, self.choice(action, **extra))
            self.assertNotIn('reminder', d.read_state(self.root)['items']['mail-demo-a']['decision'])
            self.assertFalse(d.summary(self.root)['items'][0]['new_review'])
        self.assertEqual(len(d.read_state(self.root)['items']['mail-demo-a']['reviews']), 9)

    def test_invalid_reminder_receipts_fail_without_writes(self):
        self.accepted()
        before = (self.root/'state.json').read_bytes()
        for reminder in (None, 'tomorrow', {}, {'when': 'later'}, {'when': 'next_review', 'content': 'NOT METADATA'},
                         {'when': 'at', 'at': '2030-04-09T09:00:00'}, {'when': 'at', 'at': '2030-02-30T09:00:00Z'},
                         {'when': 'at', 'at': '2030-04-09T09:00:00+01:99'}, {'when': 'at', 'at': '2030-04-09T09:00:00-00:00'},
                         {'when': 'at', 'at': True}, {'when': 'at', 'at': '2030-04-09T09:00:00Z', 'body': 'NOT METADATA'}):
            with self.subTest(reminder=reminder), self.assertRaises(d.Hold):
                d.review(self.root, self.choice('remind', reminder=reminder))
            self.assertEqual((self.root/'state.json').read_bytes(), before)
        with self.assertRaises(d.Hold):
            d.review(self.root, self.choice('seen', reminder={'when': 'next_review'}))
        self.assertEqual((self.root/'state.json').read_bytes(), before)

    def test_reminder_survives_identical_retrieval_recovery_but_not_reassessment(self):
        self.accepted()
        d.review(self.root, self.choice('remind', reminder={'when': 'at', 'at': '2099-01-01T00:00:00Z'}))
        stale = self.choice('remind', receipt_id='old-snapshot', reminder={'when': 'next_review'})
        self.inputs['items'][0]['status'] = 'failed'
        self.prepare()
        with self.assertRaises(d.Hold):
            d.review(self.root, stale)
        self.inputs['items'][0]['status'] = 'complete'
        self.assertEqual(self.prepare()['requests'], [])
        self.assertFalse(d.summary(self.root)['items'][0]['new_review'])
        self.inputs['items'][0]['content'] += ' A new reply changes the situation.'
        batch = self.prepare()
        d.accept(self.root, batch, dict(self.response, results=self.response['results'][:1]))
        with self.assertRaises(d.Hold):
            d.review(self.root, stale)
        self.assertTrue(d.summary(self.root)['items'][0]['new_review'])
        row = d.read_state(self.root)['items']['mail-demo-a']
        self.assertNotIn('reminder', row['decision'])
        self.assertEqual(len(row['history']), 2)
        self.assertEqual(row['reviews'][0]['reminder']['at'], '2099-01-01T00:00:00Z')

    def test_skip_stays_visible_until_user_choice_and_can_be_reminded_without_reclassification(self):
        self.accepted()
        item = d.summary(self.root)['items'][-1]
        self.assertEqual(item['label'], 'skip')
        self.assertTrue(item['new_review'])
        row = d.read_state(self.root)['items'][item['id']]
        d.review(self.root, {'id': item['id'], 'decision_id': row['decision']['id'],
                            'receipt_id': 'skip-shown', 'action': 'delivered', 'note': 'Shown in review.'})
        self.assertEqual(self.prepare()['requests'], [])
        self.assertTrue(d.summary(self.root)['items'][-1]['new_review'])
        d.review(self.root, {'id': item['id'], 'decision_id': row['decision']['id'],
                            'receipt_id': 'skip-confirmed', 'action': 'seen'})
        self.assertFalse(d.summary(self.root)['items'][-1]['new_review'])
        choice = {'id': item['id'], 'decision_id': row['decision']['id'], 'receipt_id': 'skip-reminder',
                  'action': 'remind', 'reminder': {'when': 'at', 'at': '2000-01-01T00:00:00Z'}}
        # A delayed submission is still valid and already due, not quietly lost.
        d.review(self.root, choice)
        item = d.summary(self.root)['items'][-1]
        self.assertEqual(item['label'], 'skip')
        self.assertTrue(item['new_review'])

    def test_text_reminder_requires_resolution_and_preserves_exact_request_and_receipt(self):
        self.accepted()
        request = {'when': 'requested', 'text': ' Tomorrow at 9 AM ', 'timezone': 'America/Chicago',
                   'requested_at': '2030-04-08T17:00:00Z'}
        choice = self.choice('remind', reminder=request)
        before = (self.root/'state.json').read_bytes()
        with self.assertRaises(d.Hold):
            d.review(self.root, choice)
        self.assertEqual((self.root/'state.json').read_bytes(), before)
        self.assertTrue(d.summary(self.root)['items'][0]['new_review'])
        resolution = {'when': 'at', 'at': '2030-04-09T09:00:00-05:00'}
        self.assertEqual(d.review(self.root, choice, resolution), 'saved')
        state = d.read_state(self.root)
        self.assertEqual(state['receipts']['remind'], choice)
        self.assertEqual(state['reminder_resolutions']['remind'], resolution)
        self.assertEqual(state['items']['mail-demo-a']['decision']['reminder'], resolution)
        self.assertEqual(state['items']['mail-demo-a']['reviews'][-1], choice)
        self.assertEqual(d.review(self.root, choice, resolution), 'already saved')
        self.assertEqual(d.review(self.root, choice), 'already saved')
        with self.assertRaises(d.Hold):
            d.review(self.root, choice, {'when': 'next_review'})
        self.assertEqual(d.read_state(self.root), state)
        self.assertEqual(self.prepare()['requests'], [])
        page = d.render(self.root).read_text()
        self.assertIn('Tomorrow at 9 AM', page)
        self.assertIn('Resolved: 2030-04-09T09:00:00-05:00', page)

    def test_invalid_text_request_or_resolution_never_changes_state(self):
        self.accepted()
        request = {'when': 'requested', 'text': 'Friday at 9 AM', 'timezone': 'America/Chicago',
                   'requested_at': '2030-04-08T17:00:00Z'}
        before = (self.root/'state.json').read_bytes()
        for changes in ({'text': ''}, {'text': 'x'*501}, {'timezone': None}, {'timezone': ''},
                        {'requested_at': '2030-04-08T17:00:00'}, {'content': 'Unexpected source'}):
            with self.subTest(changes=changes), self.assertRaises(d.Hold):
                d.review(self.root, self.choice('remind', reminder=dict(request, **changes)), {'when': 'next_review'})
            self.assertEqual((self.root/'state.json').read_bytes(), before)
        for resolution in (request, {'when': 'at', 'at': 'tomorrow'}, {'when': 'at', 'at': '2030-04-09T09:00:00'}):
            with self.subTest(resolution=resolution), self.assertRaises(d.Hold):
                d.review(self.root, self.choice('remind', reminder=request), resolution)
            self.assertEqual((self.root/'state.json').read_bytes(), before)
        with self.assertRaises(d.Hold):
            d.review(self.root, self.choice('seen'), {'when': 'next_review'})
        stale = self.choice('remind', reminder=request)
        self.inputs['items'][0]['content'] += ' New evidence.'
        self.prepare()
        before = (self.root/'state.json').read_bytes()
        with self.assertRaises(d.Hold):
            d.review(self.root, stale, {'when': 'next_review'})
        self.assertEqual((self.root/'state.json').read_bytes(), before)

    def test_cli_resolves_text_request_without_rewriting_submitted_file(self):
        self.accepted()
        choice = self.choice('remind', reminder={'when': 'requested', 'text': 'Next time I review these',
                            'timezone': 'America/Chicago', 'requested_at': '2030-04-08T17:00:00Z'})
        path = self.root/'choice.json'; path.write_text(json.dumps(choice))
        command = [sys.executable, 'workflow/decision.py', 'review', '--root', str(self.root), '--choice', str(path)]
        missing = subprocess.run(command, text=True, capture_output=True)
        self.assertNotEqual(missing.returncode, 0)
        saved = subprocess.run(command + ['--resolve-reminder', 'next_review'], text=True, capture_output=True)
        self.assertEqual(saved.returncode, 0, saved.stderr)
        self.assertEqual(d.load_json(path), choice)
        state = d.read_state(self.root)
        self.assertEqual(state['receipts']['remind'], choice)
        self.assertEqual(state['reminder_resolutions']['remind'], {'when': 'next_review'})
        self.assertTrue(d.summary(self.root)['items'][0]['new_review'])

    def test_missing_failed_sources_and_partial_coverage_preserve_history(self):
        self.accepted();self.inputs['items']=self.inputs['items'][:1]
        self.inputs['items'][0]['status']='failed';self.inputs['coverage']['status']='partial'
        self.assertEqual(self.prepare()['requests'],[])
        state=d.read_state(self.root)
        self.assertEqual(len(state['items']),self.item_count)
        self.assertEqual(state['items']['mail-demo-a']['status'],'held')
        self.assertEqual(len(state['items']['mail-demo-a']['history']),1)
        self.assertFalse(d.summary(self.root)['items'][0]['new_review'])

    def test_retrieval_hold_suspends_then_restores_exact_review_and_task(self):
        import inline_review
        self.accepted()
        d.review(self.root, self.choice('assign', note='Draft the fictional reply.'))
        correction = self.choice('correct', label='read', note='This can wait.')
        d.review(self.root, correction)
        d.review(self.root, self.choice('delivered', note='Presented in fictional chat.'))
        original = copy.deepcopy(d.read_state(self.root)['items']['mail-demo-a'])
        self.inputs['items'][0]['status'] = 'failed'
        self.inputs['coverage']['status'] = 'partial'
        self.assertEqual(self.prepare()['requests'], [])
        held = d.summary(self.root)['items'][0]
        self.assertEqual(held['status'], 'held'); self.assertIsNone(held['label'])
        self.assertFalse(held['new_review'])
        self.assertEqual(held['follow_up']['status'], 'open')
        with self.assertRaises(d.Hold):
            d.review(self.root, dict(correction, receipt_id='while-held'))
        with self.assertRaises(d.Hold):
            d.teach(self.root, self.approval(), self.refs, self.inputs['items'][0])
        page = d.render(self.root).read_text()
        self.assertNotIn('data-id="mail-demo-a"', page)
        fragment = inline_review.render(self.root, self.root/'held.html', include_seen=True).read_text()
        payload = json.loads(fragment.split('class="dr-data">')[1].split('</script>')[0])
        self.assertNotIn('mail-demo-a', [i['id'] for i in payload['items']])
        self.assertEqual(len(payload['holds']), 1)
        self.inputs['items'][0]['status'] = 'complete'
        self.inputs['coverage']['status'] = 'complete'
        self.assertEqual(self.prepare()['requests'], [])
        restored = d.read_state(self.root)['items']['mail-demo-a']
        self.assertEqual(restored, original)
        self.assertEqual(d.summary(self.root)['items'][0]['label'], 'read')
        self.assertFalse(d.summary(self.root)['items'][0]['new_review'])
        self.assertTrue(d.teach(self.root, self.approval(), self.refs, self.inputs['items'][0]))

    def test_changed_inputs_after_hold_require_fresh_assessment(self):
        for changed in ('content', 'context', 'rubric', 'reference', 'evaluator'):
            with self.subTest(changed=changed), tempfile.TemporaryDirectory() as root:
                inputs, rubric, refs = map(copy.deepcopy, (self.inputs, self.rubric, self.refs))
                batch = d.prepare(root, inputs, rubric, refs, 'fixed')
                d.accept(root, batch, self.response)
                inputs['items'][0]['status'] = 'partial'
                d.prepare(root, inputs, rubric, refs, 'fixed')
                inputs['items'][0]['status'] = 'complete'
                evaluator = 'fixed'
                if changed in ('content', 'context'): inputs['items'][0][changed] += ' Changed evidence.'
                elif changed == 'rubric': rubric['version'] += '-changed'
                elif changed == 'reference': refs['references'][0]['distinction'] += ' Changed rule.'
                else: evaluator = 'changed'
                batch = d.prepare(root, inputs, rubric, refs, evaluator)
                self.assertIn('mail-demo-a', [w['request']['target']['id'] for w in batch['requests']])
                row = d.read_state(root)['items']['mail-demo-a']
                self.assertEqual(row['status'], 'pending'); self.assertIsNone(row['decision'])
                self.assertEqual(len(row['history']), 1)

    def test_unclassified_hold_recovers_to_pending_and_unseen_decision_stays_new(self):
        batch = self.prepare()
        self.inputs['items'][0]['status'] = 'failed'; self.prepare()
        self.inputs['items'][0]['status'] = 'complete'
        recovered = self.prepare()
        self.assertEqual(recovered['requests'], batch['requests'])
        d.accept(self.root, recovered, self.response)
        decision_id = d.read_state(self.root)['items']['mail-demo-a']['decision']['id']
        self.inputs['items'][0]['status'] = 'failed'; self.prepare()
        self.inputs['items'][0]['status'] = 'complete'
        self.assertEqual(self.prepare()['requests'], [])
        self.assertTrue(d.summary(self.root)['items'][0]['new_review'])
        self.assertEqual(d.read_state(self.root)['items']['mail-demo-a']['decision']['id'], decision_id)

    def test_validation_is_atomic_and_rejects_stale_results(self):
        batch=self.prepare();bad=copy.deepcopy(self.response);bad['results'][-1]['label']='made-up'
        before=(self.root/'state.json').read_bytes()
        with self.assertRaises(d.Hold):d.accept(self.root,batch,bad)
        self.assertEqual((self.root/'state.json').read_bytes(),before)
        with self.assertRaises(d.Hold):d.accept(self.root,batch,{'mode':'coding_agent','results':[]})
        self.inputs['items'][0]['context']+='Changed obligation.'; self.prepare()
        with self.assertRaises(d.Hold):d.accept(self.root,batch,self.response)

    def test_render_escapes_source_and_saves_nothing(self):
        self.inputs['items'][0]['content']='<script>alert("bad")</script><img src="https://example.com/a">'
        self.accepted();before=(self.root/'state.json').read_bytes();page=d.render(self.root).read_text()
        self.assertNotIn('<script>alert',page);self.assertNotIn('&lt;script&gt;',page)
        self.assertNotIn('<img src=',page)
        self.assertIn('not saved',page);self.assertIn('crypto.randomUUID()',page)
        self.assertEqual((self.root/'state.json').read_bytes(),before)

    def test_render_shows_held_items_open_tasks_and_approved_teaching(self):
        self.corrected(); d.teach(self.root, self.approval(), self.refs, self.inputs['items'][0])
        self.inputs['items'][1]['status'] = 'failed'; self.prepare()
        page = d.render(self.root).read_text()
        self.assertIn('Not classified yet', page); self.assertIn('Source content is incomplete', page)
        self.assertIn('Approved as a teaching example', page)
        self.assertNotIn('value="complete"', page)
        d.review(self.root, self.choice('assign', receipt_id='assign', note='Ask the host to confirm.'))
        d.review(self.root, self.choice('seen', receipt_id='seen'))
        page = d.render(self.root).read_text()
        self.assertIn('Follow-up open', page); self.assertEqual(page.count('value="complete"'), 1)

    def test_delivery_is_audit_only_and_untouched_decisions_resurface(self):
        self.accepted();d.render(self.root)
        original = d.read_state(self.root)['items']['mail-demo-a']['decision']
        self.assertTrue(d.summary(self.root)['items'][0]['new_review'])
        for run in range(2):
            d.review(self.root, self.choice('delivered', receipt_id=f'delivery-{run}', note='Confirmed in reader chat.'))
            self.assertEqual(self.prepare()['requests'], [])
            self.assertTrue(d.summary(self.root)['items'][0]['new_review'])
            current = d.read_state(self.root)['items']['mail-demo-a']['decision']
            self.assertTrue(current['delivered']); self.assertFalse(current['acknowledged'])
            self.assertEqual(current['id'], original['id'])
            self.assertEqual(current['label'], original['label'])
            page = d.render(self.root).read_text()
            self.assertIn('4 awaiting review', page)
            self.assertIn('Shown in chat', page)
        # Retrieval gaps suspend presentation, but do not turn delivery into acknowledgment.
        self.inputs['items'][0]['status'] = 'failed'; self.prepare()
        self.assertFalse(d.summary(self.root)['items'][0]['new_review'])
        self.inputs['items'][0]['status'] = 'complete'; self.prepare()
        self.assertTrue(d.summary(self.root)['items'][0]['new_review'])
        d.review(self.root, self.choice('seen'))
        self.assertEqual(self.prepare()['requests'], [])
        self.assertFalse(d.summary(self.root)['items'][0]['new_review'])
        self.assertIn('3 awaiting review', d.render(self.root).read_text())

    def test_unapproved_reference_change_does_not_invalidate(self):
        self.accepted();ref=copy.deepcopy(self.refs['references'][0]);ref.update(id='proposal',status='proposed')
        self.refs['references'].append(ref)
        self.assertEqual(self.prepare()['requests'],[])

    def test_duplicate_source_identity_rejected(self):
        self.inputs['items'].append(self.inputs['items'][0])
        with self.assertRaises(d.Hold):self.prepare()

    def test_overlapping_writer_cannot_alter_saved_state(self):
        self.accepted()
        before = (self.root/'state.json').read_bytes()
        with d.writer_lock(self.root):
            with self.assertRaises(d.Hold):
                self.prepare()
            self.assertEqual((self.root/'state.json').read_bytes(), before)
        self.assertFalse((self.root/'.writer.lock').exists())

    def approval(self, **changes):
        return {'receipt_id': 'correct', 'use_as_example': True,
                'approved_by': 'Fictional reviewer',
                'approval_evidence': 'Explicit fictional test instruction to use this as an example.',
                'distinction': 'A delegated equipment check is waiting on another person, not an action for the reader.',
                'contrast_ids': ['email-deadline'], **changes}

    def corrected(self):
        self.accepted()
        d.review(self.root, self.choice('correct', label='read',
                 note='This is waiting on the assigned host.'))

    def test_correction_does_not_teach_without_approval(self):
        self.corrected()
        self.assertFalse((self.root/'references.json').exists())
        self.assertEqual(self.prepare()['requests'], [])
        with self.assertRaises(d.Hold):
            d.teach(self.root, self.approval(use_as_example=False), self.refs)
        self.assertFalse((self.root/'references.json').exists())

    def test_approved_correction_reaches_next_packet_with_full_content(self):
        self.corrected(); before = d.read_state(self.root)
        ref_id = d.teach(self.root, self.approval(), self.refs, self.inputs['items'][0])
        library = d.load_json(self.root/'references.json')
        batch = d.prepare(self.root, self.inputs, self.rubric, library, 'test-evaluator')
        # Target never receives its own corrected answer; other targets receive the example.
        self.assertEqual(len(batch['requests']), self.item_count - 1)
        request = batch['requests'][0]['request']
        ref = next(r for r in request['references'] if r['id'] == ref_id)
        self.assertEqual(ref['content'], self.inputs['items'][0]['content'])
        self.assertEqual(ref['context'], self.inputs['items'][0]['context'])
        self.assertEqual(ref['label'], 'read')
        self.assertEqual(ref['distinction'], self.approval()['distinction'])
        self.assertEqual(ref['contrast_ids'], ['email-deadline'])
        self.assertNotIn('approval', ref)
        self.assertEqual(request['rubric'], self.rubric)
        after = d.read_state(self.root)
        self.assertEqual(before['receipts'], after['receipts'])
        self.assertEqual(before['items']['mail-demo-a'], after['items']['mail-demo-a'])
        self.assertEqual(len(list((self.root/'reference-history').glob('*.json'))), 1)

    def test_cli_uses_updated_local_library_by_default(self):
        self.corrected(); ref_id = d.teach(self.root, self.approval(), self.refs, self.inputs['items'][0])
        (self.root/'rubric.json').write_bytes(d.encoded(self.rubric))
        result = subprocess.run([sys.executable, 'workflow/decision.py', 'prepare', '--root', str(self.root),
                                 '--evaluator', 'test-evaluator', '--stdin'], input=json.dumps(self.inputs), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        batch = d.load_json(self.root/'packet.json')
        self.assertEqual(len(batch['requests']), self.item_count - 1)
        self.assertTrue(all(ref_id in [r['id'] for r in w['request']['references']]
                            for w in batch['requests']))

    def test_teaching_retry_is_idempotent_and_conflicts_do_not_write(self):
        self.corrected(); ref = d.teach(self.root, self.approval(), self.refs, self.inputs['items'][0])
        saved = (self.root/'references.json').read_bytes()
        self.assertEqual(d.teach(self.root, self.approval(), self.refs, self.inputs['items'][0]), ref)
        with self.assertRaises(d.Hold):
            d.teach(self.root, self.approval(distinction='Different teaching claim.'), self.refs, self.inputs['items'][0])
        self.assertEqual((self.root/'references.json').read_bytes(), saved)

    def test_teaching_requires_current_correction_and_valid_contrast(self):
        self.corrected()
        for fields in ({'contrast_ids': ['missing']}, {'contrast_ids': ['email-deadline','email-deadline']},
                       {'approved_by': ''}, {'approval_evidence': ''}):
            with self.assertRaises(d.Hold):
                d.teach(self.root, self.approval(**fields), self.refs, self.inputs['items'][0])
        self.inputs['items'][0]['content'] += ' A later reply settles it.'
        self.prepare()
        with self.assertRaises(d.Hold):
            d.teach(self.root, self.approval(), self.refs, self.inputs['items'][0])
        self.assertFalse((self.root/'references.json').exists())

    def test_teaching_retires_old_situation_and_rejects_non_email_targets(self):
        self.corrected()
        old = copy.deepcopy(self.refs['references'][0])
        old.update(id='older-situation', source_id='mail-demo-a')
        self.refs['references'].append(old)
        ref = d.teach(self.root, self.approval(), self.refs, self.inputs['items'][0])
        library = d.load_json(self.root/'references.json')
        self.assertEqual(next(r for r in library['references'] if r['id']=='older-situation')['status'], 'retired')
        other = copy.deepcopy(self.inputs['items'][0]); other['kind'] = 'unsupported'
        rubric = copy.deepcopy(self.rubric); rubric['kind'] = 'unsupported'
        with self.assertRaises(d.Hold):
            d.packet(other, rubric, library, 'test')

if __name__=='__main__':unittest.main()

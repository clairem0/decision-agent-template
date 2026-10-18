import copy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import decision as d
import jev_run as j
import jev_workflow as w


def answer(payload, label='act', evidence='sufficient'):
    choices = {'email_category': label, 'evidence_status': evidence}
    return {'model': j.MODEL, 'usage': {'input_tokens': 50, 'output_tokens': 2, 'cost': .0000021},
            'answers': {name: {'type': 'choice', 'choice': choices[name], 'confidence': 1,
                         'probabilities': {key: int(key == choices[name]) for key in question['criteria']}}
                        for name, question in payload['questions'].items()}}


class JevWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.inputs = d.load_json('workflow/demo/inputs.json')
        self.inputs['items'] = self.inputs['items'][:2]
        self.inputs['items'][0]['content'] += ' PRIVATE_SOURCE_MARKER'
        self.rubric = d.load_json('rubric/rubric.json')
        self.refs = d.load_json('rubric/examples.json')
        self.batch = self.prepare()

    def prepare(self):
        return d.prepare(self.root, self.inputs, self.rubric, self.refs, w.EVALUATOR)

    def test_jev_results_reach_review_and_correction_survives_without_another_call(self):
        with patch.dict(os.environ, {'JEV_API_KEY': 'test-key'}), patch.object(j, 'post', side_effect=lambda p, k: answer(p)) as post:
            result = w.run(self.root, self.batch, live=True, max_requests=2)
            self.assertEqual(result['accepted'], 2)
            row = d.read_state(self.root)['items']['mail-demo-a']
            self.assertEqual(row['decision']['mode'], 'jev')
            self.assertEqual(row['decision']['provider_result']['model'], j.MODEL)
            self.assertIn('Category definition', row['decision']['reason'])
            d.review(self.root, {'receipt_id': 'correction-1', 'id': 'mail-demo-a',
                'decision_id': row['decision']['id'], 'action': 'correct', 'label': 'read', 'note': 'Already handled.'})
            self.assertEqual(w.run(self.root, self.prepare(), live=True, max_requests=2)['accepted'], 0)
            self.assertEqual(d.summary(self.root)['items'][0]['label'], 'read')
            self.assertEqual(post.call_count, 2)
        for path in self.root.rglob('*.json'):
            self.assertNotIn('PRIVATE_SOURCE_MARKER', path.read_text())
            self.assertNotIn('test-key', path.read_text())

    def test_preview_and_request_bound_do_not_send(self):
        with patch.object(j, 'post') as post:
            self.assertEqual(w.run(self.root, self.batch)['pending'], 2)
            with self.assertRaises(d.Hold): w.run(self.root, self.batch, live=True, max_requests=1)
            post.assert_not_called()

    def test_delivered_but_untouched_results_resurface_without_provider_calls(self):
        import inline_review
        with patch.dict(os.environ, {'JEV_API_KEY': 'test-key'}), patch.object(j, 'post', side_effect=lambda p, k: answer(p)) as post:
            w.run(self.root, self.batch, live=True, max_requests=2)
            state = d.read_state(self.root)
            for key, row in state['items'].items():
                d.review(self.root, {'receipt_id': 'shown-'+key, 'id': key,
                    'decision_id': row['decision']['id'], 'action': 'delivered', 'note': 'Shown in chat.'})
            self.assertEqual(w.run(self.root, self.prepare(), live=True, max_requests=2)['accepted'], 0)
            self.assertEqual(post.call_count, 2)
        self.assertTrue(all(item['new_review'] for item in d.summary(self.root)['items']))
        fragment = inline_review.render(self.root, self.root/'next-review.html').read_text()
        payload = json.loads(fragment.split('class="dr-data">')[1].split('</script>')[0])
        self.assertEqual({item['id']: item['decision_id'] for item in payload['items']},
                         {key: row['decision']['id'] for key, row in state['items'].items()})

    def test_uncertain_skip_is_visible_reviewable_and_reused_without_another_call(self):
        with patch.dict(os.environ, {'JEV_API_KEY': 'test-key'}), patch.object(j, 'post', side_effect=lambda p, k: answer(p, 'skip', 'needs_review')):
            result = w.run(self.root, self.batch, live=True, max_requests=2)
        self.assertEqual((result['accepted'], result['pending'], result['flagged']), (2, 0, 2))
        state = d.read_state(self.root)
        self.assertTrue(all(row['decision']['provider_result']['requires_review'] for row in state['items'].values()))
        self.assertTrue(all(item['new_review'] and item['label'] == 'skip' and item['uncertainty'] for item in d.summary(self.root)['items']))
        self.assertIn('Needs context:', d.render(self.root).read_text())
        with patch.object(j, 'post') as post:
            self.assertEqual(w.run(self.root, self.prepare(), live=True, max_requests=0)['accepted'], 0)
        post.assert_not_called()

    def test_one_failed_call_does_not_block_other_items_or_resend_on_rerun(self):
        self.inputs['items'].append(d.load_json('workflow/demo/inputs.json')['items'][2])
        batch = self.prepare()
        def provider(payload, key):
            if payload['state']['target']['id'] == 'mail-demo-b':
                raise TimeoutError('PRIVATE_ERROR_MARKER')
            return answer(payload)
        with patch.dict(os.environ, {'JEV_API_KEY':'test-key'}), patch.object(j, 'post', side_effect=provider) as post:
            result = w.run(self.root, batch, live=True, max_requests=3)
        self.assertEqual(post.call_count, 3)
        self.assertEqual((result['accepted'], result['pending']), (2, 1))
        state = d.read_state(self.root)
        self.assertEqual(state['items']['mail-demo-a']['status'], 'current')
        self.assertEqual(state['items']['mail-demo-b']['status'], 'pending')
        self.assertIsNone(state['items']['mail-demo-b']['decision'])
        self.assertEqual(state['items']['mail-demo-c']['status'], 'current')
        self.assertIn('saved attempt', d.render(self.root).read_text())
        with patch.object(j, 'post') as post:
            retry = w.run(self.root, self.prepare(), live=True, max_requests=1)
        self.assertEqual((retry['accepted'], retry['pending']), (0, 1))
        post.assert_not_called()
        for path in self.root.rglob('*.json'):
            self.assertNotIn('PRIVATE_ERROR_MARKER', path.read_text())
            self.assertNotIn('PRIVATE_SOURCE_MARKER', path.read_text())

    def test_old_successful_but_flagged_skip_attempt_can_resume_without_resending(self):
        with patch.dict(os.environ, {'JEV_API_KEY':'test-key'}), patch.object(j, 'post', side_effect=lambda p,k: answer(p, 'skip', 'needs_review')):
            j.run(self.batch, 'mail-demo-a', self.root/'attempts', live=True, max_requests=1)
        with patch.dict(os.environ, {'JEV_API_KEY':'test-key'}), patch.object(j, 'post', side_effect=lambda p,k: answer(p)) as post:
            result = w.run(self.root, self.batch, live=True, max_requests=2)
        self.assertEqual(result['accepted'], 2)
        self.assertEqual(result['reused_attempts'], 1)
        self.assertEqual(result['flagged'], 1)
        self.assertEqual(post.call_count, 1)

    def test_due_reminder_reuses_jev_result_without_another_provider_call(self):
        with patch.dict(os.environ, {'JEV_API_KEY': 'test-key'}), patch.object(j, 'post', side_effect=lambda p, k: answer(p)) as post:
            w.run(self.root, self.batch, live=True, max_requests=2)
            row = d.read_state(self.root)['items']['mail-demo-a']
            d.review(self.root, {'receipt_id': 'remind-a', 'id': 'mail-demo-a', 'decision_id': row['decision']['id'],
                                'action': 'remind', 'reminder': {'when': 'at', 'at': '2030-04-09T09:00:00Z'}})
            batch = self.prepare()
            self.assertEqual(batch['requests'], [])
            self.assertEqual(w.run(self.root, batch, live=True, max_requests=2)['accepted'], 0)
            self.assertTrue(d.summary(self.root, datetime(2030, 4, 9, 9, tzinfo=timezone.utc))['items'][0]['new_review'])
            self.assertEqual(post.call_count, 2)
            self.assertEqual(d.read_state(self.root)['items']['mail-demo-a']['decision']['id'], row['decision']['id'])

    def test_saved_success_can_resume_after_interruption_without_resending(self):
        def interrupted(payload, key):
            if payload['state']['target']['id'] == 'mail-demo-b': raise KeyboardInterrupt()
            return answer(payload)
        with patch.dict(os.environ, {'JEV_API_KEY': 'test-key'}), patch.object(j, 'post', side_effect=interrupted):
            with self.assertRaises(KeyboardInterrupt): w.run(self.root, self.batch, live=True, max_requests=2)
        with patch.object(j, 'post') as post:
            result = w.run(self.root, self.prepare(), live=True, max_requests=2)
            post.assert_not_called()
        self.assertEqual(result['pending'], 1)
        state = d.read_state(self.root)
        self.assertIsNotNone(state['items']['mail-demo-a']['decision'])
        self.assertIsNone(state['items']['mail-demo-b']['decision'])

    def test_wrong_state_or_evaluator_stops_before_spending(self):
        with patch.object(j, 'post') as post:
            bad = copy.deepcopy(self.batch)
            bad['requests'][0]['request']['evaluator'] = 'coding-agent'
            with self.assertRaises(d.Hold): w.run(self.root, bad, live=True, max_requests=2)
            with self.assertRaises(d.Hold): w.run(self.root/'wrong-root', self.batch, live=True, max_requests=2)
            post.assert_not_called()

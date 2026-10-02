import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import decision as d
import inline_review


class StoragePolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.inputs = d.load_json('examples/email/inputs.json')
        self.rubric = d.load_json('examples/email/rubric.json')
        self.refs = d.load_json('examples/references.json')
        self.response = d.load_json('examples/email/demo-results.json')
        self.inputs['items'][0].update(content='UNRETAINED_BODY_7938', context='UNRETAINED_CONTEXT_5291',
                                       unrelated='UNRETAINED_EXTRA_5281', original_url='https://mail.example.test/thread/one')

    def prepare(self):
        return d.prepare(self.root, self.inputs, self.rubric, self.refs, 'retention-test')

    def correct(self):
        batch = self.prepare(); d.accept(self.root, batch, self.response)
        row = d.read_state(self.root)['items']['mail-demo-a']
        receipt = {'receipt_id':'teaching-test', 'id':'mail-demo-a', 'decision_id':row['decision']['id'],
                   'action':'correct', 'label':'track', 'note':'Waiting on the assigned owner.'}
        d.review(self.root, receipt)
        return {'receipt_id':receipt['receipt_id'], 'use_as_example':True, 'approved_by':'fictional reviewer',
                'approval_evidence':'Synthetic explicit teaching approval.', 'distinction':'Waiting is not an action.'}

    def test_complete_input_reaches_classifier_but_not_retained_artifacts(self):
        batch = self.prepare()
        request = batch['requests'][0]['request']
        self.assertEqual(request['target']['content'], 'UNRETAINED_BODY_7938')
        self.assertEqual(request['target']['context'], 'UNRETAINED_CONTEXT_5291')
        self.assertEqual(request['references'][0]['content'], self.refs['references'][0]['content'])
        self.assertNotIn('original_url', request['target'])
        # CLI acceptance needs only the metadata manifest, not a cached body.
        d.accept(self.root, d.load_json(self.root/'packet.json'), self.response)
        d.render(self.root); inline_review.render(self.root, self.root/'native.html')
        for path in self.root.rglob('*'):
            if path.is_file():
                self.assertNotIn(b'UNRETAINED_', path.read_bytes(), str(path))
        self.assertFalse((self.root/'inputs.json').exists())
        self.assertIn('https://mail.example.test/thread/one', (self.root/'review/index.html').read_text())
        payload = json.loads((self.root/'native.html').read_text().split('class="dr-data">')[1].split('</script>')[0])
        self.assertEqual(payload['items'][0]['original_url'], 'https://mail.example.test/thread/one')

    def test_link_only_refresh_preserves_review_and_no_reassessment(self):
        self.correct()
        self.inputs['items'][0]['original_url'] = 'https://mail.example.test/thread/two'
        self.assertEqual(self.prepare()['requests'], [])
        self.assertEqual(d.summary(self.root)['items'][0]['label'], 'track')
        self.assertFalse(d.summary(self.root)['items'][0]['new_review'])
        self.assertIn('/thread/two', d.render(self.root).read_text())

    def test_unsafe_links_are_absent_in_both_reviews_and_held_links_remain(self):
        for link in ('javascript:alert(1)', 'data:text/html,test', '//mail.example.test/x',
                     'https://user:secret@mail.example.test/x', 'https://mail.example.test/\nx',
                     'https://mail.example.test\\x', 'https://[bad'):
            self.assertIsNone(d.source_link(link))
        self.inputs['items'][0]['original_url'] = 'javascript:alert(1)'
        self.inputs['items'][1]['status'] = 'failed'
        batch = self.prepare()
        response = copy.deepcopy(self.response); response['results'] = [r for r in response['results'] if r['id'] != 'mail-demo-b']
        d.accept(self.root, batch, response)
        self.assertNotIn('javascript:', d.render(self.root).read_text())
        text = inline_review.render(self.root, self.root/'native.html').read_text()
        data = json.loads(text.split('class="dr-data">')[1].split('</script>')[0])
        self.assertIsNone(data['items'][0]['original_url'])
        self.assertEqual(data['holds'][0]['original_url'], self.inputs['items'][1]['original_url'])

    def test_teaching_requires_matching_source_and_only_then_retains_it(self):
        approval = self.correct()
        before = (self.root/'state.json').read_bytes()
        with self.assertRaises(d.Hold): d.teach(self.root, approval, self.refs)
        changed = dict(self.inputs['items'][0], content='Changed after the decision.')
        with self.assertRaises(d.Hold): d.teach(self.root, approval, self.refs, changed)
        self.assertFalse((self.root/'references.json').exists())
        ref_id = d.teach(self.root, approval, self.refs, self.inputs['items'][0])
        library = d.load_json(self.root/'references.json')
        self.assertEqual(next(r for r in library['references'] if r['id']==ref_id)['content'], 'UNRETAINED_BODY_7938')
        self.assertEqual((self.root/'state.json').read_bytes(), before)
        batch = d.prepare(self.root, self.inputs, self.rubric, library, 'retention-test')
        self.assertTrue(any(r['id']==ref_id and r['content']=='UNRETAINED_BODY_7938'
                            for r in batch['requests'][0]['request']['references']))

    def test_metadata_manifest_tampering_is_rejected_without_partial_write(self):
        self.prepare(); batch = d.load_json(self.root/'packet.json')
        batch['requests'][-1]['request']['target']['source_hash'] = 'forged'
        before = (self.root/'state.json').read_bytes()
        with self.assertRaises(d.Hold): d.accept(self.root, batch, self.response)
        self.assertEqual((self.root/'state.json').read_bytes(), before)

    def test_receipts_reject_full_source_extra_fields(self):
        approval = self.correct()
        receipt = d.read_state(self.root)['receipts'][approval['receipt_id']]
        with self.assertRaises(d.Hold): d.review(self.root, dict(receipt, receipt_id='other', content='UNRETAINED_BODY_7938'))

    def test_explicit_legacy_migration_preserves_choices_and_redacts_managed_files(self):
        batch = self.prepare(); d.accept(self.root, batch, self.response)
        state = d.read_state(self.root); row = state['items']['mail-demo-a']
        d.review(self.root, {'receipt_id':'seen', 'id':'mail-demo-a', 'decision_id':row['decision']['id'], 'action':'seen'})
        state = d.read_state(self.root); expected = state['receipts']; state.pop('storage_version')
        for wrapper in batch['requests']:
            row = state['items'][wrapper['request']['target']['id']]
            row['source'] = copy.deepcopy(next(i for i in self.inputs['items'] if i['id']==row['source']['id']))
            row['request'] = wrapper['request']; row['history'][0]['request'] = wrapper['request']
        (self.root/'state.json').write_bytes(d.encoded(state))
        (self.root/'packet.json').write_bytes(d.encoded(batch))
        (self.root/'inputs.json').write_bytes(d.encoded(self.inputs))
        with self.assertRaises(d.Hold): d.read_state(self.root)
        d.migrate(self.root)
        self.assertEqual(d.read_state(self.root)['receipts'], expected)
        self.assertEqual(self.prepare()['requests'], [])
        self.assertFalse(d.summary(self.root)['items'][0]['new_review'])
        for path in self.root.rglob('*'):
            if path.is_file(): self.assertNotIn(b'UNRETAINED_', path.read_bytes())

    def test_teach_cli_reads_single_source_on_stdin(self):
        approval = self.correct()
        (self.root/'approval.json').write_bytes(d.encoded(approval))
        result = subprocess.run([sys.executable, 'decision.py', 'teach', '--root', str(self.root),
                                 '--approval', str(self.root/'approval.json'), '--references', 'examples/references.json', '--stdin'],
                                input=json.dumps(self.inputs['items'][0]), text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.root/'references.json').exists())
        self.assertFalse((self.root/'inputs.json').exists())

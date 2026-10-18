import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import decision as d
import jev_run as j
import try_jev as sample
from test_jev_workflow import answer


class SyntheticInboxTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)/'synthetic'
        self.inputs, self.rubric, self.examples = sample.load_samples()
        # Expectations are available only to this fake provider, never to the product requests.
        self.expected = d.load_json(sample.FIXTURES/'expected.json')['expectations']

    def provider(self, payload, key):
        target = payload['state']['target']
        want = self.expected[target['id']]
        self.assertEqual(key, 'test-key')
        self.assertEqual(payload['state']['rubric'], self.rubric)
        self.assertFalse({'expected', 'label', 'needs_review', 'reason'} & set(target))
        self.assertNotIn('expectations', payload['state'])
        self.assertEqual(target['content'], next(i['content'] for i in self.inputs['items'] if i['id'] == target['id']))
        return answer(payload, want['label'], 'needs_review' if want['needs_review'] else 'sufficient')

    def live(self):
        return sample.run(self.root, live=True, max_requests=50)

    def test_one_self_contained_fifty_thread_inbox_with_variety_and_separate_teaching(self):
        items = self.inputs['items']
        self.assertEqual(len(items), 50)
        self.assertEqual(len({i['content'] for i in items}), 50)
        self.assertEqual(len({i['title'] for i in items}), 50)
        self.assertEqual({i['id'] for i in items}, set(self.expected))
        self.assertEqual(set(self.rubric['labels']), {'act', 'read', 'skip'})
        self.assertTrue(all(v['label'] in d.LABELS for v in self.expected.values()))
        self.assertEqual(sum(v['needs_review'] for v in self.expected.values()), 2)
        self.assertGreater(len({i['sender'] for i in items}), 20)
        self.assertTrue(any('Message 4' in i['content'] for i in items))
        self.assertTrue(any('unsent' in i['content'] for i in items))
        self.assertFalse({r['source_id'] for r in self.examples['references']} & set(self.expected))
        # No real source URLs, account addresses, local paths or user-linked brand names.
        for obj in (self.inputs, self.rubric, self.examples):
            text = json.dumps(obj)
            self.assertNotIn('original_url', text)
            self.assertNotIn('@', text)
            self.assertNotIn('/Users/', text)
            self.assertNotIn('Technically Curious', text)
            self.assertNotIn('Recalc', text)

    def test_preview_needs_no_key_does_not_read_answers_or_private_root_and_writes_nothing(self):
        self.root.mkdir(); private = self.root/'state.json'; private.write_text('DO NOT READ')
        actual_load = d.load_json
        def guarded(path):
            self.assertNotEqual(Path(path), sample.FIXTURES/'expected.json')
            self.assertNotEqual(Path(path), private)
            return actual_load(path)
        with patch.object(d, 'load_json', side_effect=guarded), patch.object(sample, 'load_key') as key, patch.object(j, 'post') as post:
            result = sample.run(self.root, env_file='unrelated-key-file')
        self.assertEqual(result['threads'], 50); self.assertEqual(result['new_api_calls'], 0)
        self.assertEqual(result['mode'], 'preview'); key.assert_not_called(); post.assert_not_called()
        self.assertEqual(list(self.root.iterdir()), [private])
        self.assertEqual(private.read_text(), 'DO NOT READ')

    def test_live_freezes_predictions_before_comparison_and_distinguishes_cached_speed(self):
        actual_load = d.load_json
        def guarded(path):
            if Path(path) == sample.FIXTURES/'expected.json':
                frozen = list((self.root/'runs').glob('*/predictions.json'))
                self.assertTrue(frozen)
                self.assertEqual(len(actual_load(frozen[-1])), 50)
            return actual_load(path)
        with patch.dict(os.environ, {'JEV_API_KEY':'test-key'}), patch.object(j, 'post', side_effect=self.provider) as post, patch.object(d, 'load_json', side_effect=guarded):
            first = self.live()
            self.assertEqual(first['new_api_calls'], 50)
            self.assertEqual(first['reused_decisions'], 0)
            self.assertEqual(first['reused_attempts'], 0)
            self.assertEqual(first['comparison']['category_matches'], 50)
            self.assertEqual(first['comparison']['evidence_matches'], 50)
            self.assertEqual(first['new_call_tokens'], {'input_tokens':2500,'output_tokens':100})
            self.assertEqual(first['api_round_trip_seconds'], sum(m['seconds'] for m in first['requests']))
            self.assertGreaterEqual(first['timings_seconds']['classify_and_save'], first['api_round_trip_seconds'])
            self.assertEqual(len(d.read_state(self.root)['items']), 50)
            self.assertTrue(all(r['new_review'] for r in d.summary(self.root)['items']))
            row = d.read_state(self.root)['items']['synthetic-001']
            d.review(self.root, {'receipt_id':'user-correction','id':'synthetic-001','decision_id':row['decision']['id'],
                                'action':'correct','label':'skip','note':'A fictional review correction.'})
            second = self.live()
            self.assertEqual(second['new_api_calls'], 0)
            self.assertEqual(second['reused_decisions'], 50)
            self.assertIsNone(second['median_api_round_trip_seconds'])
            self.assertIsNone(second['api_round_trip_seconds'])
            self.assertEqual(second['new_call_tokens'], {'input_tokens':0,'output_tokens':0})
            self.assertEqual(second['comparison']['category_matches'], 50)  # Original predictions, not corrections.
            self.assertEqual(post.call_count, 50)
            self.assertNotEqual(first['report_file'], second['report_file'])
        self.assertTrue(Path(first['inline_review_file']).exists())
        for path in self.root.rglob('*.json'):
            self.assertNotIn('test-key', path.read_text())
            self.assertNotIn(self.inputs['items'][0]['content'], path.read_text())

    def test_existing_personal_root_and_modified_config_fail_before_api_or_key_read(self):
        self.root.mkdir(); marker = self.root/'rubric.json'; marker.write_text('PRIVATE_MARKER')
        with patch.object(j, 'post') as post, patch.object(sample, 'load_key') as key:
            with self.assertRaises(d.Hold): sample.run(self.root, live=True, max_requests=50, env_file='unrelated')
        self.assertEqual(list(self.root.iterdir()), [marker]); post.assert_not_called(); key.assert_not_called()
        marker.unlink()
        with patch.dict(os.environ, {'JEV_API_KEY':'test-key'}), patch.object(j, 'post', side_effect=self.provider):
            self.live()
        marker.write_text('PRIVATE_MARKER')
        with patch.object(j, 'post') as post:
            with self.assertRaises(d.Hold): self.live()
        post.assert_not_called(); self.assertEqual(marker.read_text(),'PRIVATE_MARKER')

    def test_saved_successful_attempts_resume_without_claiming_fresh_speed(self):
        with patch.dict(os.environ, {'JEV_API_KEY':'test-key'}), patch.object(j, 'post', side_effect=self.provider) as post:
            with patch.object(d, 'accept', side_effect=d.Hold('Interrupted before accepting results.')):
                with self.assertRaises(d.Hold): self.live()
            self.assertEqual(post.call_count, 50)
        with patch.object(j, 'post') as post:
            resumed = self.live()
        post.assert_not_called()
        self.assertEqual(resumed['status'], 'complete')
        self.assertEqual(resumed['new_api_calls'], 0)
        self.assertEqual(resumed['reused_decisions'], 0)
        self.assertEqual(resumed['reused_attempts'], 50)
        self.assertIsNone(resumed['api_round_trip_seconds'])
        self.assertEqual(resumed['new_call_tokens'], {'input_tokens':0,'output_tokens':0})
        self.assertEqual(resumed['comparison']['total'], 50)

    def test_request_bound_and_changed_fixtures_fail_without_sending(self):
        with patch.object(j, 'post') as post:
            with self.assertRaises(d.Hold): sample.run(self.root, live=True, max_requests=49)
        self.assertFalse(self.root.exists()); post.assert_not_called()
        with patch.dict(os.environ, {'JEV_API_KEY':'test-key'}), patch.object(j, 'post', side_effect=self.provider):
            self.live()
        changed = copy.deepcopy(self.inputs); changed['items'][0]['content'] += ' Changed text.'
        before = (self.root/'state.json').read_bytes()
        with patch.object(sample, 'load_samples', return_value=(changed,self.rubric,self.examples)), patch.object(j, 'post') as post:
            with self.assertRaises(d.Hold): self.live()
        post.assert_not_called(); self.assertEqual((self.root/'state.json').read_bytes(),before)

    def test_failure_saves_timing_and_successful_attempts_without_answers_or_automatic_retry(self):
        def interrupted(payload, key):
            if payload['state']['target']['id'] == 'synthetic-002': raise TimeoutError('PRIVATE_ERROR_MARKER')
            return self.provider(payload,key)
        with patch.dict(os.environ, {'JEV_API_KEY':'test-key'}), patch.object(j, 'post', side_effect=interrupted) as post, patch.object(sample, 'compare') as compare:
            with self.assertRaises(d.Hold): self.live()
            self.assertEqual(post.call_count,50); compare.assert_not_called()
        report = d.load_json(next((self.root/'runs').glob('*/report.json')))
        self.assertEqual(report['status'],'held'); self.assertEqual(report['new_api_calls'],50)
        self.assertEqual(report['successful_new_calls'],49)
        self.assertEqual(report['pending'],1)
        self.assertIsNone(report['comparison']); self.assertGreaterEqual(report['api_round_trip_seconds'],0)
        self.assertFalse(list((self.root/'runs').glob('*/predictions.json')))
        with patch.object(j, 'post') as post:
            with self.assertRaises(d.Hold): self.live()
        post.assert_not_called()
        self.assertEqual(sum(r['decision'] is not None for r in d.read_state(self.root)['items'].values()),49)
        for path in self.root.rglob('*.json'): self.assertNotIn('PRIVATE_ERROR_MARKER',path.read_text())

    def test_cli_defaults_to_safe_preview(self):
        result = subprocess.run([sys.executable,'workflow/try_jev.py','--root',str(self.root),'--env-file','does-not-exist'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('50 fictional email threads',result.stdout)
        self.assertIn('API calls: 0',result.stdout)
        self.assertFalse(self.root.exists())


if __name__ == '__main__': unittest.main()

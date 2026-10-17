import copy
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

    def test_uncertain_skip_is_held_not_silently_hidden_or_relabelled(self):
        with patch.dict(os.environ, {'JEV_API_KEY': 'test-key'}), patch.object(j, 'post', side_effect=lambda p, k: answer(p, 'skip', 'needs_review')):
            with self.assertRaises(d.Hold): w.run(self.root, self.batch, live=True, max_requests=2)
        self.assertTrue(all(row['decision'] is None for row in d.read_state(self.root)['items'].values()))
        self.assertTrue(list((self.root/'attempts').glob('*.json')))

    def test_saved_success_can_resume_after_interruption_without_resending(self):
        def interrupted(payload, key):
            if payload['state']['target']['id'] == 'mail-demo-b': raise KeyboardInterrupt()
            return answer(payload)
        with patch.dict(os.environ, {'JEV_API_KEY': 'test-key'}), patch.object(j, 'post', side_effect=interrupted):
            with self.assertRaises(KeyboardInterrupt): w.run(self.root, self.batch, live=True, max_requests=2)
        with patch.object(j, 'post') as post:
            with self.assertRaises(d.Hold): w.run(self.root, self.batch, live=True, max_requests=2)
            post.assert_not_called()
        self.assertTrue(all(row['decision'] is None for row in d.read_state(self.root)['items'].values()))

    def test_wrong_state_or_evaluator_stops_before_spending(self):
        with patch.object(j, 'post') as post:
            bad = copy.deepcopy(self.batch)
            bad['requests'][0]['request']['evaluator'] = 'coding-agent'
            with self.assertRaises(d.Hold): w.run(self.root, bad, live=True, max_requests=2)
            with self.assertRaises(d.Hold): w.run(self.root/'wrong-root', self.batch, live=True, max_requests=2)
            post.assert_not_called()

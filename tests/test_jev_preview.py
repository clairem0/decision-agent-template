import copy
import json
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest

import decision as d
import jev_preview as j


class JevPreviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        inputs = d.load_json('examples/email/inputs.json')
        inputs['items'][0].update(expected='PRIVATE_ANSWER', feedback='PRIVATE_REVIEW')
        self.batch = d.prepare(self.root, inputs, d.load_json('rubric.example.json'),
                               d.load_json('examples/references.json'), 'preview-test')

    def test_exact_target_rubric_and_reference_content_reach_jev_state(self):
        payload = j.build_payload(self.batch, 'mail-demo-a')
        request = self.batch['requests'][0]['request']
        for key in ('target','rubric','references'):
            self.assertEqual(payload['state'][key], request[key])
        self.assertEqual(payload['questions']['email_category']['criteria'], request['rubric']['labels'])
        encoded = d.encoded(payload)
        self.assertNotIn(b'PRIVATE_ANSWER', encoded); self.assertNotIn(b'PRIVATE_REVIEW', encoded)
        self.assertIn(b'Please approve the launch copy by April 9', encoded)
        self.assertNotIn('evaluator', payload['state'])

    def test_preview_streams_without_writing_or_changing_decisions(self):
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        result = subprocess.run([sys.executable, 'jev_preview.py', '--id', 'mail-demo-a'],
                                input=json.dumps(self.batch), text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), j.build_payload(self.batch, 'mail-demo-a'))
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir()})

    def test_missing_duplicate_or_altered_requests_are_not_exported(self):
        with self.assertRaises(d.Hold): j.build_payload(self.batch, 'missing')
        bad = copy.deepcopy(self.batch); bad['requests'].append(bad['requests'][0])
        with self.assertRaises(d.Hold): j.build_payload(bad, 'mail-demo-a')
        bad = copy.deepcopy(self.batch); bad['requests'][0]['request']['target']['content'] += ' altered'
        with self.assertRaises(d.Hold): j.build_payload(bad, 'mail-demo-a')

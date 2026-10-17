import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import decision as d
import jev_run as j
import pipeline
from test_jev_workflow import answer


class PipelineTests(unittest.TestCase):
    def test_public_pipeline_uses_saved_rubric_and_returns_saved_review(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for source, target in [('rubric.example.json','rubric.json'), ('examples/references.json','references.json')]:
                (root/target).write_text(Path(source).read_text())
            inputs = d.load_json('examples/email/inputs.json')
            item_count = len(inputs['items'])
            with patch.dict(os.environ, {'JEV_API_KEY':'test-key'}), patch.object(j, 'post', side_effect=lambda p,k: answer(p)) as post:
                result = pipeline.run(root, inputs, live=True, max_requests=item_count)
                self.assertEqual(result['accepted'], item_count)
                self.assertTrue(Path(result['review_file']).exists())
                self.assertEqual(pipeline.run(root, inputs, live=True, max_requests=0)['accepted'], 0)
                self.assertEqual(post.call_count, item_count)

    def test_explicit_environment_file_reads_only_key_without_execution(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {}, clear=True):
            key_file = Path(directory)/'.env'
            marker = Path(directory)/'should-not-exist'
            key_file.write_text('JEV_API_KEY="fake-key"\nUNRELATED=do-not-load\nRUN=$(touch '+str(marker)+')\n')
            pipeline.load_key(key_file)
            self.assertEqual(os.environ['JEV_API_KEY'], 'fake-key')
            self.assertNotIn('UNRELATED', os.environ)
            self.assertFalse(marker.exists())
            key_file.write_text('JEV_API_KEY=\n')
            with self.assertRaises(d.Hold): pipeline.load_key(key_file)

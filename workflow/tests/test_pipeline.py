import os
import contextlib
import io
import json
from pathlib import Path
import tempfile
import sys
import unittest
from unittest.mock import patch

import decision as d
import jev_run as j
import pipeline
from test_jev_workflow import answer


class PipelineTests(unittest.TestCase):
    def temporary_input(self, root):
        inputs = d.load_json('workflow/demo/inputs.json')
        inputs['items'] = inputs['items'][:1]
        inputs['items'][0]['content'] += '\nFull-source-only marker: café 雨\r\nReply retained.'
        path = root/'temporary-input'/'batch.json'
        path.parent.mkdir()
        path.write_text(json.dumps(inputs, ensure_ascii=False), encoding='utf-8')
        for source, target in [('rubric/rubric.json','rubric.json'), ('rubric/examples.json','references.json')]:
            (root/target).write_text(Path(source).read_text(), encoding='utf-8')
        return path, inputs

    def test_temporary_input_is_removed_before_key_loading_and_provider_call(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path, inputs = self.temporary_input(root)
            sibling = path.with_name('leave-alone.json')
            sibling.write_text('{}')
            def key_loader(_):
                self.assertFalse(path.exists())
            def provider(payload, key):
                self.assertFalse(path.exists())
                self.assertEqual(payload['state']['target']['content'], inputs['items'][0]['content'])
                return answer(payload)
            argv = ['pipeline.py','--root',str(root),'--temporary-input',str(path),
                    '--env-file','unused.env','--live','--max-requests','1']
            stdout = io.StringIO()
            with patch.object(sys, 'argv', argv), patch.object(d, 'read_stdin_json') as stdin, patch.object(pipeline, 'load_key', side_effect=key_loader) as load_key, patch.dict(os.environ, {'JEV_API_KEY':'test-key'}), patch.object(j, 'post', side_effect=provider) as post, contextlib.redirect_stdout(stdout):
                pipeline.main()
            report = json.loads(stdout.getvalue())
            self.assertTrue(report['temporary_input_removed'])
            self.assertEqual(report['accepted'], 1)
            load_key.assert_called_once()
            post.assert_called_once()
            stdin.assert_not_called()
            self.assertTrue(sibling.exists())
            for saved in root.rglob('*'):
                if saved.is_file():
                    self.assertNotIn('Full-source-only marker', saved.read_text(encoding='utf-8'))
            self.assertNotIn('Full-source-only marker', stdout.getvalue())

    def test_temporary_input_is_consumed_in_offline_preview(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path, _ = self.temporary_input(root)
            argv = ['pipeline.py','--root',str(root),'--temporary-input',str(path)]
            stdout = io.StringIO()
            with patch.object(sys, 'argv', argv), patch.object(j, 'post') as post, patch.object(pipeline, 'load_key') as load_key, contextlib.redirect_stdout(stdout):
                pipeline.main()
            self.assertTrue(json.loads(stdout.getvalue())['temporary_input_removed'])
            self.assertFalse(path.exists())
            post.assert_not_called()
            load_key.assert_not_called()

    def test_equivalent_state_root_paths_can_consume_the_same_input(self):
        # System temporary folders can have an aliased ancestor, e.g. on macOS.
        for aliased_root in [True, False]:
            with self.subTest(aliased_root=aliased_root), tempfile.TemporaryDirectory() as directory:
                parent = Path(directory)
                root = parent/'state'
                root.mkdir()
                path, inputs = self.temporary_input(root)
                alias = parent/'state-alias'
                alias.symlink_to(root, target_is_directory=True)
                result = pipeline.consume_temporary_input(
                    alias if aliased_root else root,
                    path if aliased_root else alias/'temporary-input'/'batch.json')
                self.assertEqual(result, inputs)
                self.assertFalse(path.exists())

    def test_malformed_temporary_input_is_removed_without_echoing_source(self):
        for content in [b'{"body":"private-fixture",', b'\xff', b'{"body":NaN}']:
            with self.subTest(content=content), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                path, _ = self.temporary_input(root)
                path.write_bytes(content)
                argv = ['pipeline.py','--root',str(root),'--temporary-input',str(path),'--live','--max-requests','1']
                stdout, stderr = io.StringIO(), io.StringIO()
                with patch.object(sys, 'argv', argv), patch.object(j, 'post') as post, contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    with self.assertRaises(SystemExit) as stopped: pipeline.main()
                self.assertEqual(stopped.exception.code, 2)
                self.assertFalse(path.exists())
                post.assert_not_called()
                self.assertEqual(stdout.getvalue(), '')
                self.assertNotIn('private-fixture', stderr.getvalue())

    def test_key_and_configuration_failures_still_remove_temporary_input(self):
        for failure in ['key', 'configuration']:
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                path, _ = self.temporary_input(root)
                argv = ['pipeline.py','--root',str(root),'--temporary-input',str(path),'--live','--max-requests','1']
                if failure == 'key': argv += ['--env-file',str(root/'missing.env')]
                else: (root/'rubric.json').unlink()
                with patch.object(sys, 'argv', argv), patch.object(j, 'post') as post, contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as stopped: pipeline.main()
                self.assertEqual(stopped.exception.code, 2)
                self.assertFalse(path.exists())
                post.assert_not_called()

    def test_temporary_input_is_removed_on_read_error_or_interrupt(self):
        for error in [OSError('fixture'), KeyboardInterrupt()]:
            with self.subTest(error=type(error)), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                path, _ = self.temporary_input(root)
                with patch.object(d, 'load_json', side_effect=error):
                    with self.assertRaises(type(error)): pipeline.consume_temporary_input(root, path)
                self.assertFalse(path.exists())

    def test_cleanup_failure_stops_before_processing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path, _ = self.temporary_input(root)
            argv = ['pipeline.py','--root',str(root),'--temporary-input',str(path),'--live','--max-requests','1']
            stderr = io.StringIO()
            with patch.object(sys, 'argv', argv), patch.object(Path, 'unlink', side_effect=PermissionError('private-fixture')), patch.object(pipeline, 'run') as run, contextlib.redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as stopped: pipeline.main()
            self.assertEqual(stopped.exception.code, 2)
            self.assertTrue(path.exists())
            self.assertIn('could not be removed', stderr.getvalue())
            self.assertNotIn('private-fixture', stderr.getvalue())
            run.assert_not_called()

    def test_unapproved_locations_and_symlinks_are_not_read_or_removed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path, _ = self.temporary_input(root)
            other = root/'rubric.json'
            key = path.with_name('.env')
            key.write_text('private-fixture')
            link = path.with_name('link.json')
            link.symlink_to(other)
            nested = path.parent/'nested'
            nested.mkdir()
            nested_file = nested/'batch.json'
            nested_file.write_text('{}')
            for refused in [other, key, link, nested_file, path.parent/'missing.json', path.parent]:
                with self.subTest(path=refused), patch.object(d, 'load_json') as read:
                    with self.assertRaises(pipeline.TemporaryInputError): pipeline.consume_temporary_input(root, refused)
                    read.assert_not_called()
            self.assertTrue(other.exists())
            self.assertTrue(key.exists())
            self.assertTrue(link.is_symlink())
            self.assertTrue(nested_file.exists())
            alternate = root/'alternate'
            alternate.mkdir()
            (alternate/'temporary-input').symlink_to(path.parent, target_is_directory=True)
            with self.assertRaises(pipeline.TemporaryInputError):
                pipeline.consume_temporary_input(alternate, alternate/'temporary-input'/'batch.json')
            self.assertTrue(path.exists())

    def test_partial_review_is_printed_with_nonzero_exit_and_saved_successes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for source, target in [('rubric/rubric.json','rubric.json'), ('rubric/examples.json','references.json')]:
                (root/target).write_text(Path(source).read_text())
            inputs = d.load_json('workflow/demo/inputs.json')
            def provider(payload, key):
                if payload['state']['target']['id'] == 'mail-demo-b':
                    raise TimeoutError('fixture')
                return answer(payload, 'skip', 'needs_review')
            stdout, stderr = io.StringIO(), io.StringIO()
            argv = ['pipeline.py','--root',str(root),'--live','--max-requests','4']
            with patch.object(sys, 'argv', argv), patch.object(d, 'read_stdin_json', return_value=inputs), patch.dict(os.environ, {'JEV_API_KEY':'test-key'}), patch.object(j, 'post', side_effect=provider), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as stopped: pipeline.main()
            self.assertEqual(stopped.exception.code, 2)
            report = json.loads(stdout.getvalue())
            self.assertEqual((report['accepted'],report['pending'],report['flagged']), (3,1,3))
            self.assertTrue(Path(report['review_file']).is_file())
            self.assertIn('Partial review saved', stderr.getvalue())

    def test_public_pipeline_uses_saved_rubric_and_returns_saved_review(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for source, target in [('rubric/rubric.json','rubric.json'), ('rubric/examples.json','references.json')]:
                (root/target).write_text(Path(source).read_text())
            inputs = d.load_json('workflow/demo/inputs.json')
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

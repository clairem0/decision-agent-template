import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import decision as d


class ReaderSetupTests(unittest.TestCase):
    def test_personalized_prepare_streams_source_and_uses_saved_rubric_and_references(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inputs = d.load_json('examples/email/inputs.json')
            inputs['items'] = inputs['items'][:1]
            inputs['items'][0]['id'] = 'fictional-reader:thread-1'
            rubric = d.load_json('examples/email/rubric.json'); rubric['version'] = 'reader-approved-test'
            refs = d.load_json('examples/references.json'); refs['references'][0]['distinction'] += ' Approved test refinement.'
            for name, data in [('rubric.json',rubric),('references.json',refs)]:
                (root/name).write_text(json.dumps(data))
            command = [sys.executable,'decision.py','prepare','--root',str(root),'--evaluator','coding-agent:test','--stdin']
            prepared = subprocess.run(command, input=json.dumps(inputs), capture_output=True, text=True)
            self.assertEqual(prepared.returncode, 0, prepared.stderr)
            batch = json.loads(prepared.stdout); request = batch['requests'][0]['request']
            self.assertEqual(len(batch['requests']), 1)
            self.assertEqual(request['target']['id'], 'fictional-reader:thread-1')
            self.assertEqual(request['rubric'], rubric)
            self.assertEqual(request['references'][0]['distinction'], refs['references'][0]['distinction'])
            d.accept(root, batch, {'mode':'simulated','results':[{'id':request['target']['id'],
                     'label':'act','reason':'Fictional test decision.','reference_ids':['email-deadline']}]})
            item = d.read_state(root)['items'][request['target']['id']]
            d.review(root, {'receipt_id':'reader-test','id':request['target']['id'],
                     'decision_id':item['decision']['id'],'action':'correct','label':'track',
                     'note':'Fictional reader correction.'})
            self.assertEqual(subprocess.run(command, input=json.dumps(inputs), text=True, capture_output=True).returncode, 0)
            self.assertEqual(d.load_json(root/'packet.json')['requests'], [])
            self.assertEqual(d.summary(root)['items'][0]['label'], 'track')
            inputs['items'][0]['context'] += ' A later message changes the obligation.'
            self.assertEqual(subprocess.run(command, input=json.dumps(inputs), text=True, capture_output=True).returncode, 0)
            self.assertEqual(len(d.load_json(root/'packet.json')['requests']), 1)
            self.assertEqual(len(d.read_state(root)['items'][request['target']['id']]['reviews']), 1)

    def test_process_input_is_utf8_even_with_non_utf8_console_encoding(self):
        with tempfile.TemporaryDirectory() as directory:
            inputs = d.load_json('examples/email/inputs.json')
            marker = 'Café — 東京'
            inputs['items'][0]['content'] += marker
            env = dict(os.environ, PYTHONIOENCODING='cp1252', PYTHONUTF8='0')
            result = subprocess.run([sys.executable, 'decision.py', 'prepare', '--root', directory,
                '--rubric', 'examples/email/rubric.json', '--references', 'examples/references.json',
                '--evaluator', 'unicode-test', '--stdin'], input=json.dumps(inputs, ensure_ascii=False).encode('utf-8'),
                capture_output=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            batch = json.loads(result.stdout)
            self.assertIn(marker, batch['requests'][0]['request']['target']['content'])
            for command in ('jev_preview.py', 'jev_run.py'):
                preview = subprocess.run([sys.executable, command, '--id', 'mail-demo-a'],
                    input=json.dumps(batch, ensure_ascii=False).encode('utf-8'), capture_output=True, env=env)
                self.assertEqual(preview.returncode, 0, preview.stderr)
                output = json.loads(preview.stdout)
                payload = output.get('payload', output)
                self.assertIn(marker, payload['state']['target']['content'])
            fragment_path = Path(directory)/'native.html'
            rendered = subprocess.run([sys.executable, 'inline_review.py', '--root', directory,
                '--output', str(fragment_path)], capture_output=True, env=env)
            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            self.assertIn('✓', fragment_path.read_text(encoding='utf-8'))

    def test_prepare_requires_actual_evaluator_before_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable,'decision.py','prepare','--root',directory],capture_output=True,text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('--evaluator', result.stderr)
            self.assertFalse((Path(directory)/'state.json').exists())

    def test_missing_reader_files_do_not_silently_classify_demo_emails(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable,'decision.py','prepare','--root',directory,
                                     '--evaluator','coding-agent:test'],capture_output=True,text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Fresh source required', result.stderr)
            self.assertFalse((Path(directory)/'state.json').exists())

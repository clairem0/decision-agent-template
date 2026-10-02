import json
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

import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

import decision as d
import jev_run as j


class JevRunTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)/'attempts'
        inputs = d.load_json('workflow/demo/inputs.json')
        inputs['items'][0]['content'] += ' SOURCE_MARKER_9382'
        self.batch = d.prepare(Path(self.temp.name)/'review', inputs,
                               d.load_json('rubric/rubric.json'), d.load_json('rubric/examples.json'), 'jev-test')
        self.payload = j.build_payload(self.batch, 'mail-demo-a')
        self.response = {'id':'gen-dec-fictional-123', 'model':j.MODEL+'-20260917', 'provider':'TypeSafe',
                         'usage':{'input_tokens':20,'output_tokens':2,'cost':0.001}, 'answers':{}}
        for name, q in self.payload['questions'].items():
            choice = next(iter(q['criteria']))
            self.response['answers'][name] = {'type':'choice','choice':choice,'confidence':1,
                                              'probabilities':{k:int(k==choice) for k in q['criteria']}}

    def run_live(self):
        return j.run(self.batch, 'mail-demo-a', self.root, live=True, max_requests=1)

    def test_preview_needs_no_key_network_or_files_and_live_requires_bound(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(j, 'post') as post:
            self.assertEqual(j.run(self.batch, 'mail-demo-a', self.root)['mode'], 'preview')
            with self.assertRaises(d.Hold): self.run_live()
            with self.assertRaises(d.Hold): j.run(self.batch, 'mail-demo-a', self.root, live=True)
            post.assert_not_called()
        self.assertFalse(self.root.exists())

    def test_attempt_precedes_send_and_success_saves_typed_data_only(self):
        def post(payload, key):
            attempt = json.loads(next(self.root.glob('*.json')).read_text())
            self.assertEqual(attempt['status'], 'started')
            self.assertEqual(payload, self.payload)
            self.assertEqual(key, 'test-key')
            return dict(self.response, echo='SOURCE_MARKER_9382', error='test-key')
        state = (Path(self.temp.name)/'review/state.json').read_bytes()
        with patch.dict(os.environ, {'JEV_API_KEY':'test-key'}), patch.object(j, 'post', side_effect=post) as mock:
            result = self.run_live()
            self.assertEqual(result['status'], 'succeeded')
            self.assertEqual(result['result']['model'], self.response['model'])
            with self.assertRaises(d.Hold): self.run_live()
            self.assertEqual(mock.call_count, 1)
        self.assertEqual(state, (Path(self.temp.name)/'review/state.json').read_bytes())
        saved = next(self.root.glob('*.json')).read_text()
        self.assertNotIn('SOURCE_MARKER_9382', saved); self.assertNotIn('test-key', saved)

    def test_timeout_and_http_failure_are_preserved_without_retry_or_body(self):
        errors = [TimeoutError('SOURCE_MARKER_9382'), urllib.error.HTTPError(j.ENDPOINT, 429, 'SOURCE_MARKER_9382', {}, None)]
        for i, error in enumerate(errors):
            self.root = Path(self.temp.name)/str(i)
            with patch.dict(os.environ, {'JEV_API_KEY':'test-key'}), patch.object(j, 'post', side_effect=error) as mock:
                with self.assertRaises(d.Hold): self.run_live()
                with self.assertRaises(d.Hold): self.run_live()
                self.assertEqual(mock.call_count, 1)
            saved = next(self.root.glob('*.json')).read_text()
            self.assertNotIn('SOURCE_MARKER_9382', saved)
            self.assertEqual(json.loads(saved)['status'], ['uncertain','http_failed'][i])

    def test_invalid_or_partial_answers_preserve_failure(self):
        response = copy.deepcopy(self.response); del response['answers']['evidence_status']
        with patch.dict(os.environ, {'JEV_API_KEY':'test-key'}), patch.object(j, 'post', return_value=response):
            with self.assertRaises(d.Hold): self.run_live()
        self.assertEqual(json.loads(next(self.root.glob('*.json')).read_text())['status'], 'invalid_response')
        for value in [float('nan'), True, -1, 2]:
            bad = copy.deepcopy(self.response); bad['answers']['email_category']['confidence'] = value
            with self.assertRaises(d.Hold): j.validate(bad, self.payload)
        bad = copy.deepcopy(self.response); bad['model']='other-provider'
        with self.assertRaises(d.Hold): j.validate(bad, self.payload)

    def test_uncertain_provider_judgment_stays_flagged_and_not_a_default_assessment(self):
        response = copy.deepcopy(self.response)
        response['answers']['evidence_status'].update(choice='needs_review', probabilities={'sufficient':0,'needs_review':1})
        self.assertTrue(j.validate(response, self.payload)['requires_review'])
        with self.assertRaises(d.Hold): d.accept(Path(self.temp.name)/'review', self.batch, {'mode':'jev','results':[]})

    def test_http_transport_posts_expected_json_with_timeout(self):
        from unittest.mock import MagicMock
        connection = MagicMock()
        connection.__enter__.return_value.read.return_value = json.dumps(self.response).encode()
        opener = MagicMock(); opener.open.return_value = connection
        with patch.object(j.urllib.request, 'build_opener', return_value=opener):
            self.assertEqual(j.post(self.payload, 'test-key'), self.response)
        request = opener.open.call_args.args[0]
        self.assertEqual(request.full_url, j.ENDPOINT)
        self.assertEqual(request.get_method(), 'POST')
        self.assertEqual(request.get_header('Authorization'), 'Bearer test-key')
        self.assertEqual(json.loads(request.data), self.payload)
        self.assertEqual(opener.open.call_args.kwargs['timeout'], 30)

    def test_redirect_is_refused(self):
        request = j.urllib.request.Request(j.ENDPOINT)
        with self.assertRaises(urllib.error.HTTPError):
            j.NoRedirect().redirect_request(request, None, 302, '', {}, 'https://example.test')

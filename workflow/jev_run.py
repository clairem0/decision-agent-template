"""One explicitly authorized Jev experiment. Preview by default; no automatic retries."""
import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.request

import decision as d
from jev_preview import build_payload

ENDPOINT = 'https://api.typesafe.ai/v1/systemone'
MODEL = 'jev-1.13.0'


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, 'Redirect refused', headers, fp)


def post(payload, key):
    request = urllib.request.Request(ENDPOINT, data=d.encoded(payload), method='POST',
                                    headers={'Authorization': 'Bearer '+key, 'Content-Type': 'application/json'})
    with urllib.request.build_opener(NoRedirect).open(request, timeout=30) as response:
        raw = response.read(1_000_001)
    if len(raw) > 1_000_000:
        raise d.Hold('Provider response exceeds the response limit.')
    return json.loads(raw)


def number(value, maximum=None):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0 or (maximum is not None and value > maximum):
        raise d.Hold('Invalid provider numeric value.')
    return value


def validate(response, payload):
    """Retain typed values only; never persist provider text, body echoes or errors."""
    if not isinstance(response, dict):
        raise d.Hold('Invalid provider response.')
    model = response.get('model')
    if not isinstance(model, str) or not re.fullmatch(re.escape(MODEL)+r'(?:-\d{8})?', model):
        raise d.Hold('Unexpected served model; review provider provenance.')
    answers = response.get('answers')
    if not isinstance(answers, dict) or set(answers) != set(payload['questions']):
        raise d.Hold('Provider must answer every question exactly once.')
    clean = {}
    for name, question in payload['questions'].items():
        answer = answers[name]
        allowed = set(question['criteria'])
        if not isinstance(answer, dict) or answer.get('type') != 'choice' or answer.get('choice') not in allowed:
            raise d.Hold('Invalid provider choice.')
        probabilities = answer.get('probabilities')
        if not isinstance(probabilities, dict) or set(probabilities) != allowed:
            raise d.Hold('Incomplete provider probabilities.')
        probabilities = {key: number(value, 1) for key, value in probabilities.items()}
        if not math.isclose(sum(probabilities.values()), 1, abs_tol=.02):
            raise d.Hold('Provider probabilities do not sum to one.')
        clean[name] = {'type': 'choice', 'choice': answer['choice'],
                       'confidence': number(answer.get('confidence'), 1), 'probabilities': probabilities}
    usage = response.get('usage')
    if not isinstance(usage, dict) or not {'input_tokens', 'output_tokens'} <= set(usage):
        raise d.Hold('Provider usage is missing.')
    saved_usage = {}
    for key in ('input_tokens', 'output_tokens', 'cost'):
        if key in usage:
            value = number(usage[key])
            if key.endswith('_tokens') and type(value) is not int:
                raise d.Hold('Invalid provider token count.')
            saved_usage[key] = value
    result = {'model': model, 'answers': clean, 'usage': saved_usage}
    # Strict provider metadata formats prevent source echoes from becoming local logs.
    if isinstance(response.get('id'), str) and re.fullmatch(r'gen-dec-[A-Za-z0-9-]{1,128}', response['id']):
        result['id'] = response['id']
    if response.get('provider') == 'TypeSafe':
        result['provider'] = 'TypeSafe'
    result['requires_review'] = (clean['evidence_status']['choice'] == 'needs_review')
    return result


def run(batch, item_id, root, *, live=False, max_requests=0, metrics=None):
    payload = build_payload(batch, item_id, MODEL)
    if not live:
        return {'mode': 'preview', 'destination': ENDPOINT, 'payload': payload}
    if max_requests != 1:
        raise d.Hold('A live experiment requires --max-requests 1; only one request is sent.')
    key = os.environ.get('JEV_API_KEY', '').strip()
    if not key or any(ord(c) < 33 or ord(c) > 126 for c in key):
        raise d.Hold('Configure JEV_API_KEY in the environment; never paste it into chat.')
    digest = d.fingerprint(payload)
    root = Path(root)
    with d.writer_lock(root):
        path = root / (digest+'.json')
        if path.exists():
            raise d.Hold('This payload already has an attempt in this folder. Inspect its outcome; no automatic resend.')
        attempt = {'version': 1, 'status': 'started', 'at': datetime.now(timezone.utc).isoformat(),
                   'endpoint': ENDPOINT, 'requested_model': MODEL, 'payload_hash': digest,
                   'target_id': payload['state']['target']['id'], 'max_requests': 1}
        d.atomic_write(path, d.encoded(attempt))
        try:
            started = time.perf_counter()
            try:
                raw = post(payload, key)
            finally:
                attempt['request_seconds'] = time.perf_counter() - started
            result = validate(raw, payload)
        except BaseException as error:
            attempt['status'] = ('http_failed' if isinstance(error, urllib.error.HTTPError) else
                                 'invalid_response' if isinstance(error, (d.Hold, ValueError, KeyError, TypeError)) else 'uncertain')
            if isinstance(error, urllib.error.HTTPError):
                attempt['http_status'] = error.code
            d.atomic_write(path, d.encoded(attempt))
            if isinstance(error, (KeyboardInterrupt, SystemExit)):
                raise
            raise d.Hold('Jev attempt '+attempt['status']+'. Inspect the attempt record before any deliberate retry; no response body was saved.') from None
        else:
            attempt.update(status='succeeded', result=result)
            d.atomic_write(path, d.encoded(attempt))
        finally:
            if metrics is not None:
                metrics.append({'target_id': item_id, 'seconds': attempt['request_seconds'],
                                'status': attempt['status'], 'usage': attempt.get('result', {}).get('usage')})
    return {'mode': 'jev', 'attempt_file': str(path), **attempt}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--id', required=True)
    parser.add_argument('--root', default='local/jev-experiment/attempts')
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--max-requests', type=int, default=0)
    args = parser.parse_args()
    try:
        result = run(d.read_stdin_json(), args.id, args.root, live=args.live, max_requests=args.max_requests)
        print(json.dumps(result, indent=2, allow_nan=False))
    except (d.Hold, OSError, ValueError, KeyError, TypeError):
        # Do not print arbitrary input/provider error text: it can contain full email source.
        parser.exit(2, 'Held: check the request, environment and any saved attempt. No automatic retry. See setup/jev.md#troubleshooting.\n')


if __name__ == '__main__':
    main()

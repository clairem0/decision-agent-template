"""Apply Jev to a prepared batch and save its decisions for the existing review."""
import argparse
import json
from pathlib import Path

import decision as d
import jev_run as j

EVALUATOR = 'jev:jev-1.13.0:email-v3'


def run(root, batch, *, live=False, max_requests=0):
    root = Path(root)
    state = d.read_state(root)
    if batch.get('contract') != d.CONTRACT:
        raise d.Hold('Prepare a current batch first.')
    payloads = []
    for wrapper in batch['requests']:
        request = wrapper['request']; item_id = request['target']['id']
        row = state['items'].get(item_id)
        if (request['evaluator'] != EVALUATOR or not row or row['status'] != 'pending' or
                row['current'] != wrapper['fingerprint'] or
                d.retained_request(request) != row['request']):
            raise d.Hold('Use a fresh Jev batch and its matching review folder.')
        payloads.append(j.build_payload(batch, item_id))
    if not live:
        return {'mode': 'preview', 'pending': len(payloads), 'destination': j.ENDPOINT, 'model': j.MODEL}
    if type(max_requests) is not int or max_requests < len(payloads):
        raise d.Hold('Set a request bound covering this small agreed batch.')
    results = []
    for payload in payloads:
        item_id = payload['state']['target']['id']
        digest = d.fingerprint(payload)
        path = root/'attempts'/(digest+'.json')
        if path.exists():
            attempt = d.load_json(path)
            if (attempt.get('status') != 'succeeded' or attempt.get('payload_hash') != digest or
                    attempt.get('target_id') != item_id or attempt.get('endpoint') != j.ENDPOINT):
                raise d.Hold('Reconcile the existing failed or uncertain attempt; it was not retried.')
        else:
            attempt = j.run(batch, item_id, root/'attempts', live=True, max_requests=1)
        provider = j.validate(attempt['result'], payload)
        label = provider['answers']['email_category']['choice']
        if label == 'skip' and provider['requires_review']:
            raise d.Hold('Jev suggested Skip with missing evidence. Review the saved result and supply context; no decision was accepted.')
        definition = payload['state']['rubric']['labels'][label]
        results.append({'id': item_id, 'label': label,
                        'reason': 'Category definition: '+definition+' (Jev supplies no written reason.)',
                        'reference_ids': [],
                        'uncertainty': 'Jev flagged missing or contradictory evidence; review the original conversation.' if provider['requires_review'] else '',
                        'provider_result': provider, 'payload_hash': digest})
    if results:
        d.accept(root, batch, {'mode': 'jev', 'results': results})
    return {'mode': 'jev', 'accepted': len(results), 'pending': 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--max-requests', type=int, default=0)
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.root, d.read_stdin_json(), live=args.live, max_requests=args.max_requests)))
    except (d.Hold, OSError, ValueError, KeyError, TypeError):
        parser.exit(2, 'Held: inspect saved attempts and the prepared batch. No automatic retry. See docs/jev.md.\n')


if __name__ == '__main__':
    main()

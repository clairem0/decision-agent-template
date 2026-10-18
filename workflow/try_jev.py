"""Try Jev on 50 bundled fictional threads. No Gmail or personal configuration."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import statistics
import time
import uuid

import decision as d
import inline_review
import jev_workflow as w
from pipeline import load_key

FIXTURES = Path(__file__).resolve().parent / 'synthetic'
DEFAULT_ROOT = Path('local/synthetic-inbox')


def load_samples():
    # Intentionally no input/rubric/profile overrides or connector entry points.
    inputs = d.load_json(FIXTURES/'inbox.json')
    rubric = d.load_json(FIXTURES/'rubric.json')
    examples = d.load_json(FIXTURES/'examples.json')
    if len(inputs['items']) != 50 or any(row['status'] != 'complete' for row in inputs['items']):
        raise d.Hold('Expected the complete, bundled 50-thread synthetic inbox.')
    return inputs, rubric, examples


def claim_root(root, identity):
    """Never open an existing personal review as a synthetic test."""
    root = Path(root)
    if root.is_symlink():
        raise d.Hold('Use a dedicated synthetic review folder, not a symlink.')
    root.mkdir(parents=True, exist_ok=True)
    marker = root/'synthetic-inbox.json'
    if not marker.exists() and any(root.iterdir()):
        raise d.Hold('This folder is not an owned synthetic test. Leave it unchanged.')
    with d.writer_lock(root):
        if marker.exists():
            if d.load_json(marker) != identity:
                raise d.Hold('Synthetic inputs changed. Preserve this run and review the change before starting another trial.')
        else:
            # Recheck after acquiring the lock; do not claim another workflow's folder.
            if any(p.name != '.writer.lock' for p in root.iterdir()):
                raise d.Hold('This folder already belongs to another workflow.')
            d.atomic_write(marker, d.encoded(identity))
        if (root/'rubric.json').exists() or (root/'references.json').exists():
            raise d.Hold('Personalized configuration belongs in a separate workflow, not this fixed synthetic test.')
        state = d.read_state(root)
        if set(state['items']) - set(identity['source_ids']):
            raise d.Hold('Unexpected sources in the synthetic test folder. Do not mix inboxes.')


def compare(predictions):
    # Called only after the original provider predictions have been saved separately.
    expected = d.load_json(FIXTURES/'expected.json')['expectations']
    if set(expected) != set(predictions):
        raise d.Hold('Expected answers do not cover the same synthetic inbox.')
    mismatches = []
    for key, actual in predictions.items():
        want = expected[key]
        if actual['label'] != want['label'] or actual['needs_review'] != want['needs_review']:
            mismatches.append({'id': key, 'actual': actual, 'expected': want})
    return {'note': 'Agreement with author-written expectations; not real-inbox accuracy.',
            'category_matches': sum(predictions[k]['label'] == expected[k]['label'] for k in expected),
            'evidence_matches': sum(predictions[k]['needs_review'] == expected[k]['needs_review'] for k in expected),
            'total': len(expected), 'mismatches': mismatches}


def run(root=DEFAULT_ROOT, *, live=False, max_requests=0, env_file=None):
    started = time.perf_counter()
    inputs, rubric, examples = load_samples()
    load_seconds = time.perf_counter() - started
    count = len(inputs['items'])
    # Preview does not inspect a key, saved user state, or the expected answers.
    if not live:
        return {'mode': 'preview', 'threads': count, 'retrieval': 'Not used: bundled fictional data only.',
                'destination': w.j.ENDPOINT, 'model': w.j.MODEL, 'new_api_calls': 0,
                'load_seconds': load_seconds,
                'note': 'No classifications or Jev speed measurements yet. Live mode can make up to 50 sequential API calls.'}
    if type(max_requests) is not int or max_requests < count:
        raise d.Hold('The synthetic test requires --live --max-requests 50. This is a request bound, not a dollar cap.')
    identity = {'kind': 'synthetic-inbox-v1', 'dataset_hash': d.fingerprint([inputs, rubric, examples]),
                'source_ids': [i['id'] for i in inputs['items']]}
    root = Path(root)
    claim_root(root, identity)
    # A separate run lock protects a full trial, including comparisons and reports.
    with d.writer_lock(root/'runs'):
        run_id = uuid.uuid4().hex
        run_dir = root/'runs'/run_id
        run_dir.mkdir()
        metrics = []
        report = {'run_id': run_id, 'at': datetime.now(timezone.utc).isoformat(), 'status': 'held',
                  'mode': 'jev', 'threads': count, 'dataset_hash': identity['dataset_hash'],
                  'retrieval': 'Not used: bundled fictional data only. Gmail retrieval was not measured.',
                  'timing_scope': 'Wall-clock time on this machine. API round trips include network and response decoding, not just model inference. Calls are sequential.',
                  'timings_seconds': {'load_samples': load_seconds}, 'comparison': None}
        def measure(name, operation):
            start = time.perf_counter()
            try:
                return operation()
            finally:
                report['timings_seconds'][name] = time.perf_counter() - start
        try:
            if env_file:
                load_key(env_file)
            batch = measure('prepare', lambda: d.prepare(root, inputs, rubric, examples, w.EVALUATOR))
            report['reused_decisions'] = count - len(batch['requests'])
            result = measure('classify_and_save', lambda: w.run(root, batch, live=True,
                             max_requests=max_requests, metrics=metrics))
            report['reused_attempts'] = result['accepted'] - len(metrics)
            state = d.read_state(root)
            predictions = {}
            for item in inputs['items']:
                decision = state['items'][item['id']]['decision']
                # Score original provider answers, never the reader's corrected category.
                provider = decision['provider_result']
                predictions[item['id']] = {'label': provider['answers']['email_category']['choice'],
                                           'needs_review': provider['requires_review']}
            d.atomic_write(run_dir/'predictions.json', d.encoded(predictions))
            report['comparison'] = measure('compare', lambda: compare(predictions))
            def review():
                d.render(root)
                inline_review.render(root, run_dir/'review.html')
            measure('build_review', review)
            report['review_file'] = str(root/'review/index.html')
            report['inline_review_file'] = str(run_dir/'review.html')
            report['status'] = 'complete'
        finally:
            durations = [m['seconds'] for m in metrics]
            report['new_api_calls'] = len(metrics)
            report['successful_new_calls'] = sum(m['status'] == 'succeeded' for m in metrics)
            report['api_round_trip_seconds'] = sum(durations) if durations else None
            report['median_api_round_trip_seconds'] = statistics.median(durations) if durations else None
            report['new_call_tokens'] = {k: sum(m['usage'][k] for m in metrics if m['usage'])
                                         for k in ('input_tokens', 'output_tokens')}
            report['requests'] = metrics
            report['total_seconds'] = time.perf_counter() - started
            report['report_file'] = str(run_dir/'report.json')
            # Failure timings and counts remain visible; no fabricated labels or automatic retries.
            d.atomic_write(run_dir/'report.json', d.encoded(report))
    return report


def describe(report):
    print(f"50 fictional email threads · {'preview only' if report['mode'] == 'preview' else report['status']}")
    print('Inbox retrieval: not used; no email account connected.')
    if report['mode'] == 'preview':
        print(f"Load samples: {report['load_seconds']:.3f}s · API calls: 0")
        print('To test Jev, ask your agent to run this same inbox with --live --max-requests 50.')
        return
    labels = {'load_samples': 'Load samples', 'prepare': 'Prepare requests',
              'classify_and_save': 'Classify and save', 'compare': 'Compare with expectations', 'build_review': 'Build review'}
    for name, value in report['timings_seconds'].items():
        print(f'{labels[name]}: {value:.3f}s')
    print(f"New API calls: {report['new_api_calls']} · Reused decisions: {report['reused_decisions']} · Reused attempts: {report['reused_attempts']}")
    if report['new_api_calls']:
        print(f"API round trips: {report['api_round_trip_seconds']:.3f}s total; {report['median_api_round_trip_seconds']:.3f}s median per call (included in classification time).")
        usage = report['new_call_tokens']
        print(f"New successful calls used {usage['input_tokens']} input tokens and {usage['output_tokens']} output tokens.")
    else:
        print('All results reused. This run does not measure fresh Jev speed.')
    print(f"Total: {report['total_seconds']:.3f}s. Calls are sequential; round trips include network time.")
    comparison = report['comparison']
    print(f"Author expectations: {comparison['category_matches']}/50 categories; {comparison['evidence_matches']}/50 evidence flags. This is not real-inbox accuracy.")
    print('Review: '+report['review_file'])
    print('Report: '+report['report_file'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', help='Explicitly send the fixed 50-thread fictional inbox to Jev')
    parser.add_argument('--max-requests', type=int, default=0)
    parser.add_argument('--env-file', help='Explicit local Jev key file; unused in preview')
    parser.add_argument('--root', default=str(DEFAULT_ROOT), help='Dedicated synthetic results folder; existing personal folders are refused')
    args = parser.parse_args()
    try:
        describe(run(args.root, live=args.live, max_requests=args.max_requests, env_file=args.env_file))
    except (d.Hold, OSError, ValueError, KeyError, TypeError):
        parser.exit(2, 'Held: check the dedicated synthetic folder, request bound, key and saved attempts/reports. No automatic retry. See workflow/README.md#try-jev-without-gmail.\n')


if __name__ == '__main__':
    main()

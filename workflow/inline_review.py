"""Render saved decisions for an agent's inline conversation surface. No network."""
import argparse
import json
import os
from pathlib import Path
import uuid

import decision as d

TEMPLATE = Path(__file__).resolve().parent / 'review_assets' / 'inline-review.html'


def render(root, output, include_seen=False):
    state = d.read_state(root)
    items, holds = [], []
    for key, row in state['items'].items():
        source, assessment = row['source'], row['decision']
        if row['status'] != 'current' or not assessment:
            holds.append({'title': source.get('title', key), 'reason': row.get('hold', 'Awaiting classification.'),
                          'original_url': d.source_link(source.get('original_url'))})
            continue
        if not include_seen and (assessment['acknowledged'] or assessment['delivered']):
            continue
        current = assessment['correction'] or assessment
        summary = current['reason']
        if assessment['correction']:
            summary_label = 'Your correction'
        elif assessment['mode'] == 'jev':
            summary_label = 'Category definition'
            summary = summary.removeprefix('Category definition: ').removesuffix(' (Jev supplies no written reason.)')
        else:
            summary_label = 'Summary' if assessment['mode'] == 'simulated' else 'Agent summary'
        items.append({'id': key, 'decision_id': assessment['id'], 'title': source['title'],
                      'sender': source.get('sender', source['kind'].title()),
                      'label': current['label'], 'summary': summary, 'summary_label': summary_label,
                      'original_url': d.source_link(source.get('original_url')),
                      'uncertainty': assessment.get('uncertainty', ''),
                      'mode': assessment['mode']})
    priority = {label: index for index, label in enumerate(d.LABEL_NAMES)}
    items.sort(key=lambda item: priority.get(item['label'], len(priority)))
    review_id = uuid.uuid4().hex
    payload = {'review_id': review_id, 'items': items, 'holds': holds,
               'names': d.LABEL_NAMES, 'handoff': d.HANDOFF,
               'coverage': state['scans'][-1] if state['scans'] else {}}
    # Source text cannot close the data script or become executable markup.
    data = json.dumps(payload, ensure_ascii=True).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    fragment = TEMPLATE.read_text(encoding='utf-8').replace('__REVIEW_ROOT__', 'decision-review-'+review_id).replace('__REVIEW_DATA__', data)
    if len(fragment.encode()) >= 1_000_000:
        raise d.Hold('Inline review exceeds 1 MB; explicitly split the review, never truncate review metadata.')
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    # Delivered snapshots keep their exact decision mappings; never overwrite one.
    descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
        stream.write(fragment)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default='local/email-demo')
    parser.add_argument('--output', required=True, help='New fragment in an authorized, private conversation output directory')
    parser.add_argument('--include-seen', action='store_true', help='Explicit full review, including cleared decisions')
    args = parser.parse_args()
    try:
        print(render(args.root, args.output, args.include_seen))
    except (d.Hold, OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, 'Held: '+str(error)+'\n')


if __name__ == '__main__':
    main()

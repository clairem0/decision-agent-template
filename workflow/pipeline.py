"""Run the email pipeline on complete messages supplied by your agent's connector."""
import argparse
import json
import os
from pathlib import Path
import shlex

import decision as d
import jev_workflow as j


def load_key(path):
    """Read only the named key from an explicitly selected file; never execute it."""
    values = []
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        if line.strip().startswith('JEV_API_KEY='):
            parts = shlex.split(line.strip().split('=', 1)[1], comments=True)
            if len(parts) != 1:
                raise d.Hold('Set one nonempty JEV_API_KEY in the selected environment file.')
            values.append(parts[0])
    if len(values) != 1:
        raise d.Hold('Set exactly one JEV_API_KEY in the selected environment file.')
    os.environ['JEV_API_KEY'] = values[0]


def run(root, inputs, *, live=False, max_requests=0):
    root = Path(root)
    batch = d.prepare(root, inputs, d.load_json(root/'rubric.json'),
                      d.load_json(root/'references.json'), j.EVALUATOR)
    result = j.run(root, batch, live=live, max_requests=max_requests)
    if live:
        result['review_file'] = str(d.render(root))
        result['summary'] = d.summary(root)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default='local/my-review')
    parser.add_argument('--env-file', help='Explicit local key file; never loaded by default')
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--max-requests', type=int, default=0)
    args = parser.parse_args()
    try:
        if args.live and args.env_file:
            load_key(args.env_file)
        print(json.dumps(run(args.root, d.read_stdin_json(), live=args.live, max_requests=args.max_requests)))
    except (d.Hold, OSError, ValueError, KeyError, TypeError):
        parser.exit(2, 'Held: check setup, source coverage and saved attempts. See setup/README.md.\n')


if __name__ == '__main__':
    main()

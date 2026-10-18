import json
from pathlib import Path
import tempfile
import unittest

import decision as d
import inline_review


class InlineReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        inputs = d.load_json('workflow/demo/inputs.json')
        inputs['items'][0]['content'] += '\n</script><img src=x onerror=alert(1)>'
        batch = d.prepare(self.root, inputs, d.load_json('rubric/rubric.json'),
                          d.load_json('rubric/examples.json'), 'inline-test')
        d.accept(self.root, batch, d.load_json('workflow/demo/demo-results.json'))

    def payload(self, name, include_seen=False):
        path = inline_review.render(self.root, self.root/name, include_seen)
        fragment = path.read_text()
        data = fragment.split('class="dr-data">')[1].split('</script>')[0]
        return fragment, json.loads(data)

    def test_fragment_omits_bodies_and_preserves_current_decision_mappings(self):
        before = (self.root/'state.json').read_bytes()
        fragment, payload = self.payload('first.html')
        self.assertNotIn('<html', fragment)
        self.assertNotIn('</script><img', fragment)
        self.assertNotIn('content', payload['items'][0]); self.assertNotIn('context', payload['items'][0])
        state = d.read_state(self.root)
        for item in payload['items']:
            self.assertEqual(item['decision_id'], state['items'][item['id']]['decision']['id'])
        self.assertEqual((self.root/'state.json').read_bytes(), before)
        self.assertIn('window.openai.sendFollowUpMessage', fragment)
        self.assertIn('Copy changes to chat', fragment)

    def test_submitted_receipt_uses_existing_persistence_and_unchanged_choice_stays_quiet(self):
        _, payload = self.payload('first.html')
        item = payload['items'][0]
        receipt = {'receipt_id': payload['review_id']+':1', 'id': item['id'],
                   'decision_id': item['decision_id'], 'action': 'correct', 'label': 'read',
                   'note': 'Fictional test correction.', 'propose_teaching': True}
        d.review(self.root, receipt)
        d.review(self.root, receipt)
        _, quiet = self.payload('quiet.html')
        self.assertNotIn(item['id'], [i['id'] for i in quiet['items']])
        _, full = self.payload('full.html', include_seen=True)
        self.assertEqual(next(i for i in full['items'] if i['id']==item['id'])['label'], 'read')
        self.assertEqual(len(d.read_state(self.root)['items'][item['id']]['reviews']), 1)
        # Requesting a proposal must not approve or write a teaching library.
        self.assertFalse((self.root/'references.json').exists())

    def test_only_submitted_user_choices_remove_items_from_the_next_review(self):
        _, first = self.payload('first.html')
        items = {item['id']: item for item in first['items']}
        for item in items.values():
            d.review(self.root, {'receipt_id': 'shown-'+item['id'], 'id': item['id'],
                     'decision_id': item['decision_id'], 'action': 'delivered', 'note': 'Shown in chat.'})
        _, delivered = self.payload('delivered.html')
        self.assertEqual(delivered['items'], first['items'])
        # Leave A untouched; explicitly acknowledge B, assign C, and correct D.
        for item_id, action, extra in (
                ('mail-demo-b', 'seen', {}),
                ('mail-demo-c', 'assign', {'note': 'Draft a note about the guide.'}),
                ('mail-demo-d', 'correct', {'label': 'read', 'note': 'I want this sale update.'})):
            item = items[item_id]
            d.review(self.root, {'receipt_id': 'choice-'+item_id, 'id': item_id,
                     'decision_id': item['decision_id'], 'action': action, **extra})
        before = d.read_state(self.root)
        _, next_review = self.payload('next.html')
        self.assertEqual([item['id'] for item in next_review['items']], ['mail-demo-a'])
        self.assertEqual(next_review['items'][0]['decision_id'], items['mail-demo-a']['decision_id'])
        _, full = self.payload('full.html', include_seen=True)
        self.assertEqual(len(full['items']), 4)
        self.assertEqual(d.read_state(self.root), before)
        self.assertEqual(before['items']['mail-demo-c']['task']['status'], 'open')

    def test_metadata_only_retrieval_failure_renders_without_a_subject(self):
        failed = {'coverage': {'status': 'partial', 'scope': 'Fictional retry', 'detail': 'One unreadable conversation.'},
                  'items': [{'id': 'fictional-account:unreadable', 'status': 'failed'}]}
        d.prepare(self.root, failed, {}, {'references': []}, 'inline-test')
        _, payload = self.payload('metadata-only.html')
        self.assertEqual(payload['holds'][0]['title'], 'fictional-account:unreadable')
        self.assertIsNone(payload['holds'][0]['original_url'])
        page = d.render(self.root).read_text()
        self.assertIn('fictional-account:unreadable', page)
        self.assertNotIn('data-id="fictional-account:unreadable"', page)

    def test_snapshots_are_unique_and_cannot_overwrite_delivered_file(self):
        _, first = self.payload('first.html')
        _, second = self.payload('second.html')
        self.assertNotEqual(first['review_id'], second['review_id'])
        with self.assertRaises(FileExistsError):
            self.payload('first.html')

    def test_summary_labels_distinguish_demo_agent_jev_and_user_text(self):
        state = d.read_state(self.root)
        rows = list(state['items'].values())
        rows[1]['decision']['mode'] = 'agent'
        rows[2]['decision']['mode'] = 'jev'
        rows[2]['decision']['reason'] = 'Category definition: Wanted reading. (Jev supplies no written reason.)'
        rows[3]['decision']['mode'] = 'jev'
        rows[3]['decision']['correction'] = {'label': 'read', 'reason': 'I want this update.'}
        (self.root/'state.json').write_text(json.dumps(state))
        _, payload = self.payload('summary-labels.html', include_seen=True)
        by_id = {item['id']: item for item in payload['items']}
        self.assertEqual(by_id['mail-demo-a']['summary_label'], 'Summary')
        self.assertEqual(by_id['mail-demo-b']['summary_label'], 'Agent summary')
        self.assertEqual(by_id['mail-demo-c']['summary_label'], 'Category definition')
        self.assertEqual(by_id['mail-demo-c']['summary'], 'Wanted reading.')
        self.assertEqual(by_id['mail-demo-d']['summary_label'], 'Your correction')
        self.assertEqual(by_id['mail-demo-d']['summary'], 'I want this update.')

    def test_category_order_uses_saved_corrections_and_leaves_holds_separate(self):
        state = d.read_state(self.root)
        current = [row for row in state['items'].values() if row['status'] == 'current' and row['decision']]
        # Reverse the categories across source IDs so accidental source ordering fails.
        labels = ['skip', 'read', 'act']
        for row, label in zip(current, labels):
            row['decision']['label'] = label
            row['decision']['correction'] = None
        current[0]['decision']['correction'] = {'label': 'act', 'reason': 'Approved correction.'}
        (self.root/'state.json').write_text(json.dumps(state))
        _, payload = self.payload('ordered.html', include_seen=True)
        priority = {label: index for index, label in enumerate(['act', 'read', 'skip'])}
        ranks = [priority[item['label']] for item in payload['items']]
        self.assertEqual(ranks, sorted(ranks))
        self.assertEqual(payload['items'][0]['summary'], 'Approved correction.')
        self.assertEqual(len(payload['holds']), sum(row['status'] != 'current' or not row['decision'] for row in state['items'].values()))


if __name__ == '__main__':
    unittest.main()

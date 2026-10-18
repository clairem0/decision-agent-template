// Shared by the inline review and the local copy-to-chat review. No scheduling API.
const reminderZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
function reminderCaption(reminder) {
  if (reminder.when === 'requested') return reminder.text;
  return reminder.when === 'next_review' ? 'Next review' : new Date(reminder.at).toLocaleString(undefined, {
    month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit', timeZoneName: 'short'
  });
}
function reminderFields() {
  return '<label>When should I remind you?<textarea class="reminder-text" aria-label="Reminder time" maxlength="500" placeholder="e.g. tomorrow at 9 AM"></textarea></label><p>Leave blank for next review.</p>'
    + '<p class="reminder-detail" role="status"></p><p>Returns during a review. No separate notification.</p>';
}
function reminderDraft(container) {
  return {text: container.querySelector('.reminder-text').value};
}
function readReminder(container) {
  const {text} = reminderDraft(container);
  if (!text.trim()) return {when: 'next_review'};
  if (text.length > 500) throw new Error('Keep the reminder time under 500 characters.');
  // The coding agent resolves language in chat; the UI preserves the request and its time context.
  return {when: 'requested', text, timezone: reminderZone, requested_at: new Date().toISOString()};
}
function bindReminder(container, draft = {}) {
  container.querySelector('.reminder-text').value = draft.text || '';
  const refresh = () => {
    const custom = Boolean(reminderDraft(container).text.trim());
    container.querySelector('.reminder-detail').hidden = !custom;
    container.querySelector('.reminder-detail').textContent = 'Your agent will confirm the time in chat · ' + reminderZone;
  };
  container.querySelector('.reminder-text').addEventListener('input', refresh);
  refresh();
}

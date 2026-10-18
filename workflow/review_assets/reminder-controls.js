// Shared by the inline review and the local copy-to-chat review. No scheduling API.
const reminderZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
function reminderCaption(reminder) {
  return reminder.when === 'next_review' ? 'Next review' : new Date(reminder.at).toLocaleString(undefined, {
    month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit', timeZoneName: 'short'
  });
}
function reminderFields() {
  return '<label>When?<select class="reminder-when cursor-interaction" aria-label="Remind me when">'
    + '<option value="next_review">Next review</option><option value="custom">Choose date &amp; time…</option></select></label>'
    + '<label class="reminder-custom" hidden>Date &amp; time<input class="reminder-date" type="datetime-local" aria-label="Reminder date and time"></label>'
    + '<p class="reminder-detail" role="status"></p><p class="reminder-help"></p>';
}
function reminderDraft(container) {
  return {preset: container.querySelector('.reminder-when').value, local: container.querySelector('.reminder-date').value};
}
function readReminder(container) {
  const {preset, local} = reminderDraft(container);
  if (preset === 'next_review') return {when: 'next_review'};
  let date;
  if (preset === 'custom') {
    // Check the round trip: nonexistent local times at a daylight-saving jump must not shift silently.
    const parts = local.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})$/);
    if (!parts) throw new Error('Choose a date and time.');
    date = new Date(local);
    const actual = [date.getFullYear(), date.getMonth() + 1, date.getDate(), date.getHours(), date.getMinutes()];
    if (actual.some((value, i) => value !== Number(parts[i + 1]))) throw new Error('That local time does not exist. Choose another time.');
  } else throw new Error('Choose when to bring this back.');
  if (!Number.isFinite(date.getTime()) || date <= new Date()) throw new Error('Choose a future date and time.');
  return {when: 'at', at: date.toISOString()};
}
function bindReminder(container, draft = {}) {
  container.querySelector('.reminder-when').value = draft.preset || 'next_review';
  container.querySelector('.reminder-date').value = draft.local || '';
  const refresh = () => {
    const custom = reminderDraft(container).preset === 'custom';
    container.querySelector('.reminder-custom').hidden = !custom;
    container.querySelector('.reminder-detail').hidden = !custom;
    container.querySelector('.reminder-help').textContent = custom ? 'Returns in your first review at or after this time. No separate notification.' : 'Returns in your next review. No separate notification.';
    let caption;
    try { caption = reminderCaption(readReminder(container)); } catch (error) { caption = error.message; }
    container.querySelector('.reminder-detail').textContent = caption + ' · ' + reminderZone;
  };
  container.querySelectorAll('select,input').forEach(field => field.addEventListener('input', refresh));
  refresh();
}

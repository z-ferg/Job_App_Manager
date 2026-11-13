// Dates are stored as ISO strings: 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:mm' (local time).

export function parseDate(iso) {
  const [d, t] = iso.split('T');
  const [y, m, day] = d.split('-').map(Number);
  const [hh, mm] = t ? t.split(':').map(Number) : [0, 0];
  return new Date(y, m - 1, day, hh, mm);
}

export const hasTime = (iso) => iso.includes('T');

export function startOfDay(date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

export const formatShort = (iso) =>
  parseDate(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

export const formatWeekdayShort = (iso) =>
  parseDate(iso).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });

export const formatWeekday = (iso) =>
  parseDate(iso).toLocaleDateString('en-US', { weekday: 'long' });

export const formatTime = (iso) =>
  parseDate(iso).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });

export const monthAbbr = (iso) =>
  parseDate(iso).toLocaleDateString('en-US', { month: 'short' }).toUpperCase();

export const dayOfMonth = (iso) => String(parseDate(iso).getDate()).padStart(2, '0');

// Group a reminder into Today / This week / Later relative to `now`.
export function reminderGroup(iso, now = new Date()) {
  const day = startOfDay(parseDate(iso));
  const today = startOfDay(now);
  const diffDays = Math.round((day - today) / 86400000);
  if (diffDays <= 0) return 'Today';
  if (diffDays <= 7) return 'This week';
  return 'Later';
}

export function reminderWhen(iso, now = new Date()) {
  const group = reminderGroup(iso, now);
  if (group === 'Today') return hasTime(iso) ? `Today · ${formatTime(iso)}` : 'Today';
  return hasTime(iso) ? `${formatWeekdayShort(iso)} · ${formatTime(iso)}` : formatWeekdayShort(iso);
}

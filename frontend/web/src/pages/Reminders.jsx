import { useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import Icon from '../components/Icon.jsx';
import { REMINDER_TYPES } from '../api/reminders.js';
import { formatShort, parseDate, reminderGroup, reminderWhen, startOfDay } from '../utils/dates.js';

const GROUPS = ['Today', 'This week', 'Later'];

function NewReminderForm({ applications, fairs, goingFairIds, onSave }) {
  const empty = {
    linkTo: 'application',
    type: 'Follow-up',
    applicationId: '',
    eventId: '',
    date: new Date().toISOString().slice(0, 10),
    time: '09:00',
  };
  const [form, setForm] = useState(empty);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  // Switching what the reminder is for also picks the type that usually goes with it.
  const setLinkTo = (linkTo) =>
    setForm({ ...form, linkTo, type: linkTo === 'event' ? 'Event Application' : 'Follow-up' });

  const isEvent = form.linkTo === 'event';
  const eventId = Number(form.eventId);
  const willRegister = isEvent && form.eventId !== '' && !goingFairIds.includes(eventId);
  const upcomingFairs = fairs.filter((f) => parseDate(f.date) >= startOfDay(new Date()));

  const submit = async (e) => {
    e.preventDefault();
    setError(null);
    setSaving(true);
    try {
      await onSave({
        type: form.type,
        ...(isEvent ? { eventId } : { applicationId: Number(form.applicationId) }),
        due: form.time ? `${form.date}T${form.time}` : form.date,
      });
      setForm(empty);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <form className="card reminder-form" onSubmit={submit}>
      <h2 className="card__title">New reminder</h2>
      <fieldset className="fieldset">
        <legend>Reminder for</legend>
        <div className="segmented" role="radiogroup">
          {[['application', 'An application'], ['event', 'A career fair']].map(([value, label]) => (
            <label key={value} className={`segmented__opt${form.linkTo === value ? ' is-active' : ''}`}>
              <input
                type="radio"
                name="r-link-to"
                value={value}
                checked={form.linkTo === value}
                onChange={() => setLinkTo(value)}
              />
              {label}
            </label>
          ))}
        </div>
      </fieldset>
      {isEvent ? (
        <div className="field">
          <label htmlFor="r-event">Career fair</label>
          <select id="r-event" value={form.eventId} onChange={set('eventId')} required>
            <option value="" disabled>
              {upcomingFairs.length ? 'Choose a fair' : 'No upcoming fairs'}
            </option>
            {upcomingFairs.map((f) => (
              <option key={f.id} value={f.id}>
                {`${f.name} · ${formatShort(f.date)}${goingFairIds.includes(f.id) ? ' (going)' : ''}`}
              </option>
            ))}
          </select>
          {willRegister && (
            <span className="muted text-sm">Saving will also mark you as going to this fair.</span>
          )}
        </div>
      ) : (
        <div className="field">
          <label htmlFor="r-app">Application</label>
          <select id="r-app" value={form.applicationId} onChange={set('applicationId')} required>
            <option value="" disabled>
              {applications.length ? 'Choose an application' : 'Add an application first'}
            </option>
            {applications.map((a) => (
              <option key={a.id} value={a.id}>{`${a.company} · ${a.role}`}</option>
            ))}
          </select>
        </div>
      )}
      <div className="field">
        <label htmlFor="r-type">Type</label>
        <select id="r-type" value={form.type} onChange={set('type')}>
          {REMINDER_TYPES.map((t) => <option key={t}>{t}</option>)}
        </select>
      </div>
      <div className="form-grid form-grid--2">
        <div className="field">
          <label htmlFor="r-date">Date</label>
          <input id="r-date" type="date" value={form.date} onChange={set('date')} required />
        </div>
        <div className="field">
          <label htmlFor="r-time">Time</label>
          <input id="r-time" type="time" value={form.time} onChange={set('time')} />
        </div>
      </div>
      {error && <p className="muted" role="alert">{error}</p>}
      <button type="submit" className="btn btn--primary btn--lg" disabled={saving}>
        {saving ? 'Saving…' : 'Save reminder'}
      </button>
    </form>
  );
}

export default function Reminders() {
  const { reminders, toggleReminder, removeReminder, addReminder, applications, fairs, goingFairIds } = useOutletContext();
  const now = new Date();

  const sorted = [...reminders].sort((a, b) => parseDate(a.due) - parseDate(b.due));
  const grouped = GROUPS.map((label) => ({
    label,
    items: sorted.filter((r) => reminderGroup(r.due, now) === label),
  })).filter((g) => g.items.length > 0);

  const confirmRemove = async (r) => {
    const what = r.link ? `${r.title} · ${r.link}` : r.title;
    if (!window.confirm(`Delete the reminder “${what}”?`)) return;
    try {
      await removeReminder(r.id);
    } catch (err) {
      window.alert(err.message);
    }
  };

  const open = reminders.filter((r) => !r.done).length;

  return (
    <>
      <header className="page-header">
        <div className="stack-6">
          <h1 className="page-title">Reminders</h1>
          <p className="muted">Deadlines, interviews and follow-ups, in order.</p>
        </div>
        <span className="header-meta">{open} open</span>
      </header>

      <div className="split">
        <section className="split__main stack-20">
          {grouped.map((g) => (
            <div key={g.label} className="stack-10">
              <h2 className="group-title">{g.label}</h2>
              <ul className="card card--list">
                {g.items.map((r) => {
                  const urgent = g.label === 'Today' && !r.done;
                  return (
                    <li key={r.id} className={`reminder${r.done ? ' reminder--done' : ''}`}>
                      <button
                        type="button"
                        role="checkbox"
                        aria-checked={r.done}
                        aria-label={`Mark “${r.title}” done`}
                        className="check"
                        onClick={() => toggleReminder(r.id).catch((err) => window.alert(err.message))}
                      >
                        {r.done && <Icon name="check" size={16} strokeWidth={3} />}
                      </button>
                      <span className="reminder__text">
                        <span className="reminder__title">{r.title}</span>
                        <span className="muted text-sm">{r.link}</span>
                      </span>
                      <span className={`reminder__when${urgent ? ' text-urgent' : ''}`}>
                        {reminderWhen(r.due, now)}
                      </span>
                      <button
                        type="button"
                        className="icon-btn"
                        aria-label={`Delete reminder “${r.title}”`}
                        onClick={() => confirmRemove(r)}
                      >
                        <Icon name="trash" size={18} />
                      </button>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </section>

        <div className="split__side">
          <NewReminderForm applications={applications} fairs={fairs} goingFairIds={goingFairIds} onSave={addReminder} />
        </div>
      </div>
    </>
  );
}

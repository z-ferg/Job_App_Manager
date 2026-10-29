import { useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import Icon from '../components/Icon.jsx';
import { parseDate, reminderGroup, reminderWhen } from '../utils/dates.js';

const GROUPS = ['Today', 'This week', 'Later'];

function NewReminderForm({ applications, fairs, onSave }) {
  const empty = { title: '', date: new Date().toISOString().slice(0, 10), time: '09:00', link: 'General', email: true, browser: true };
  const [form, setForm] = useState(empty);
  const set = (key) => (e) =>
    setForm({ ...form, [key]: e.target.type === 'checkbox' ? e.target.checked : e.target.value });

  const submit = (e) => {
    e.preventDefault();
    if (!form.title.trim()) return;
    onSave({
      title: form.title.trim(),
      link: form.link,
      due: form.time ? `${form.date}T${form.time}` : form.date,
      notify: { email: form.email, browser: form.browser },
    });
    setForm(empty);
  };

  return (
    <form className="card reminder-form" onSubmit={submit}>
      <h2 className="card__title">New reminder</h2>
      <div className="field">
        <label htmlFor="r-title">What do you need to do?</label>
        <input id="r-title" value={form.title} onChange={set('title')} placeholder="e.g. Follow up with recruiter" required />
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
      <div className="field">
        <label htmlFor="r-link">Link to</label>
        <select id="r-link" value={form.link} onChange={set('link')}>
          <option value="General">Nothing</option>
          <optgroup label="Applications">
            {applications.map((a) => {
              const label = `${a.company} · ${a.role}`;
              return <option key={a.id} value={label}>{label}</option>;
            })}
          </optgroup>
          <optgroup label="Career fairs">
            {fairs.map((f) => <option key={f.id} value={f.name}>{f.name}</option>)}
          </optgroup>
        </select>
      </div>
      <fieldset className="fieldset">
        <legend>Notify me by</legend>
        <label className="checkbox">
          <input type="checkbox" checked={form.email} onChange={set('email')} />
          Email to my VT address
        </label>
        <label className="checkbox">
          <input type="checkbox" checked={form.browser} onChange={set('browser')} />
          Browser notification
        </label>
      </fieldset>
      <button type="submit" className="btn btn--primary btn--lg">Save reminder</button>
    </form>
  );
}

export default function Reminders() {
  const { reminders, toggleReminder, addReminder, applications, fairs } = useOutletContext();
  const now = new Date();

  const sorted = [...reminders].sort((a, b) => parseDate(a.due) - parseDate(b.due));
  const grouped = GROUPS.map((label) => ({
    label,
    items: sorted.filter((r) => reminderGroup(r.due, now) === label),
  })).filter((g) => g.items.length > 0);

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
                        onClick={() => toggleReminder(r.id)}
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
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </section>

        <div className="split__side">
          <NewReminderForm applications={applications} fairs={fairs} onSave={addReminder} />
        </div>
      </div>
    </>
  );
}

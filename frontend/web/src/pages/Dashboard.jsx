import { Link, useOutletContext } from 'react-router-dom';
import Icon from '../components/Icon.jsx';
import StatusBadge from '../components/StatusBadge.jsx';
import CompanyAvatar from '../components/CompanyAvatar.jsx';
import DateBlock from '../components/DateBlock.jsx';
import { getStudent } from '../api/auth.js'
import { formatShort, parseDate, reminderGroup, reminderWhen } from '../utils/dates.js';

function greeting(now) {
  const h = now.getHours();
  if (h < 12) return 'Good morning';
  if (h < 18) return 'Good afternoon';
  return 'Good evening';
}

export default function Dashboard() {
  const { applications, reminders, fairs } = useOutletContext();
  const now = new Date();
  const student = getStudent()

  const firstName = student?.name.split(' ')[0] ?? 'missing_name';
  const major = student?.major ?? 'missing_major';
  const gradYear = student?.grad_year ?? 'missing_year';
  const student_id = student?.student_id ?? 'missing_id';

  const count = (status) => applications.filter((a) => a.status === status).length;
  const stats = [
    { label: 'Total applications', value: applications.length },
    { label: 'Awaiting response', value: count('Applied') },
    { label: 'Interviews scheduled', value: count('Interview') },
    { label: 'Offers', value: count('Offer'), highlight: true },
  ];

  const recent = [...applications]
    .sort((a, b) => parseDate(b.applied) - parseDate(a.applied))
    .slice(0, 5);

  const dueSoon = reminders
    .filter((r) => !r.done)
    .sort((a, b) => parseDate(a.due) - parseDate(b.due))
    .slice(0, 3);

  const upcomingFairs = fairs.filter((f) => parseDate(f.date) >= now).slice(0, 2);

  return (
    <>
      <header className="page-header">
        <div className="stack-6">
          <p className="muted">
            {now.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
          </p>
          <h1 className="page-title">
            {greeting(now)}, {firstName}!
          </h1>
        </div>
        <div className="actions">
          <Link to="/reminders" className="btn btn--secondary">
            <Icon name="bell" size={18} />
            New reminder
          </Link>
          <Link to="/applications?new=1" className="btn btn--accent">
            <Icon name="plus" size={18} strokeWidth={2.4} />
            Add application
          </Link>
        </div>
      </header>

      <div className="stats">
        {stats.map((s) => (
          <div key={s.label} className={`stat${s.highlight ? ' stat--highlight' : ''}`}>
            <span className="stat__label">{s.label}</span>
            <span className="stat__value">{s.value}</span>
          </div>
        ))}
      </div>

      <div className="split">
        <section className="card split__main">
          <div className="card__header">
            <h2 className="card__title">Recent applications</h2>
            <Link to="/applications" className="link-sm">View all</Link>
          </div>
          <div className="table-wrap">
            <table className="table table--compact">
              <thead>
                <tr>
                  <th>Company</th>
                  <th>Role</th>
                  <th>Applied</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {recent.map((app) => (
                  <tr key={app.id}>
                    <td>
                      <span className="company">
                        <CompanyAvatar name={app.company} size="sm" />
                        {app.company}
                      </span>
                    </td>
                    <td className="text-secondary">{app.role}</td>
                    <td className="muted nowrap">{formatShort(app.applied)}</td>
                    <td><StatusBadge status={app.status} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <div className="split__side">
          <section className="card">
            <div className="card__header">
              <h2 className="card__title">Due soon</h2>
              <Link to="/reminders" className="link-sm">All reminders</Link>
            </div>
            {dueSoon.length === 0 && <p className="muted">You’re all caught up.</p>}
            <ul className="due-list">
              {dueSoon.map((r) => {
                const today = reminderGroup(r.due, now) === 'Today';
                return (
                  <li key={r.id} className="due-item">
                    <span className={`dot${today ? ' dot--urgent' : ''}`} />
                    <span className="stack-2">
                      <span className="due-item__title">{r.title}</span>
                      <span className={`due-item__when${today ? ' text-urgent' : ''}`}>
                        {reminderWhen(r.due, now)}
                      </span>
                    </span>
                  </li>
                );
              })}
            </ul>
          </section>

          <section className="card">
            <div className="card__header">
              <h2 className="card__title">Upcoming fairs</h2>
              <Link to="/fairs" className="link-sm">See all</Link>
            </div>
            <ul className="fair-mini-list">
              {upcomingFairs.map((f) => (
                <li key={f.id}>
                  <Link to="/fairs" className="fair-mini">
                    <DateBlock date={f.date} />
                    <span className="stack-2">
                      <span className="fair-mini__name">{f.name}</span>
                      <span className="muted text-sm">{f.where} · {f.time}</span>
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        </div>
      </div>
    </>
  );
}

import { useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import Icon from '../components/Icon.jsx';
import DateBlock from '../components/DateBlock.jsx';
import FilterPills from '../components/FilterPills.jsx';
import { formatWeekday } from '../utils/dates.js';

const TABS = ['All fairs', 'In person', 'Virtual', 'Going'].map((t) => ({ value: t, label: t }));

export default function CareerFairs() {
  const { fairs, goingFairIds, toggleFair } = useOutletContext();
  const [tab, setTab] = useState('All fairs');

  const visible = fairs.filter((f) => {
    if (tab === 'All fairs') return true;
    if (tab === 'Going') return goingFairIds.includes(f.id);
    return f.kind === tab;
  });

  const n = goingFairIds.length;

  return (
    <>
      <header className="page-header">
        <div className="stack-6">
          <h1 className="page-title">Career fairs</h1>
          <p className="muted">
            Upcoming recruiting events on campus and online. Mark the ones you plan to attend to get a reminder.
          </p>
        </div>
        <span className="header-meta">Going to {n} {n === 1 ? 'fair' : 'fairs'}</span>
      </header>

      <FilterPills label="Filter fairs" options={TABS} value={tab} onChange={setTab} />

      <div className="fair-grid">
        {visible.map((f) => {
          const going = goingFairIds.includes(f.id);
          return (
            <article key={f.id} className="card fair">
              <div className="fair__top">
                <DateBlock date={f.date} large />
                <div className="stack-4">
                  <h2 className="fair__name">{f.name}</h2>
                  <span className="muted text-sm">{formatWeekday(f.date)} · {f.time}</span>
                </div>
              </div>

              <div className="fair__meta">
                <span><Icon name="pin" size={16} />{f.where}</span>
                <span>
                  <Icon name="building" size={16} />
                  {f.employers != null ? `${f.employers} employers registered` : 'Employer list coming soon'}
                </span>
              </div>

              <div className="tags">
                {f.tags.map((t) => <span key={t} className="tag">{t}</span>)}
              </div>

              <div className="fair__actions">
                <button
                  type="button"
                  className={`btn ${going ? 'btn--primary' : 'btn--outline'} fair__going`}
                  aria-pressed={going}
                  onClick={() => toggleFair(f)}
                >
                  {going && <Icon name="check" size={18} strokeWidth={2.4} />}
                  {going ? 'Going · reminder set' : 'I’m going'}
                </button>
                <a href="#" className="btn btn--secondary">Employers</a>
              </div>
            </article>
          );
        })}
      </div>
      {visible.length === 0 && <p className="empty">No fairs here yet.</p>}
    </>
  );
}

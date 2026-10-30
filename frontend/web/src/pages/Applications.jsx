import { useState } from 'react';
import { Link, useOutletContext, useSearchParams } from 'react-router-dom';
import Icon from '../components/Icon.jsx';
import StatusBadge from '../components/StatusBadge.jsx';
import CompanyAvatar from '../components/CompanyAvatar.jsx';
import FilterPills from '../components/FilterPills.jsx';
import { STATUSES } from '../data.js';
import { formatShort, parseDate } from '../utils/dates.js';

const EMPTY_FORM = { company: '', role: '', location: '', status: 'Applied', applied: '', next: '' };

function AddApplicationForm({ onSave, onCancel }) {
  const [form, setForm] = useState({ ...EMPTY_FORM, applied: new Date().toISOString().slice(0, 10) });
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setError(null);
    setSaving(true);
    try {
      await onSave(form);
    } catch (err) {
      setError(err.message);
      setSaving(false);
    }
  };

  return (
    <form className="card add-form" onSubmit={submit}>
      <h2 className="card__title">Add application</h2>
      <div className="form-grid">
        <div className="field">
          <label htmlFor="app-company">Company</label>
          <input id="app-company" value={form.company} onChange={set('company')} required />
        </div>
        <div className="field">
          <label htmlFor="app-role">Role</label>
          <input id="app-role" value={form.role} onChange={set('role')} required />
        </div>
        <div className="field">
          <label htmlFor="app-location">Location</label>
          <input id="app-location" value={form.location} onChange={set('location')} placeholder="City, ST or Remote" />
        </div>
        <div className="field">
          <label htmlFor="app-date">Date applied</label>
          <input id="app-date" type="date" value={form.applied} onChange={set('applied')} required />
        </div>
        <div className="field">
          <label htmlFor="app-status">Status</label>
          <select id="app-status" value={form.status} onChange={set('status')}>
            {STATUSES.map((s) => <option key={s}>{s}</option>)}
          </select>
        </div>
        <div className="field">
          <label htmlFor="app-next">Next step</label>
          <input id="app-next" value={form.next} onChange={set('next')} placeholder="e.g. Follow up Nov 5" />
        </div>
      </div>
      {error && <p className="muted" role="alert">{error}</p>}
      <div className="actions">
        <button type="button" className="btn btn--secondary" onClick={onCancel}>Cancel</button>
        <button type="submit" className="btn btn--primary" disabled={saving}>
          {saving ? 'Saving…' : 'Save application'}
        </button>
      </div>
    </form>
  );
}

export default function Applications() {
  const { applications, addApplication, removeApplication } = useOutletContext();
  const [searchParams, setSearchParams] = useSearchParams();
  const [filter, setFilter] = useState('All');
  const [query, setQuery] = useState('');
  const showForm = searchParams.get('new') === '1';

  const openForm = () => setSearchParams({ new: '1' });
  const closeForm = () => setSearchParams({});

  const confirmDelete = async (app) => {
    if (!window.confirm(`Delete your ${app.company} application?`)) return;
    try {
      await removeApplication(app.id);
    } catch (err) {
      // e.g. a 409 when interviews or reminders still point at this application
      window.alert(err.message);
    }
  };

  const filterOptions = ['All', ...STATUSES].map((s) => ({
    value: s,
    label: s,
    count: s === 'All' ? applications.length : applications.filter((a) => a.status === s).length,
  }));

  const q = query.trim().toLowerCase();
  const visible = applications
    .filter((a) => filter === 'All' || a.status === filter)
    .filter((a) => !q || `${a.company} ${a.role}`.toLowerCase().includes(q))
    .sort((a, b) => (b.applied ? parseDate(b.applied) : 0) - (a.applied ? parseDate(a.applied) : 0));

  return (
    <>
      <header className="page-header">
        <div className="stack-6">
          <h1 className="page-title">Applications</h1>
          <p className="muted">Every role you have applied to, and what happens next.</p>
        </div>
        <button type="button" className="btn btn--accent" onClick={openForm}>
          <Icon name="plus" size={18} strokeWidth={2.4} />
          Add application
        </button>
      </header>

      {showForm && (
        <AddApplicationForm
          onSave={async (app) => {
            await addApplication(app);
            closeForm();
          }}
          onCancel={closeForm}
        />
      )}

      <div className="toolbar">
        <FilterPills label="Filter by status" options={filterOptions} value={filter} onChange={setFilter} />
        <div className="search">
          <label htmlFor="search" className="sr-only">Search applications</label>
          <Icon name="search" size={18} className="search__icon" />
          <input
            id="search"
            type="search"
            placeholder="Search company or role"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
      </div>

      <section className="card card--table">
        <div className="table-wrap">
          <table className="table table--wide">
            <thead>
              <tr>
                <th>Company</th>
                <th>Role</th>
                <th>Location</th>
                <th>Applied</th>
                <th>Status</th>
                <th>Next step</th>
                <th><span className="sr-only">Actions</span></th>
              </tr>
            </thead>
            <tbody>
              {visible.map((app) => (
                <tr key={app.id}>
                  <td>
                    <span className="company nowrap">
                      <CompanyAvatar name={app.company} size="sm" />
                      {app.company}
                    </span>
                  </td>
                  <td className="text-secondary">{app.role}</td>
                  <td className="muted nowrap">{app.location}</td>
                  <td className="muted nowrap">{app.applied ? formatShort(app.applied) : '—'}</td>
                  <td><StatusBadge status={app.status} /></td>
                  <td className="text-secondary nowrap">{app.next}</td>
                  <td className="align-right nowrap">
                    <Link to="/reminders" className="icon-btn" aria-label={`Set a reminder for ${app.company}`}>
                      <Icon name="bell" size={18} />
                    </Link>
                    <button
                      type="button"
                      className="icon-btn"
                      aria-label={`Delete ${app.company} application`}
                      onClick={() => confirmDelete(app)}
                    >
                      <Icon name="trash" size={18} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {visible.length === 0 && <p className="empty">No applications match.</p>}
      </section>
    </>
  );
}

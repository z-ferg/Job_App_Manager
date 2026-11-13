import { useEffect, useState } from 'react';
import { getStudent } from '../api/auth.js';
import { createApp, deleteApp, getApps, updateApp } from '../api/application.js';
import { createReminder, deleteReminder, getReminders, updateReminder } from '../api/reminders.js';
import { createRegistration, deleteRegistration, getEvents, getRegistrations } from '../api/fairs.js';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar.jsx';

// Map an API application onto the { id, company, role, location, status, applied, next }
// shape the pages (and the Add application form) use.
const toUiApplication = (a) => ({
  id: a.application_id,
  company: a.company_name,
  role: a.role_title,
  location: '',
  status: a.status,
  applied: a.date_applied,
  next: a.notes ?? 'No update yet',
});

// Map an API reminder onto the { id, title, link, due, done } shape the pages use.
// Timestamps come back as 'YYYY-MM-DDTHH:mm:ss'. Midnight means "no time given",
// so drop it and let the pages show just the date.
const toUiDate = (ts) => (ts?.endsWith('T00:00:00') ? ts.slice(0, 10) : ts);

// The create/update endpoints don't return target_label, so callers can pass a fallback.
const toUiReminder = (r, fallbackLabel = '') => ({
  id: r.reminder_id,
  applicationId: r.application_id,
  registrationId: r.registration_id,
  title: r.reminder_type,
  link: r.target_label ?? fallbackLabel,
  due: toUiDate(r.reminder_date),
  done: r.completed,
});

// Map a career_fair_event row onto the { id, date, name, time, where, tags, kind } shape
// the fair pages use. The table has no time range, employer count or tags, so those are derived.
const toUiFair = (e) => {
  const virtual = /virtual|online|zoom/i.test(`${e.location ?? ''} ${e.event_name}`);
  const kind = virtual ? 'Virtual' : 'In person';
  return {
    id: e.event_id,
    date: toUiDate(e.event_date),
    name: e.event_name,
    time: e.description ?? 'Time TBA',
    where: e.location ?? 'Location TBA',
    employers: null,
    tags: [kind],
    kind,
  };
};

// Holds the signed-in student's data and shares it with every page through
// the router outlet context. Swap the useState seeds for API calls.
export default function AppLayout() {
  const student = getStudent();
  const [applications, setApplications] = useState([]);
  const [reminders, setReminders] = useState([]);
  const [fairs, setFairs] = useState([]);
  // { id: registration_id, eventId } for each fair the student is going to.
  const [registrations, setRegistrations] = useState([]);
  const goingFairIds = registrations.map((r) => r.eventId);

  useEffect(() => {
    if (!student) return;
    getApps(student.student_id)
      .then((rows) => setApplications(rows.map(toUiApplication)))
      .catch((err) => console.error(err));
    getReminders(student.student_id)
      .then((rows) => setReminders(rows.map((r) => toUiReminder(r))))
      .catch((err) => console.error(err));
    getRegistrations(student.student_id)
      .then((rows) => setRegistrations(rows.map((r) => ({ id: r.registration_id, eventId: r.event_id }))))
      .catch((err) => console.error(err));
  }, [student?.student_id]);

  useEffect(() => {
    getEvents()
      // Events without a date can't be shown on a calendar card, so skip them.
      .then((rows) => setFairs(rows.filter((e) => e.event_date).map(toUiFair)))
      .catch((err) => console.error(err));
  }, [student?.student_id]);

  // Saves the form's application to the backend, then shows the saved row.
  // location has no column in the database, so it isn't sent.
  const addApplication = async (app) => {
    const saved = await createApp({
      student_id: student.student_id,
      company_name: app.company,
      role_title: app.role,
      status: app.status,
      date_applied: app.applied || null,
      notes: app.next || null,
    });
    setApplications((list) => [toUiApplication(saved), ...list]);
  };

  // Saves changes (in the UI shape, e.g. { status: 'Accepted' }) and swaps in the saved row.
  const updateApplication = async (id, changes) => {
    const fields = {};
    if ('company' in changes) fields.company_name = changes.company;
    if ('role' in changes) fields.role_title = changes.role;
    if ('status' in changes) fields.status = changes.status;
    if ('applied' in changes) fields.date_applied = changes.applied || null;
    if ('next' in changes) fields.notes = changes.next || null;

    // The database requires a date_applied for any status other than 'Not Applied',
    // so moving a never-applied application forward stamps it with today's date.
    const current = applications.find((a) => a.id === id);
    if (fields.status && fields.status !== 'Not Applied' && !current?.applied && !fields.date_applied) {
      fields.date_applied = new Date().toISOString().slice(0, 10);
    }

    const saved = await updateApp(id, fields);
    setApplications((list) => list.map((a) => (a.id === id ? toUiApplication(saved) : a)));
  };

  const removeApplication = async (id) => {
    await deleteApp(id);
    setApplications((list) => list.filter((a) => a.id !== id));
  };

  // Registers the student for a fair (if they aren't already) and returns the registration.
  const ensureRegistration = async (eventId) => {
    const existing = registrations.find((r) => r.eventId === eventId);
    if (existing) return existing;
    const saved = await createRegistration(student.student_id, eventId);
    const reg = { id: saved.registration_id, eventId };
    setRegistrations((list) => [...list, reg]);
    return reg;
  };

  // Saves a reminder linked to either an application or a career fair:
  // { applicationId, type, due } or { eventId, type, due }.
  // A reminder can only point at a fair through a registration, so linking one to a
  // fair the student isn't going to yet also marks them as going.
  const addReminder = async ({ applicationId, eventId, type, due }) => {
    const reminder_date = due.includes('T') ? due : `${due}T00:00`;
    let target;
    let label = '';
    if (eventId != null) {
      const reg = await ensureRegistration(eventId);
      target = { registration_id: reg.id };
      label = fairs.find((f) => f.id === eventId)?.name ?? '';
    } else {
      target = { application_id: applicationId };
      const app = applications.find((a) => a.id === applicationId);
      label = app ? `${app.company} · ${app.role}` : '';
    }
    const saved = await createReminder({ ...target, reminder_type: type, reminder_date });
    setReminders((list) => [...list, toUiReminder(saved, label)]);
  };

  const toggleReminder = async (id) => {
    const current = reminders.find((r) => r.id === id);
    if (!current) return;
    await updateReminder(id, { completed: !current.done });
    setReminders((list) => list.map((r) => (r.id === id ? { ...r, done: !r.done } : r)));
  };

  const removeReminder = async (id) => {
    await deleteReminder(id);
    setReminders((list) => list.filter((r) => r.id !== id));
  };

  // Reminders that point at the student's registration for this fair.
  const remindersForFair = (fairId) => {
    const reg = registrations.find((r) => r.eventId === fairId);
    return reg ? reminders.filter((r) => r.registrationId === reg.id) : [];
  };

  // "I'm going" registers for the fair and adds an Event reminder on the fair's date.
  // Un-going deletes the fair's reminders first, since they'd block deleting the registration.
  const toggleFair = async (fair) => {
    const reg = registrations.find((r) => r.eventId === fair.id);
    if (!reg) {
      await addReminder({ eventId: fair.id, type: 'Event Application', due: fair.date });
      return;
    }
    const linked = remindersForFair(fair.id);
    for (const r of linked) await deleteReminder(r.id);
    await deleteRegistration(reg.id);
    const linkedIds = new Set(linked.map((r) => r.id));
    setReminders((list) => list.filter((r) => !linkedIds.has(r.id)));
    setRegistrations((list) => list.filter((r) => r.id !== reg.id));
  };

  const context = {
    applications,
    addApplication,
    updateApplication,
    removeApplication,
    reminders,
    addReminder,
    toggleReminder,
    removeReminder,
    fairs,
    goingFairIds,
    toggleFair,
    remindersForFair,
  };

  return (
    <div className="shell">
      <Sidebar />
      <main className="main">
        <div className="main__inner">
          <Outlet context={context} />
        </div>
      </main>
    </div>
  );
}

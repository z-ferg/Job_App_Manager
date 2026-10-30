import { useEffect, useState } from 'react';
import { getStudent } from '../api/auth.js';
import { createApp, deleteApp, getApps } from '../api/application.js';
import { getReminders } from '../api/reminders.js';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar.jsx';
import { sampleFairs } from '../data.js';

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
const toUiReminder = (r) => ({
  id: r.reminder_id,
  title: r.reminder_type,
  link: r.target_label ?? '',
  due: r.reminder_date,
  done: r.completed,
});

// Holds the signed-in student's data and shares it with every page through
// the router outlet context. Swap the useState seeds for API calls.
export default function AppLayout() {
  const student = getStudent();
  const [applications, setApplications] = useState([]);
  const [reminders, setReminders] = useState([]);
  const [goingFairIds, setGoingFairIds] = useState(['eng']);

  useEffect(() => {
    if (!student) return;
    getApps(student.student_id)
      .then((rows) => setApplications(rows.map(toUiApplication)))
      .catch((err) => console.error(err));
    getReminders(student.student_id)
      .then((rows) => setReminders(rows.map(toUiReminder)))
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

  const removeApplication = async (id) => {
    await deleteApp(id);
    setApplications((list) => list.filter((a) => a.id !== id));
  };

  const addReminder = (reminder) =>
    setReminders((list) => [...list, { ...reminder, id: crypto.randomUUID(), done: false }]);

  const toggleReminder = (id) =>
    setReminders((list) => list.map((r) => (r.id === id ? { ...r, done: !r.done } : r)));

  const toggleFair = (fair) => {
    const going = goingFairIds.includes(fair.id);
    setGoingFairIds((ids) => (going ? ids.filter((id) => id !== fair.id) : [...ids, fair.id]));
    if (!going) {
      addReminder({ title: `Attend ${fair.name}`, link: fair.where, due: fair.date });
    }
  };

  const context = {
    applications,
    addApplication,
    removeApplication,
    reminders,
    addReminder,
    toggleReminder,
    fairs: sampleFairs,
    goingFairIds,
    toggleFair,
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

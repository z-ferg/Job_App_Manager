import { useEffect, useState } from 'react';
import { getStudent } from '../api/auth.js';
import { getApps } from '../api/application.js';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar.jsx';
import { sampleApplications, sampleFairs, sampleReminders } from '../data.js';

// Holds the signed-in student's data and shares it with every page through
// the router outlet context. Swap the useState seeds for API calls.
export default function AppLayout() {
  const student = getStudent();
  const [applications, setApplications] = useState([]);
  const [reminders, setReminders] = useState(sampleReminders);
  const [goingFairIds, setGoingFairIds] = useState(['eng']);

  useEffect(() => {
    if (!student) return;
    getApps(student.student_id)
      .then(setApplications)
      .catch((err) => console.error(err));
  }, [student?.student_id]);

  const addApplication = (app) =>
    setApplications((list) => [{ ...app, id: crypto.randomUUID() }, ...list]);

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

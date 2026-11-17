import { request } from './client.js';

// Must match the backend's ReminderType enum (and the Postgres reminder_type_t type).
export const REMINDER_TYPES = ['Follow-up', 'Interview Prep', 'Deadline', 'Event Application'];

export async function getReminders(student_id) {
    return request(`/reminders?student_id=${student_id}&limit=100`);
}

// Creates a reminder and returns the saved row. Needs exactly one of
// application_id, interview_id or registration_id.
export async function createReminder(fields) {
    return request('/reminders', {
        method: 'POST',
        body: JSON.stringify(fields),
    });
}

// Partially updates a reminder (reminder_date, reminder_type, completed).
export async function updateReminder(reminder_id, fields) {
    return request(`/reminders/${reminder_id}`, {
        method: 'PATCH',
        body: JSON.stringify(fields),
    });
}

export async function deleteReminder(reminder_id) {
    return request(`/reminders/${reminder_id}`, { method: 'DELETE' });
}

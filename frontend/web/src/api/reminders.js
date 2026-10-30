import { request } from './client.js';

export async function getReminders(student_id) {
    return request(`/reminders?student_id=${student_id}`);
}
import { request } from './client.js';

// Career fair events (career_fair_event table).
export async function getEvents() {
    return request('/events?limit=100');
}

// The student's registrations, i.e. the fairs they're going to.
export async function getRegistrations(student_id) {
    return request(`/event-registrations?student_id=${student_id}&limit=100`);
}

export async function createRegistration(student_id, event_id) {
    return request('/event-registrations', {
        method: 'POST',
        body: JSON.stringify({ student_id, event_id }),
    });
}

export async function deleteRegistration(registration_id) {
    return request(`/event-registrations/${registration_id}`, { method: 'DELETE' });
}

import { request } from './client.js';

export async function getApps(student_id) {
    return request(`/applications?student_id=${student_id}&limit=100`);
}

// Creates an application and returns the saved row (with its application_id).
export async function createApp(fields) {
    return request('/applications', {
        method: 'POST',
        body: JSON.stringify(fields),
    });
}

// Partially updates an application (only the fields given) and returns the saved row.
export async function updateApp(application_id, fields) {
    return request(`/applications/${application_id}`, {
        method: 'PATCH',
        body: JSON.stringify(fields),
    });
}

export async function deleteApp(application_id) {
    return request(`/applications/${application_id}`, { method: 'DELETE' });
}

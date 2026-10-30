import { request } from './client.js';

export async function getApps(student_id) {
    return request(`/applications?student_id=${student_id}`);
}

// Creates an application and returns the saved row (with its application_id).
export async function createApp(fields) {
    return request('/applications', {
        method: 'POST',
        body: JSON.stringify(fields),
    });
}

export async function deleteApp(application_id) {
    return request(`/applications/${application_id}`, { method: 'DELETE' });
}

import { request } from './client.js';

export async function getApps(student_id) {
    return request(`/applications?student_id=${student_id}`);
}
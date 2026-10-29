import { request } from './client.js';

// The backend checks the password against password_hash; the hash never reaches the browser.
export async function login(email, password) {
  const student = await request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  console.log(JSON.stringify(student));
  localStorage.setItem('student', JSON.stringify(student));
  return student;
}

export function logout() {
  localStorage.removeItem('student');
}

export function getStudent() {
  const raw = localStorage.getItem('student')
  return raw ? JSON.parse(raw) : null;
}

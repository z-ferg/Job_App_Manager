import { request } from './client.js';

// The backend checks the password against password_hash; the hash never reaches the browser.
export async function login(email, password) {
  const student = await request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });

  localStorage.setItem('student', JSON.stringify(student));
  return student;
}

export function logout() {
  localStorage.removeItem('student');
}

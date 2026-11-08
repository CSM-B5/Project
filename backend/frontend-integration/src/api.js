// Copy to: src/api.js
// One place for every call to the FastAPI backend.
import axios from 'axios';

export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({ baseURL: API_URL });

// Send the login token with every request
api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// If the token expired / became invalid, go back to the login page
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const isLoginCall = (err.config?.url || '').includes('/api/auth/login');
    if (err.response?.status === 401 && !isLoginCall && sessionStorage.getItem('token')) {
      sessionStorage.removeItem('token');
      sessionStorage.removeItem('user');
      window.location.assign('/login');
    }
    return Promise.reject(err);
  }
);

/** Turns any axios error into a readable message. */
export function errorMessage(err) {
  const detail = err?.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) return detail.map((d) => d.msg).join('; ');
  if (err?.code === 'ERR_NETWORK') return 'Cannot reach the server. Is the backend running?';
  return err?.message || 'Something went wrong.';
}

// ---- auth ----
export const loginRequest = (email, password, role) =>
  api.post('/api/auth/login', { email, password, role }).then((r) => r.data);

// ---- dashboards ----
export const getStats = () => api.get('/api/stats/dashboard').then((r) => r.data);

// ---- studies (MRI scans) ----
export const getStudies = (reportStatus) =>
  api.get('/api/studies', { params: reportStatus ? { reportStatus } : {} }).then((r) => r.data);
export const getStudy = (id) => api.get(`/api/studies/${id}`).then((r) => r.data);
export const createStudy = (formData) => api.post('/api/studies', formData).then((r) => r.data);
export const approveReport = (id, summary) =>
  api.post(`/api/studies/${id}/report/approve`, summary ? { summary } : {}).then((r) => r.data);
export const getPatients = () => api.get('/api/patients').then((r) => r.data);

// ---- chat ----
export const sendChat = (message, studyId, history) =>
  api.post('/api/chat', { message, studyId, history }).then((r) => r.data);

// ---- admin ----
export const adminListUsers = (role) =>
  api.get('/api/admin/users', { params: role ? { role } : {} }).then((r) => r.data);
export const adminCreateUser = (body) => api.post('/api/admin/users', body).then((r) => r.data);
export const adminUpdateUser = (id, body) => api.patch(`/api/admin/users/${id}`, body).then((r) => r.data);

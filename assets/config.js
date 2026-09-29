const AUTH0_DOMAIN = window.AUTH0_DOMAIN || 'YOUR_TENANT.us.auth0.com';
const AUTH0_CLIENT_ID = window.AUTH0_CLIENT_ID || 'YOUR_AUTH0_CLIENT_ID';
const AUTH0_AUDIENCE = window.AUTH0_AUDIENCE || 'https://ag2-platform-api';
const AUTH0_REDIRECT_URI = window.location.origin + '/login.html';
const API_BASE_URL = window.location.hostname === 'localhost' ? 'http://localhost:8000' : window.location.origin;

window.authToken = localStorage.getItem('authToken');
window.setAuthToken = (token) => {
  window.authToken = token || null;
  if (token) localStorage.setItem('authToken', token);
  else localStorage.removeItem('authToken');
};

window.apiClient = {
  async request(method, path, data) {
    const options = { method, headers: { 'Content-Type': 'application/json' } };
    if (window.authToken) options.headers.Authorization = `Bearer ${window.authToken}`;
    if (data) options.body = JSON.stringify(data);
    const response = await fetch(API_BASE_URL + path, options);
    if (response.status === 401) {
      window.setAuthToken(null);
      window.location.href = '/login.html';
      return null;
    }
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  },
  get(path) { return this.request('GET', path); },
  post(path, data) { return this.request('POST', path, data); }
};

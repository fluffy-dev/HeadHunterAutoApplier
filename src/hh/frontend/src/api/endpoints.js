import api from './axios';

/**
 * Log in to the application.
 * @param {string} username - User login.
 * @param {string} password - User password.
 * @returns {Promise<Object>} Token data.
 */
export const login = (username, password) => {
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);
  return api.post('/auth/token', formData);
};

/**
 * Register a new user.
 * @param {Object} userData - payload with name, login, email, password.
 */
export const register = (userData) => api.post('/users/', userData);

/**
 * Get current user profile.
 */
export const getMe = () => api.get('/users/me');

/**
 * Get the HH OAuth login URL.
 */
export const getHHLoginUrl = () => api.get('/auth/hh/login-url');

/**
 * Send HH auth code to backend.
 * @param {string} code - OAuth code from HH.
 */
export const sendHHCode = (code) => api.post(`/auth/hh/callback?code=${code}`);

/**
 * Get user vacancy search settings.
 */
export const getSettings = () => api.get('/vacancies/settings');

/**
 * Update user vacancy search settings.
 * @param {Object} settings - Settings DTO.
 */
export const updateSettings = (settings) => api.put('/vacancies/settings', settings);

/**
 * Get user's resumes from HH.
 */
export const getResumes = () => api.get('/vacancies/resumes');

/**
 * Manually trigger the bot/worker task.
 */
export const startBot = () => api.post('/vacancies/bot/start');
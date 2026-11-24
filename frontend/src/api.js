// Central API configuration for RINGTRACE AI Frontend
// If the app is accessed on Vite dev server (port 5173), direct requests to FastAPI backend on port 8000.
// If accessed directly on FastAPI (port 8000) or production, use relative paths.
export const API_BASE =
  typeof window !== 'undefined' && (window.location.port === '5173' || window.location.port === '3000')
    ? `${window.location.protocol}//${window.location.hostname}:8000`
    : '';

export const apiFetch = (url, options) => {
  const fullUrl = url.startsWith('http') ? url : `${API_BASE}${url}`;
  return fetch(fullUrl, options);
};

export default apiFetch;

import axios from 'axios';

// Create an Axios instance with a base URL.
// This prevents us from repeating 'http://localhost:8000' in every request.
const api = axios.create({
    baseURL: 'http://localhost:8000',
    withCredentials: true // Important for sending/receiving HttpOnly cookies
});

// Add a request interceptor to inject the token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('authToken');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Add a response interceptor to handle 401s (Token Expiry)
api.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error) => {
        const originalRequest = error.config;

        // If 401 and not already retrying
        if (error.response?.status === 401 && !originalRequest._retry && !originalRequest.url.includes('/token')) {
            originalRequest._retry = true;
            try {
                // Call refresh endpoint (cookies sent automatically)
                const res = await api.post('/refresh');
                const newAccessToken = res.data.access_token;

                // Update local storage
                localStorage.setItem('authToken', newAccessToken);

                // Update header for original request
                originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;

                // Retry original request
                return api(originalRequest);
            } catch (refreshError) {
                console.error("Refresh token failed", refreshError);
                // Clear token and redirect to login if refresh fails
                localStorage.removeItem('authToken');
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }
        return Promise.reject(error);
    }
);

// Auth Endpoints
export const login = (email, password) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    return api.post('/token', formData);
};
export const register = (email, password) => api.post('/register', { email, password });
export const logout = () => api.post('/logout');

// Export functions for each API endpoint.
// This keeps all API calls in one place, making it easier to manage and refactor.

// Alerts
export const getAlerts = () => api.get('/alerts');
export const createAlert = (data) => api.post('/alerts', data);
export const deleteAlert = (id) => api.delete(`/alerts/${id}`);

export const getStocks = () => api.get('/market/stocks');
export const getStock = (code) => api.get(`/market/stocks/${code}`);
export const triggerScrape = () => api.get('/market/scrape');
export const getTransactions = (params) => api.get('/portfolio/transactions', { params });
export const createTransaction = (data) => api.post('/portfolio/transactions', data);
export const getHoldings = () => api.get('/portfolio/'); // Root of portfolio router
export const getWatchlist = () => api.get('/portfolio/watchlist');
export const addToWatchlist = (stockId) => api.post('/portfolio/watchlist', { stock_id: stockId });

export default api;

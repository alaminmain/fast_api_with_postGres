import axios from 'axios';

// Create an Axios instance with a base URL.
// This prevents us from repeating 'http://localhost:8000' in every request.
const api = axios.create({
    baseURL: 'http://localhost:8000',
});

// Export functions for each API endpoint.
// This keeps all API calls in one place, making it easier to manage and refactor.

export const getStocks = () => api.get('/market/stocks');
export const getStock = (code) => api.get(`/market/stocks/${code}`);
export const triggerScrape = () => api.get('/market/scrape');
export const getTransactions = () => api.get('/portfolio/transactions');
export const createTransaction = (data) => api.post('/portfolio/transactions', data);
export const getHoldings = () => api.get('/portfolio/holdings');
export const getWatchlist = () => api.get('/portfolio/watchlist');
export const addToWatchlist = (stockId) => api.post('/portfolio/watchlist', { stock_id: stockId });

export default api;

import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Market from './pages/Market';
import StockDetail from './pages/StockDetail';
import Portfolio from './pages/Portfolio';

function App() {
  return (
    // BrowserRouter enables client-side routing.
    <BrowserRouter>
      <Routes>
        {/* Layout component wraps all nested routes, providing the sidebar/header */}
        <Route path="/" element={<Layout />}>
          {/* index route renders on the base path '/' */}
          <Route index element={<Dashboard />} />
          <Route path="market" element={<Market />} />
          {/* :code is a URL parameter (e.g., /market/GP) */}
          <Route path="market/:code" element={<StockDetail />} />
          <Route path="portfolio" element={<Portfolio />} />
          <Route path="alerts" element={<div className="p-4">Alerts Coming Soon</div>} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;

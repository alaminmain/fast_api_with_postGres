import React, { useEffect, useState } from 'react';
import { getHoldings, getWatchlist, triggerScrape } from '../api';
import { ArrowUp, ArrowDown, RefreshCw } from 'lucide-react';
import { Link } from 'react-router-dom';

const Dashboard = () => {
    // State variables to store data fetched from API.
    const [holdings, setHoldings] = useState([]);
    const [watchlist, setWatchlist] = useState([]);
    const [loading, setLoading] = useState(true);
    const [scraping, setScraping] = useState(false);

    // Function to fetch initial data.
    const fetchData = async () => {
        try {
            // Promise.all runs both requests in parallel.
            const [hRes, wRes] = await Promise.all([getHoldings(), getWatchlist()]);
            setHoldings(hRes.data);
            setWatchlist(wRes.data);
        } catch (error) {
            console.error("Error fetching dashboard data", error);
        } finally {
            setLoading(false);
        }
    };

    // useEffect with empty dependency array [] runs once when component mounts.
    useEffect(() => {
        fetchData();
    }, []);

    // Handler for manual refresh button.
    const handleRefresh = async () => {
        setScraping(true);
        try {
            await triggerScrape();
            // Wait a bit for scrape to potentially finish or just reload data
            setTimeout(fetchData, 2000);
        } catch (e) {
            console.error(e);
        } finally {
            setScraping(false);
        }
    };

    // Calculate portfolio summary stats using reduce.
    const totalValue = holdings.reduce((acc, curr) => acc + curr.current_value, 0);
    const totalCost = holdings.reduce((acc, curr) => acc + (curr.average_cost * curr.quantity), 0);
    const totalGain = totalValue - totalCost;
    const totalGainPercent = totalCost > 0 ? (totalGain / totalCost) * 100 : 0;

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-800">Dashboard</h2>
                <button
                    onClick={handleRefresh}
                    disabled={scraping}
                    className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
                >
                    {/* Conditional class for spinning animation */}
                    <RefreshCw size={18} className={scraping ? "animate-spin" : ""} />
                    <span>{scraping ? "Updating..." : "Refresh Market"}</span>
                </button>
            </div>

            {/* Portfolio Summary Card */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
                <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">Total Portfolio Value</h3>
                <div className="mt-2 flex items-baseline space-x-4">
                    <span className="text-4xl font-bold text-gray-900">৳{totalValue.toLocaleString()}</span>
                    {/* Conditional color based on gain/loss */}
                    <div className={`flex items-center text-sm font-medium ${totalGain >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {totalGain >= 0 ? <ArrowUp size={16} /> : <ArrowDown size={16} />}
                        <span>{Math.abs(totalGainPercent).toFixed(2)}% (৳{Math.abs(totalGain).toLocaleString()})</span>
                    </div>
                </div>
            </div>

            {/* Watchlist Grid */}
            <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Watchlist</h3>
                {/* Grid layout: 1 col on mobile, 2 on tablet, 3 on desktop */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {watchlist.map((item) => {
                        const stock = item.stock;
                        const market = stock.market_data || {};
                        const isUp = market.change >= 0;

                        return (
                            <Link key={stock.id} to={`/market/${stock.trading_code}`} className="block">
                                <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <h4 className="font-bold text-gray-900">{stock.trading_code}</h4>
                                            <p className="text-xs text-gray-500">{stock.name}</p>
                                        </div>
                                        <div className={`text-right ${isUp ? 'text-green-600' : 'text-red-600'}`}>
                                            <p className="font-bold text-lg">৳{market.ltp}</p>
                                            <p className="text-xs font-medium flex items-center justify-end">
                                                {isUp ? '+' : ''}{market.change} ({market.change && market.ltp ? ((market.change / (market.ltp - market.change)) * 100).toFixed(2) : 0}%)
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </Link>
                        );
                    })}
                    {watchlist.length === 0 && (
                        <div className="col-span-full text-center py-8 text-gray-500 bg-white rounded-xl border border-dashed">
                            No stocks in watchlist. Go to Market to add some.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;

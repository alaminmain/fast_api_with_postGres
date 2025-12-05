import React, { useEffect, useState } from 'react';
import { getStocks, addToWatchlist } from '../api';
import { Search, Star } from 'lucide-react';
import { Link } from 'react-router-dom';

const Market = () => {
    const [stocks, setStocks] = useState([]);
    const [filter, setFilter] = useState("");

    useEffect(() => {
        getStocks().then(res => setStocks(res.data));
    }, []);

    // Filter stocks based on search input (case-insensitive).
    const filteredStocks = stocks.filter(s =>
        s.trading_code.toLowerCase().includes(filter.toLowerCase()) ||
        s.name.toLowerCase().includes(filter.toLowerCase())
    );

    const handleWatch = async (e, id) => {
        // Prevent the click from propagating to the row (which would navigate to detail page).
        e.preventDefault();
        e.stopPropagation();
        try {
            await addToWatchlist(id);
            alert("Added to watchlist");
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <h2 className="text-2xl font-bold text-gray-800">Market</h2>
                {/* Search Bar */}
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                    <input
                        type="text"
                        placeholder="Search stocks..."
                        className="pl-10 pr-4 py-2 border rounded-lg w-full md:w-64 focus:ring-2 focus:ring-indigo-500 outline-none"
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                    />
                </div>
            </div>

            {/* Stock Table */}
            <div className="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100">
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm text-gray-600">
                        <thead className="bg-gray-50 text-xs uppercase font-semibold text-gray-500">
                            <tr>
                                <th className="px-6 py-4">Trading Code</th>
                                <th className="px-6 py-4 text-right">LTP</th>
                                <th className="px-6 py-4 text-right">High</th>
                                <th className="px-6 py-4 text-right">Low</th>
                                <th className="px-6 py-4 text-right">Change</th>
                                <th className="px-6 py-4 text-center">Action</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {filteredStocks.map((stock) => {
                                const market = stock.market_data || {};
                                const isUp = market.change >= 0;
                                return (
                                    <tr key={stock.id} className="hover:bg-gray-50 transition-colors">
                                        <td className="px-6 py-4 font-medium text-gray-900">
                                            <Link to={`/market/${stock.trading_code}`} className="hover:text-indigo-600">
                                                {stock.trading_code}
                                            </Link>
                                            <div className="text-xs text-gray-400 font-normal">{stock.name}</div>
                                        </td>
                                        <td className="px-6 py-4 text-right font-medium">৳{market.ltp}</td>
                                        <td className="px-6 py-4 text-right">৳{market.high}</td>
                                        <td className="px-6 py-4 text-right">৳{market.low}</td>
                                        <td className={`px-6 py-4 text-right font-medium ${isUp ? 'text-green-600' : 'text-red-600'}`}>
                                            {market.change}
                                        </td>
                                        <td className="px-6 py-4 text-center">
                                            <button onClick={(e) => handleWatch(e, stock.id)} className="text-gray-400 hover:text-yellow-500">
                                                <Star size={18} />
                                            </button>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default Market;

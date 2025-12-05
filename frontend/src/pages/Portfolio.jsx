import React, { useEffect, useState } from 'react';
import { getHoldings } from '../api';

const Portfolio = () => {
    const [holdings, setHoldings] = useState([]);

    useEffect(() => {
        getHoldings().then(res => setHoldings(res.data));
    }, []);

    return (
        <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-800">Portfolio</h2>

            <div className="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100">
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm text-gray-600">
                        <thead className="bg-gray-50 text-xs uppercase font-semibold text-gray-500">
                            <tr>
                                <th className="px-6 py-4">Stock</th>
                                <th className="px-6 py-4 text-right">Quantity</th>
                                <th className="px-6 py-4 text-right">Avg Cost</th>
                                <th className="px-6 py-4 text-right">Current Price</th>
                                <th className="px-6 py-4 text-right">Current Value</th>
                                <th className="px-6 py-4 text-right">Gain/Loss</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {holdings.map((item, idx) => {
                                const isGain = item.gain_loss >= 0;
                                return (
                                    <tr key={idx} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 font-medium text-gray-900">{item.stock.trading_code}</td>
                                        <td className="px-6 py-4 text-right">{item.quantity}</td>
                                        <td className="px-6 py-4 text-right">৳{item.average_cost.toFixed(2)}</td>
                                        <td className="px-6 py-4 text-right">৳{item.stock.market_data?.ltp || 0}</td>
                                        <td className="px-6 py-4 text-right font-medium">৳{item.current_value.toFixed(2)}</td>
                                        {/* Conditional styling for Gain (Green) / Loss (Red) */}
                                        <td className={`px-6 py-4 text-right font-medium ${isGain ? 'text-green-600' : 'text-red-600'}`}>
                                            {isGain ? '+' : ''}{item.gain_loss.toFixed(2)} ({item.gain_loss_percent.toFixed(2)}%)
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

export default Portfolio;

import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getStock, createTransaction } from '../api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const StockDetail = () => {
    // useParams hook extracts the 'code' parameter from the URL (e.g., /market/GP -> code="GP").
    const { code } = useParams();
    const [stock, setStock] = useState(null);
    const [buyQuantity, setBuyQuantity] = useState('');
    const [buyPrice, setBuyPrice] = useState('');

    useEffect(() => {
        // Fetch stock details when 'code' changes.
        getStock(code).then(res => {
            setStock(res.data);
            if (res.data.market_data) {
                setBuyPrice(res.data.market_data.ltp); // Pre-fill price with current LTP
            }
        });
    }, [code]);

    const handleTransaction = async (type) => {
        if (!buyQuantity || !buyPrice) return;
        try {
            await createTransaction({
                stock_id: stock.id,
                type: type,
                quantity: parseFloat(buyQuantity),
                price: parseFloat(buyPrice)
            });
            alert(`${type} recorded successfully!`);
            setBuyQuantity('');
        } catch (e) {
            console.error(e);
            alert("Error recording transaction");
        }
    };

    if (!stock) return <div>Loading...</div>;

    const market = stock.market_data || {};

    // Mock data for chart if no history (Recharts expects an array of objects).
    const chartData = [
        { name: 'Open', value: market.open || market.ltp - 2 },
        { name: 'Low', value: market.low || market.ltp - 5 },
        { name: 'High', value: market.high || market.ltp + 5 },
        { name: 'Close', value: market.close || market.ltp },
    ];
    // Ideally we fetch historical data here

    return (
        <div className="space-y-6">
            {/* Stock Header Info */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                <div className="flex justify-between items-start">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">{stock.trading_code}</h1>
                        <p className="text-gray-500">{stock.name}</p>
                    </div>
                    <div className="text-right">
                        <p className="text-3xl font-bold text-indigo-600">৳{market.ltp}</p>
                        <p className={`font-medium ${market.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {market.change}
                        </p>
                    </div>
                </div>

                {/* Key Statistics Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 text-sm">
                    <div className="p-3 bg-gray-50 rounded-lg">
                        <span className="text-gray-500 block">High</span>
                        <span className="font-semibold">৳{market.high}</span>
                    </div>
                    <div className="p-3 bg-gray-50 rounded-lg">
                        <span className="text-gray-500 block">Low</span>
                        <span className="font-semibold">৳{market.low}</span>
                    </div>
                    <div className="p-3 bg-gray-50 rounded-lg">
                        <span className="text-gray-500 block">Volume</span>
                        <span className="font-semibold">{market.volume}</span>
                    </div>
                    <div className="p-3 bg-gray-50 rounded-lg">
                        <span className="text-gray-500 block">YCP</span>
                        <span className="font-semibold">৳{market.ycp}</span>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Chart Section using Recharts */}
                <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-sm border border-gray-100 h-96">
                    <h3 className="text-lg font-semibold mb-4">Price Movement</h3>
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} />
                            <XAxis dataKey="name" />
                            <YAxis domain={['auto', 'auto']} />
                            <Tooltip />
                            <Line type="monotone" dataKey="value" stroke="#4f46e5" strokeWidth={2} dot={{ r: 4 }} />
                        </LineChart>
                    </ResponsiveContainer>
                </div>

                {/* Trade Section (Buy/Sell Form) */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 className="text-lg font-semibold mb-4">Trade</h3>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Quantity</label>
                            <input
                                type="number"
                                value={buyQuantity}
                                onChange={(e) => setBuyQuantity(e.target.value)}
                                className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Price</label>
                            <input
                                type="number"
                                value={buyPrice}
                                onChange={(e) => setBuyPrice(e.target.value)}
                                className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                            />
                        </div>
                        <div className="grid grid-cols-2 gap-3 pt-2">
                            <button
                                onClick={() => handleTransaction('BUY')}
                                className="bg-green-600 text-white py-2 rounded-lg font-medium hover:bg-green-700"
                            >
                                Buy
                            </button>
                            <button
                                onClick={() => handleTransaction('SELL')}
                                className="bg-red-600 text-white py-2 rounded-lg font-medium hover:bg-red-700"
                            >
                                Sell
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default StockDetail;

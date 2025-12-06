import React, { useEffect, useState, useContext } from 'react';
import { getHoldings, getTransactions, createTransaction } from '../api';
import AuthContext from '../context/AuthContext';
import { Link } from 'react-router-dom';
import { Calendar, DollarSign, Clock } from 'lucide-react';

const Portfolio = () => {
    const { user } = useContext(AuthContext);
    const [holdings, setHoldings] = useState([]);
    const [loading, setLoading] = useState(true);

    // Transaction History State
    const [transactions, setTransactions] = useState([]);
    const [historyLoading, setHistoryLoading] = useState(false);
    const [dateFrom, setDateFrom] = useState('');
    const [dateTo, setDateTo] = useState('');

    // Sell Modal State
    const [sellModalOpen, setSellModalOpen] = useState(false);
    const [sellItem, setSellItem] = useState(null);
    const [sellQuantity, setSellQuantity] = useState('');
    const [sellPrice, setSellPrice] = useState('');
    const [sellSubmitting, setSellSubmitting] = useState(false);

    const fetchData = () => {
        setLoading(true);
        getHoldings()
            .then(res => setHoldings(res.data))
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    };

    const fetchHistory = () => {
        setHistoryLoading(true);
        const params = {};
        if (dateFrom) params.start_date = new Date(dateFrom).toISOString();
        if (dateTo) params.end_date = new Date(dateTo).toISOString();

        getTransactions(params)
            .then(res => setTransactions(res.data))
            .catch(err => console.error(err))
            .finally(() => setHistoryLoading(false));
    };

    useEffect(() => {
        if (user) {
            fetchData();
            fetchHistory();
        } else {
            setLoading(false);
        }
    }, [user]);

    const handleSellClick = (item) => {
        setSellItem(item);
        setSellQuantity(item.quantity);
        setSellPrice(item.stock.market_data?.ltp || 0);
        setSellModalOpen(true);
    };

    const confirmSell = async (e) => {
        e.preventDefault();
        setSellSubmitting(true);
        try {
            await createTransaction({
                stock_id: sellItem.stock.id,
                type: 'SELL',
                quantity: parseFloat(sellQuantity),
                price: parseFloat(sellPrice)
            });
            setSellModalOpen(false);
            fetchData(); // Refresh portfolio
            fetchHistory(); // Refresh history
        } catch (err) {
            alert("Failed to sell. Check quantity.");
            console.error(err);
        } finally {
            setSellSubmitting(false);
        }
    };

    if (!user) {
        return (
            <div className="text-center py-20 bg-white rounded-xl shadow-sm border border-gray-100">
                <h2 className="text-2xl font-bold text-gray-800 mb-4">Please Login to View Portfolio</h2>
                <Link to="/login" className="inline-block bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700">
                    Login
                </Link>
            </div>
        );
    }

    if (loading) return <div>Loading...</div>;

    return (
        <div className="space-y-8">
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
                                <th className="px-6 py-4 text-right">Action</th>
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
                                        <td className={`px-6 py-4 text-right font-medium ${isGain ? 'text-green-600' : 'text-red-600'}`}>
                                            {isGain ? '+' : ''}{item.gain_loss.toFixed(2)} ({item.gain_loss_percent.toFixed(2)}%)
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <button
                                                onClick={() => handleSellClick(item)}
                                                className="bg-red-50 text-red-600 px-3 py-1 rounded hover:bg-red-100 text-xs font-medium"
                                            >
                                                Sell
                                            </button>
                                        </td>
                                    </tr>
                                );
                            })}
                            {holdings.length === 0 && (
                                <tr><td colSpan="7" className="text-center py-4 text-gray-500">No holdings found. Buy stocks from Market.</td></tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Transaction History Section */}
            <div className="space-y-4">
                <div className="flex justify-between items-center bg-white p-4 rounded-xl border border-gray-100">
                    <h3 className="text-lg font-bold text-gray-800 flex items-center">
                        <Clock size={20} className="mr-2" /> Transaction History
                    </h3>
                    <div className="flex space-x-2">
                        <input
                            type="date"
                            className="border rounded p-1 text-sm"
                            value={dateFrom}
                            onChange={e => setDateFrom(e.target.value)}
                        />
                        <span className="self-center">-</span>
                        <input
                            type="date"
                            className="border rounded p-1 text-sm"
                            value={dateTo}
                            onChange={e => setDateTo(e.target.value)}
                        />
                        <button
                            onClick={fetchHistory}
                            className="bg-indigo-600 text-white px-4 py-1 rounded text-sm hover:bg-indigo-700"
                        >
                            Filter
                        </button>
                        <button
                            onClick={() => {
                                if (transactions.length === 0) return alert("No transactions to export");
                                const headers = ["Date", "Type", "Stock ID", "Quantity", "Price", "Total"];
                                const rows = transactions.map(t => [
                                    new Date(t.date).toLocaleDateString(),
                                    t.type,
                                    t.stock_id,
                                    t.quantity,
                                    t.price,
                                    (t.quantity * t.price).toFixed(2)
                                ]);
                                const csvContent = "data:text/csv;charset=utf-8,"
                                    + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
                                const encodedUri = encodeURI(csvContent);
                                const link = document.createElement("a");
                                link.setAttribute("href", encodedUri);
                                link.setAttribute("download", "transactions.csv");
                                document.body.appendChild(link);
                                link.click();
                                document.body.removeChild(link);
                            }}
                            className="bg-gray-100 text-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-200 border border-gray-300"
                        >
                            Export
                        </button>
                    </div>
                </div>

                <div className="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100">
                    <div className="overflow-x-auto max-h-96">
                        <table className="w-full text-left text-sm text-gray-600">
                            <thead className="bg-gray-50 text-xs uppercase font-semibold text-gray-500 sticky top-0">
                                <tr>
                                    <th className="px-6 py-3">Date</th>
                                    <th className="px-6 py-3">Type</th>
                                    <th className="px-6 py-3">Stock (ID)</th>
                                    <th className="px-6 py-3 text-right">Qty</th>
                                    <th className="px-6 py-3 text-right">Price</th>
                                    <th className="px-6 py-3 text-right">Total</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                                {transactions.map((t) => (
                                    <tr key={t.id} className="hover:bg-gray-50">
                                        <td className="px-6 py-3">{new Date(t.date || Date.now()).toLocaleDateString()}</td>
                                        <td className="px-6 py-3">
                                            <span className={`px-2 py-0.5 rounded text-xs font-bold ${t.type === 'BUY' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                                {t.type}
                                            </span>
                                        </td>
                                        <td className="px-6 py-3">{t.stock_id}</td>
                                        <td className="px-6 py-3 text-right">{t.quantity}</td>
                                        <td className="px-6 py-3 text-right">৳{t.price}</td>
                                        <td className="px-6 py-3 text-right font-medium">৳{(t.quantity * t.price).toFixed(2)}</td>
                                    </tr>
                                ))}
                                {transactions.length === 0 && (
                                    <tr><td colSpan="6" className="text-center py-4">No transactions found</td></tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            {/* Sell Modal */}
            {sellModalOpen && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-xl shadow-lg p-6 w-full max-w-sm">
                        <h3 className="text-xl font-bold mb-4">Sell {sellItem?.stock.trading_code}</h3>
                        <form onSubmit={confirmSell} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-1">Quantity (Max: {sellItem?.quantity})</label>
                                <input
                                    type="number"
                                    max={sellItem?.quantity}
                                    value={sellQuantity}
                                    onChange={e => setSellQuantity(e.target.value)}
                                    className="w-full border rounded p-2"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">Price (৳)</label>
                                <input
                                    type="number"
                                    step="0.1"
                                    value={sellPrice}
                                    onChange={e => setSellPrice(e.target.value)}
                                    className="w-full border rounded p-2"
                                    required
                                />
                            </div>
                            <div className="flex space-x-3 pt-2">
                                <button
                                    type="button"
                                    onClick={() => setSellModalOpen(false)}
                                    className="flex-1 bg-gray-100 text-gray-700 py-2 rounded hover:bg-gray-200"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={sellSubmitting}
                                    className="flex-1 bg-red-600 text-white py-2 rounded hover:bg-red-700 disabled:opacity-50"
                                >
                                    {sellSubmitting ? "Selling..." : "Confirm Sell"}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Portfolio;

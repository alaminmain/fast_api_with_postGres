import React, { useEffect, useState, useContext } from 'react';
import { getAlerts, createAlert, deleteAlert, getStocks } from '../api';
import AuthContext from '../context/AuthContext';
import { Trash2, TrendingUp, TrendingDown, Bell, Plus, Check } from 'lucide-react';

const Alerts = () => {
    const { user } = useContext(AuthContext);
    const [alerts, setAlerts] = useState([]);
    const [stocks, setStocks] = useState([]);

    // Form State
    const [stockId, setStockId] = useState('');
    const [targetPrice, setTargetPrice] = useState('');
    const [condition, setCondition] = useState('ABOVE'); // ABOVE or BELOW
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState(null);

    // Fetch data
    const fetchAll = async () => {
        try {
            const [alertsRes, stocksRes] = await Promise.all([
                getAlerts(),
                getStocks()
            ]);
            setAlerts(alertsRes.data);
            setStocks(stocksRes.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (user) {
            fetchAll();
        }
    }, [user]);

    const handleCreate = async (e) => {
        e.preventDefault();
        setSubmitting(true);
        setError(null);
        try {
            await createAlert({
                stock_id: parseInt(stockId),
                target_price: parseFloat(targetPrice),
                condition: condition
            });
            // Reset form
            setStockId('');
            setTargetPrice('');
            setCondition('ABOVE');
            // Refresh list
            const res = await getAlerts();
            setAlerts(res.data);
        } catch (err) {
            console.error(err);
            setError("Failed to create alert. Ensure stock is selected and price is valid.");
        } finally {
            setSubmitting(false);
        }
    };

    const handleDelete = async (id) => {
        if (!confirm("Are you sure you want to delete this alert?")) return;
        try {
            await deleteAlert(id);
            setAlerts(alerts.filter(a => a.id !== id));
        } catch (err) {
            console.error(err);
        }
    };

    if (!user) return <div className="p-10 text-center">Please login to manage alerts.</div>;
    if (loading) return <div className="p-10 text-center">Loading...</div>;

    return (
        <div className="space-y-8">
            <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-800">Price Alerts</h2>
            </div>

            {/* Create Alert Card */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
                <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                    <Plus size={20} className="mr-2" />
                    Create New Alert
                </h3>
                {error && <div className="mb-4 text-red-600 bg-red-50 p-3 rounded-lg text-sm">{error}</div>}
                <form onSubmit={handleCreate} className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Stock</label>
                        <select
                            value={stockId}
                            onChange={e => setStockId(e.target.value)}
                            className="w-full rounded-lg border-gray-300 focus:ring-indigo-500 focus:border-indigo-500"
                            required
                        >
                            <option value="">Select Stock...</option>
                            {stocks.map(s => (
                                <option key={s.id} value={s.id}>{s.trading_code}</option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Condition</label>
                        <select
                            value={condition}
                            onChange={e => setCondition(e.target.value)}
                            className="w-full rounded-lg border-gray-300 focus:ring-indigo-500 focus:border-indigo-500"
                        >
                            <option value="ABOVE">Price Goes Above</option>
                            <option value="BELOW">Price Goes Below</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Target Price (৳)</label>
                        <input
                            type="number"
                            step="0.1"
                            value={targetPrice}
                            onChange={e => setTargetPrice(e.target.value)}
                            className="w-full rounded-lg border-gray-300 focus:ring-indigo-500 focus:border-indigo-500"
                            placeholder="0.00"
                            required
                        />
                    </div>
                    <button
                        type="submit"
                        disabled={submitting}
                        className="bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 font-medium flex justify-center items-center disabled:opacity-50"
                    >
                        {submitting ? "Adding..." : "Add Alert"}
                    </button>
                </form>
            </div>

            {/* Alerts List */}
            <div className="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100">
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm text-gray-600">
                        <thead className="bg-gray-50 text-xs uppercase font-semibold text-gray-500">
                            <tr>
                                <th className="px-6 py-4">Stock</th>
                                <th className="px-6 py-4">Current Price</th>
                                <th className="px-6 py-4">Condition</th>
                                <th className="px-6 py-4">Target Price</th>
                                <th className="px-6 py-4">Status</th>
                                <th className="px-6 py-4 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {alerts.map((alert) => {
                                const stock = stocks.find(s => s.id === alert.stock_id); // Simple lookup
                                const currentPrice = stock?.market_data?.ltp || 0;

                                return (
                                    <tr key={alert.id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 font-medium text-gray-900">{stock?.trading_code || 'Unknown'}</td>
                                        <td className="px-6 py-4">৳{currentPrice}</td>
                                        <td className="px-6 py-4">
                                            <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-semibold ${alert.condition === 'ABOVE' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                                }`}>
                                                {alert.condition === 'ABOVE' ? <TrendingUp size={14} className="mr-1" /> : <TrendingDown size={14} className="mr-1" />}
                                                {alert.condition}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 font-bold">৳{alert.target_price}</td>
                                        <td className="px-6 py-4">
                                            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${alert.is_active ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'}`}>
                                                {alert.is_active ? 'Active' : 'Inactive'}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <button
                                                onClick={() => handleDelete(alert.id)}
                                                className="text-gray-400 hover:text-red-600 transition-colors"
                                                title="Delete Alert"
                                            >
                                                <Trash2 size={18} />
                                            </button>
                                        </td>
                                    </tr>
                                );
                            })}
                            {alerts.length === 0 && (
                                <tr>
                                    <td colSpan="6" className="px-6 py-8 text-center text-gray-500">
                                        <div className="flex flex-col items-center justify-center">
                                            <Bell size={32} className="text-gray-300 mb-2" />
                                            <p>No active alerts found.</p>
                                        </div>
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default Alerts;

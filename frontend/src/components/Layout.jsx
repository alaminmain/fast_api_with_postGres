import React, { useState, useContext } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { LayoutDashboard, TrendingUp, PieChart, Menu, X, Bell, LogOut } from 'lucide-react';
import clsx from 'clsx';
import AuthContext from '../context/AuthContext';

const Layout = () => {
    const { user, logout } = useContext(AuthContext);
    // useState hook to manage the state of the mobile menu (open/closed).
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    // useLocation hook to get the current URL path (used for highlighting active nav item).
    const location = useLocation();

    const navItems = [
        { name: 'Dashboard', path: '/', icon: LayoutDashboard },
        { name: 'Market', path: '/market', icon: TrendingUp },
        { name: 'Portfolio', path: '/portfolio', icon: PieChart },
        { name: 'Alerts', path: '/alerts', icon: Bell },
    ];

    return (
        // min-h-screen: Minimum height of 100vh (full viewport height).
        // flex-col md:flex-row: Column layout on mobile, Row layout on medium screens and up.
        <div className="min-h-screen bg-gray-50 flex flex-col md:flex-row">

            {/* Mobile Header (Visible only on small screens 'md:hidden') */}
            <div className="md:hidden bg-white border-b p-4 flex justify-between items-center sticky top-0 z-20">
                <h1 className="text-xl font-bold text-indigo-600">StockManager</h1>
                <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}>
                    {isMobileMenuOpen ? <X /> : <Menu />}
                </button>
            </div>

            {/* Sidebar / Mobile Menu */}
            {/* clsx is a utility to conditionally join class names. */}
            <div className={clsx(
                "fixed inset-y-0 left-0 z-10 w-64 bg-white border-r transform transition-transform duration-200 ease-in-out md:relative md:translate-x-0",
                // If menu is open, translate-x-0 (show). If closed, -translate-x-full (hide off-screen).
                isMobileMenuOpen ? "translate-x-0" : "-translate-x-full"
            )}>
                <div className="p-6 hidden md:block">
                    <h1 className="text-2xl font-bold text-indigo-600">StockManager</h1>
                </div>
                <nav className="mt-6 px-4 space-y-2">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = location.pathname === item.path;
                        return (
                            <Link
                                key={item.path}
                                to={item.path}
                                onClick={() => setIsMobileMenuOpen(false)} // Close menu on click (mobile)
                                className={clsx(
                                    "flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors",
                                    // Conditional styling for active state
                                    isActive ? "bg-indigo-50 text-indigo-600" : "text-gray-600 hover:bg-gray-50"
                                )}
                            >
                                <Icon size={20} />
                                <span className="font-medium">{item.name}</span>
                            </Link>
                        );
                    })}

                    {user ? (
                        <button
                            onClick={() => {
                                logout();
                                setIsMobileMenuOpen(false);
                            }}
                            className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors text-red-600 hover:bg-red-50 mt-4"
                        >
                            <LogOut size={20} />
                            <span className="font-medium">Logout</span>
                        </button>
                    ) : (
                        <Link
                            to="/login"
                            onClick={() => setIsMobileMenuOpen(false)}
                            className="flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors text-indigo-600 hover:bg-indigo-50 mt-4"
                        >
                            <span className="font-medium">Login</span>
                        </Link>
                    )}
                </nav>
            </div>

            {/* Main Content Area */}
            {/* flex-1: Takes up remaining space. overflow-auto: Handles scrolling. */}
            <div className="flex-1 overflow-auto">
                <div className="p-4 md:p-8 max-w-7xl mx-auto">
                    {/* Outlet renders the child route component (Dashboard, Market, etc.) */}
                    <Outlet />
                </div>
            </div>

            {/* Overlay for mobile menu (closes menu when clicked) */}
            {isMobileMenuOpen && (
                <div
                    className="fixed inset-0 bg-black bg-opacity-50 z-0 md:hidden"
                    onClick={() => setIsMobileMenuOpen(false)}
                />
            )}
        </div>
    );
};

export default Layout;

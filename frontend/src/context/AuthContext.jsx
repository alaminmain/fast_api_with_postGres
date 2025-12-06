import React, { createContext, useState, useEffect } from 'react';
import { login as loginApi, register as registerApi, logout as logoutApi } from '../api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('authToken'));
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (token) {
            // Basic check: if token exists, we consider user logged in.
            // In a real app, we would verify token validity with backend or check expiration.
            setUser({ loggedIn: true });
        }
    }, [token]);

    const login = async (email, password) => {
        setLoading(true);
        try {
            const response = await loginApi(email, password);
            const access_token = response.data.access_token;
            setToken(access_token);
            localStorage.setItem('authToken', access_token);
            setUser({ email, loggedIn: true });
            return true;
        } catch (error) {
            console.error("Login failed", error);
            throw error;
        } finally {
            setLoading(false);
        }
    };

    const register = async (email, password) => {
        setLoading(true);
        try {
            await registerApi(email, password);
            return true;
        } catch (error) {
            console.error("Registration failed", error);
            throw error;
        } finally {
            setLoading(false);
        }
    };

    const logout = async () => {
        try {
            await logoutApi();
        } catch (error) {
            console.error("Logout failed", error);
        }
        setToken(null);
        setUser(null);
        localStorage.removeItem('authToken');
    };

    return (
        <AuthContext.Provider value={{ user, token, login, logout, register, loading }}>
            {children}
        </AuthContext.Provider>
    );
};

export default AuthContext;

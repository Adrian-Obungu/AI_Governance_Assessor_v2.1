import React, { createContext, useContext, useState, useEffect } from 'react';

interface AuthContextType {
    token: string | null;
    email: string | null;
    login: (token: string, email: string) => void;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [token, setToken] = useState<string | null>(null);
    const [email, setEmail] = useState<string | null>(null);

    useEffect(() => {
        // Load from localStorage on mount
        const savedToken = localStorage.getItem('auth_token');
        const savedEmail = localStorage.getItem('auth_email');
        if (savedToken && savedEmail) {
            setToken(savedToken);
            setEmail(savedEmail);
        }
    }, []);

    const login = (newToken: string, newEmail: string) => {
        setToken(newToken);
        setEmail(newEmail);
        localStorage.setItem('auth_token', newToken);
        localStorage.setItem('auth_email', newEmail);
    };

    const logout = () => {
        setToken(null);
        setEmail(null);
        localStorage.removeItem('auth_token');
        localStorage.removeItem('auth_email');
    };

    return (
        <AuthContext.Provider value={{ token, email, login, logout, isAuthenticated: !!token }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
};

import React, { createContext, useContext, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface AuthContextType {
    token: string | null;
    email: string | null;
    login: (token: string, email: string) => void;
    logout: () => void;
    expireSession: () => void;
    sessionMessage: string | null;
    clearSessionMessage: () => void;
    isAuthenticated: boolean;
}

const SESSION_EXPIRED_MESSAGE = 'Your session expired. Please sign in again.';
const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [token, setToken] = useState<string | null>(() => localStorage.getItem('auth_token'));
    const [email, setEmail] = useState<string | null>(() => localStorage.getItem('auth_email'));
    const [sessionMessage, setSessionMessage] = useState<string | null>(null);
    const expiryHandled = useRef(false);
    const navigate = useNavigate();

    const login = (newToken: string, newEmail: string) => {
        expiryHandled.current = false;
        setToken(newToken);
        setEmail(newEmail);
        setSessionMessage(null);
        localStorage.setItem('auth_token', newToken);
        localStorage.setItem('auth_email', newEmail);
    };

    const logout = () => {
        setToken(null);
        setEmail(null);
        localStorage.removeItem('auth_token');
        localStorage.removeItem('auth_email');
    };

    const expireSession = () => {
        if (expiryHandled.current) return;
        expiryHandled.current = true;
        logout();
        setSessionMessage(SESSION_EXPIRED_MESSAGE);
        navigate('/login', { replace: true });
    };

    const clearSessionMessage = () => setSessionMessage(null);

    return (
        <AuthContext.Provider value={{
            token,
            email,
            login,
            logout,
            expireSession,
            sessionMessage,
            clearSessionMessage,
            isAuthenticated: !!token,
        }}>
            {children}
        </AuthContext.Provider>
    );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) throw new Error('useAuth must be used within AuthProvider');
    return context;
};

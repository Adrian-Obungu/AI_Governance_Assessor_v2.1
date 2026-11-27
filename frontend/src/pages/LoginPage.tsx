import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../services/api';

const LoginPage: React.FC = () => {
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [fullName, setFullName] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login, sessionMessage, clearSessionMessage } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        clearSessionMessage();
        setLoading(true);

        try {
            if (isLogin) {
                const data = await authAPI.login(email, password);
                login(data.access_token, email);
                navigate('/dashboard');
            } else {
                await authAPI.signup(email, password, fullName);
                const loginData = await authAPI.login(email, password);
                login(loginData.access_token, email);
                navigate('/dashboard');
            }
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'An error occurred. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
            <div className="card max-w-md w-full" aria-labelledby="auth-title">
                <h1 id="auth-title" className="text-3xl font-bold text-gray-800 mb-2 text-center">
                    AI Governance Assessor
                </h1>
                <p className="text-gray-600 text-center mb-6">
                    {isLogin ? 'Sign in to review and manage AI governance assessments.' : 'Create an account to start an AI governance assessment.'}
                </p>

                <form onSubmit={handleSubmit} className="space-y-4">
                    {!isLogin && (
                        <div>
                            <label htmlFor="full-name" className="block text-sm font-medium text-gray-700 mb-1">
                                Full name
                            </label>
                            <input
                                id="full-name"
                                type="text"
                                value={fullName}
                                onChange={(e) => setFullName(e.target.value)}
                                className="input-field"
                                placeholder="Jane Doe"
                                autoComplete="name"
                                required
                            />
                        </div>
                    )}

                    <div>
                        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                            Email
                        </label>
                        <input
                            id="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="input-field"
                            placeholder="you@example.com"
                            autoComplete="email"
                            required
                        />
                    </div>

                    <div>
                        <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                            Password
                        </label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="input-field"
                            placeholder="••••••••"
                            autoComplete={isLogin ? 'current-password' : 'new-password'}
                            aria-describedby="password-hint"
                            required
                            minLength={8}
                        />
                        <p id="password-hint" className="mt-1 text-xs text-gray-500">Use at least 8 characters.</p>
                    </div>

                    {sessionMessage && (
                        <div role="alert" className="bg-amber-50 border border-amber-200 text-amber-800 px-4 py-3 rounded">
                            {sessionMessage}
                        </div>
                    )}

                    {error && (
                        <div role="alert" className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className="btn-primary w-full disabled:opacity-50"
                    >
                        {loading ? 'Processing...' : isLogin ? 'Sign in' : 'Create account'}
                    </button>
                </form>

                <div className="mt-4 text-center">
                    <button
                        type="button"
                        onClick={() => {
                            setIsLogin(!isLogin);
                            setError('');
                        }}
                        className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                    >
                        {isLogin ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;

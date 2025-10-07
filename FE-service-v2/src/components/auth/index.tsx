// React Hooks and Components for Kong Gateway Authentication
import { useState, useEffect } from 'react';
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { kongApi } from '../../services/kongApiService';
import type { AuthResponse, UserData } from '../../services/kongApiService';

// Hook for Kong Authentication
export const useKongAuth = () => {
    const [user, setUser] = useState<UserData | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [authenticated, setAuthenticated] = useState<boolean>(false);

    useEffect(() => {
        checkAuthStatus();
    }, []);

    const checkAuthStatus = async (): Promise<void> => {
        try {
            setLoading(true);
            const isValid = await kongApi.validateToken();
            if (isValid) {
                const userData = kongApi.getCurrentUserFromStorage();
                setUser(userData);
                setAuthenticated(true);
            } else {
                setUser(null);
                setAuthenticated(false);
            }
        } catch (error) {
            console.error('Auth check failed :', error);
            setUser(null);
            setAuthenticated(false);
        } finally {
            setLoading(false);
        }
    };

    const login = async (email: string, password: string): Promise<AuthResponse> => {
        try {
            const response = await kongApi.login(email, password);
            setUser(response.user);
            setAuthenticated(true);
            return response;
        } catch (error) {
            setUser(null);
            setAuthenticated(false);
            throw error;
        }
    };

    const register = async (userData: Partial<UserData>): Promise<AuthResponse> => {
        try {
            const response = await kongApi.register(userData);
            setUser(response.user);
            setAuthenticated(true);
            return response;
        } catch (error) {
            setUser(null);
            setAuthenticated(false);
            throw error;
        }
    };

    const logout = (): void => {
        kongApi.logout();
        setUser(null);
        setAuthenticated(false);
    };

    const refreshAuth = async (): Promise<AuthResponse> => {
        try {
            const response = await kongApi.refreshToken();
            setUser(response.user);
            setAuthenticated(true);
            return response;
        } catch (error) {
            setUser(null);
            setAuthenticated(false);
            throw error;
        }
    };

    return {
        user,
        loading,
        authenticated,
        login,
        register,
        logout,
        refreshAuth,
        checkAuthStatus
    };
};

// Auth Guard Component
interface AuthGuardProps {
    children: React.ReactNode;
}

export const AuthGuard: React.FC<AuthGuardProps> = ({ children }) => {
    const { authenticated, loading } = useKongAuth();
    const location = useLocation();

    if (loading) {
        return (
            <div className="flex justify-center items-center h-screen">
                <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
                <div className="ml-4 text-lg text-gray-600">Loading...</div>
            </div>
        );
    }

    if (!authenticated) {
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    return <>{children}</>;
};

// Login Form Component
interface LoginFormProps {
    onLogin: (email: string, password: string) => Promise<void>;
    loading?: boolean;
    error?: string;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onLogin, loading = false, error }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (email && password) {
            await onLogin(email, password);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8">
                <div>
                    <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                        Sign in to your account
                    </h2>
                </div>
                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    {error && (
                        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                            {error}
                        </div>
                    )}
                    <div className="rounded-md shadow-sm -space-y-px">
                        <div>
                            <input
                                id="email"
                                name="email"
                                type="email"
                                autoComplete="email"
                                required
                                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                                placeholder="Email address"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                        </div>
                        <div>
                            <input
                                id="password"
                                name="password"
                                type="password"
                                autoComplete="current-password"
                                required
                                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                                placeholder="Password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                        </div>
                    </div>

                    <div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                        >
                            {loading ? 'Signing in...' : 'Sign in'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

// User Profile Component
interface UserProfileProps {
    user: UserData | null;
    onLogout: () => void;
}

export const UserProfile: React.FC<UserProfileProps> = ({ user, onLogout }) => {
    if (!user) return null;

    return (
        <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center space-x-6">
                <div className="flex-shrink-0">
                    <div className="h-10 w-10 rounded-full bg-indigo-500 flex items-center justify-center">
                        <span className="text-sm font-medium text-white">
                            {user.name.charAt(0).toUpperCase()}
                        </span>
                    </div>
                </div>
                <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                        {user.name}
                    </p>
                    <p className="text-sm text-gray-500 truncate">
                        {user.email}
                    </p>
                </div>
                <div className="flex-shrink-0">
                    <button
                        onClick={onLogout}
                        className="bg-white py-2 px-3 border border-gray-300 rounded-md shadow-sm text-sm leading-4 font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                        Logout
                    </button>
                </div>
            </div>
        </div>
    );
};

// Error Boundary Component
interface ErrorBoundaryState {
    hasError: boolean;
    error?: Error;
}

export class ErrorBoundary extends React.Component<
    { children: React.ReactNode },
    ErrorBoundaryState
> {
    constructor(props: { children: React.ReactNode }) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(error: Error): ErrorBoundaryState {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
        console.error('Auth component error:', error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen flex items-center justify-center bg-gray-50">
                    <div className="max-w-md w-full space-y-8">
                        <div className="text-center">
                            <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
                                Something went wrong
                            </h2>
                            <p className="mt-2 text-sm text-gray-600">
                                Please refresh the page and try again.
                            </p>
                            <button
                                onClick={() => window.location.reload()}
                                className="mt-4 bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
                            >
                                Refresh Page
                            </button>
                        </div>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

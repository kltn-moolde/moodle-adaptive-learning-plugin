// LTI-specific React hooks and components
import { useState, useEffect } from 'react';
import React from 'react';
import { ltiService, type LTIUserData, isLTIContext } from '../../services/ltiServiceFixed';

// Hook for LTI Authentication
export const useLTIAuth = () => {
    const [user, setUser] = useState<LTIUserData | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [authenticated, setAuthenticated] = useState<boolean>(false);
    const [isLTI, setIsLTI] = useState<boolean>(false);
    const [error, setError] = useState<string>('');

    useEffect(() => {
        initializeLTI();
    }, []);

    const initializeLTI = async (): Promise<void> => {
        try {
            setLoading(true);
            setError('');
            
            // Check if this is an LTI launch
            const ltiContext = isLTIContext();
            setIsLTI(ltiContext);

            if (ltiContext) {
                // Authenticate with LTI parameters
                const ltiUser = await ltiService.authenticateWithLTI();
                if (ltiUser) {
                    setUser(ltiUser);
                    setAuthenticated(true);
                } else {
                    setError('Failed to authenticate with LTI parameters');
                }
            } else {
                // Not an LTI launch - check if user is already authenticated
                const storedUser = localStorage.getItem('user_data');
                if (storedUser) {
                    const userData = JSON.parse(storedUser) as LTIUserData;
                    setUser(userData);
                    setAuthenticated(true);
                } else {
                    setError('No LTI parameters found and no existing session');
                }
            }
        } catch (error) {
            console.error('LTI initialization failed:', error);
            setError(error instanceof Error ? error.message : 'LTI initialization failed');
            setAuthenticated(false);
        } finally {
            setLoading(false);
        }
    };

    const logout = (): void => {
        ltiService.clearLTISession();
        setUser(null);
        setAuthenticated(false);
        setIsLTI(false);
        if (typeof window !== 'undefined') {
            localStorage.removeItem('auth_token');
            localStorage.removeItem('user_data');
        }
    };

    const getCourseContext = () => {
        return ltiService.getCourseContext();
    };

    return {
        user,
        loading,
        authenticated,
        isLTI,
        error,
        logout,
        getCourseContext,
        reinitialize: initializeLTI
    };
};

// LTI Loading Component
export const LTILoader: React.FC = () => {
    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="max-w-md w-full space-y-8">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto"></div>
                    <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
                        Loading Moodle Integration
                    </h2>
                    <p className="mt-2 text-sm text-gray-600">
                        Authenticating with LTI parameters...
                    </p>
                </div>
            </div>
        </div>
    );
};

// LTI Error Component
interface LTIErrorProps {
    error: string;
    onRetry?: () => void;
}

export const LTIError: React.FC<LTIErrorProps> = ({ error, onRetry }) => {
    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="max-w-md w-full space-y-8">
                <div className="text-center">
                    <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto">
                        <span className="text-2xl text-red-600">⚠</span>
                    </div>
                    <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
                        LTI Authentication Failed
                    </h2>
                    <p className="mt-2 text-sm text-gray-600">
                        {error}
                    </p>
                    {onRetry && (
                        <button
                            onClick={onRetry}
                            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                        >
                            Retry
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

// LTI Context Display Component
interface LTIContextProps {
    user: LTIUserData;
}

export const LTIContext: React.FC<LTIContextProps> = ({ user }) => {
    const courseContext = ltiService.getCourseContext();
    
    return (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="flex items-center">
                <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                        <span className="text-white font-bold text-sm">M</span>
                    </div>
                </div>
                <div className="ml-3 flex-1">
                    <h3 className="text-sm font-medium text-blue-800">
                        Moodle Integration Active
                    </h3>
                    <div className="mt-1 text-sm text-blue-600">
                        <p><strong>Course:</strong> {courseContext?.courseTitle || 'Unknown'}</p>
                        <p><strong>User:</strong> {user.name} ({user.roleName})</p>
                        <p><strong>LTI ID:</strong> {user.ltiUserId}</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

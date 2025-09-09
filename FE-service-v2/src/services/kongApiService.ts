// Kong Gateway API Service
// Frontend integration with Kong Gateway and JWT authentication

export interface AuthResponse {
    token: string;
    type: string;
    user: UserData;
    expiresIn: number;
}

export interface UserData {
    id: number;
    name: string;
    email: string;
    role: string;
    roleId: number;
}

export class KongApiService {
    private baseURL: string;
    private token: string | null = null;

    constructor(baseURL: string = 'http://localhost:8000') {
        this.baseURL = baseURL;
        this.token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
    }

    // Authentication methods
    async login(email: string, password: string): Promise<AuthResponse> {
        try {
            const response = await fetch(`${this.baseURL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `Login failed: ${response.status}`);
            }

            const data: AuthResponse = await response.json();
            
            if (data.token && typeof window !== 'undefined') {
                this.token = data.token;
                localStorage.setItem('auth_token', data.token);
                localStorage.setItem('user_data', JSON.stringify(data.user));
            }

            return data;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    }

    async register(userData: Partial<UserData>): Promise<AuthResponse> {
        try {
            const response = await fetch(`${this.baseURL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `Registration failed: ${response.status}`);
            }

            const data: AuthResponse = await response.json();
            
            if (data.token && typeof window !== 'undefined') {
                this.token = data.token;
                localStorage.setItem('auth_token', data.token);
                localStorage.setItem('user_data', JSON.stringify(data.user));
            }

            return data;
        } catch (error) {
            console.error('Registration error:', error);
            throw error;
        }
    }

    async validateToken(): Promise<boolean> {
        if (!this.token) return false;

        try {
            const response = await fetch(`${this.baseURL}/auth/validate`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                return false;
            }

            const data = await response.json();
            return data.valid === true;
        } catch (error) {
            console.error('Token validation error:', error);
            return false;
        }
    }

    async refreshToken(): Promise<AuthResponse> {
        if (!this.token) throw new Error('No token to refresh');

        try {
            const response = await fetch(`${this.baseURL}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Token refresh failed');
            }

            const data: AuthResponse = await response.json();
            
            if (data.token && typeof window !== 'undefined') {
                this.token = data.token;
                localStorage.setItem('auth_token', data.token);
            }

            return data;
        } catch (error) {
            console.error('Token refresh error:', error);
            this.logout();
            throw error;
        }
    }

    logout(): void {
        this.token = null;
        if (typeof window !== 'undefined') {
            localStorage.removeItem('auth_token');
            localStorage.removeItem('user_data');
        }
    }

    // LTI Authentication method
    async authenticateWithLTI(ltiUserData: Partial<UserData>): Promise<AuthResponse> {
        try {
            const response = await fetch(`${this.baseURL}/auth/lti`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(ltiUserData)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `LTI authentication failed: ${response.status}`);
            }

            const data: AuthResponse = await response.json();
            
            if (data.token && typeof window !== 'undefined') {
                this.token = data.token;
                localStorage.setItem('auth_token', data.token);
                localStorage.setItem('user_data', JSON.stringify(data.user));
            }

            return data;
        } catch (error) {
            console.error('LTI authentication error:', error);
            throw error;
        }
    }

    // API request helper with JWT authentication
    private async makeAuthenticatedRequest(endpoint: string, options: RequestInit = {}): Promise<any> {
        // Validate token before making request
        const isValidToken = await this.validateToken();
        if (!isValidToken) {
            try {
                await this.refreshToken();
            } catch (error) {
                this.logout();
                throw new Error('Authentication required');
            }
        }

        const headers: Record<string, string> = {
            'Content-Type': 'application/json',
            ...(options.headers as Record<string, string>),
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const response = await fetch(`${this.baseURL}${endpoint}`, {
            ...options,
            headers
        });

        // Handle 401 Unauthorized - try to refresh token
        if (response.status === 401) {
            try {
                await this.refreshToken();
                headers['Authorization'] = `Bearer ${this.token}`;
                
                // Retry request with new token
                const retryResponse = await fetch(`${this.baseURL}${endpoint}`, {
                    ...options,
                    headers
                });
                
                if (!retryResponse.ok) {
                    throw new Error(`Request failed: ${retryResponse.status}`);
                }
                
                return await retryResponse.json();
            } catch (error) {
                this.logout();
                throw new Error('Authentication failed');
            }
        }

        if (!response.ok) {
            throw new Error(`Request failed: ${response.status}`);
        }

        return await response.json();
    }

    // User API methods
    async getUsers(skip: number = 0, limit: number = 100): Promise<UserData[]> {
        return this.makeAuthenticatedRequest(`/api/users?skip=${skip}&limit=${limit}`);
    }

    async getUserById(id: number): Promise<UserData> {
        return this.makeAuthenticatedRequest(`/api/users/${id}`);
    }

    async getCurrentUser(): Promise<UserData> {
        return this.makeAuthenticatedRequest('/auth/me');
    }

    // Course API methods
    async getCourses(skip: number = 0, limit: number = 100): Promise<any[]> {
        return this.makeAuthenticatedRequest(`/api/courses?skip=${skip}&limit=${limit}`);
    }

    async getCourseById(id: number): Promise<any> {
        return this.makeAuthenticatedRequest(`/api/courses/${id}`);
    }

    async createCourse(courseData: any): Promise<any> {
        return this.makeAuthenticatedRequest('/api/courses', {
            method: 'POST',
            body: JSON.stringify(courseData)
        });
    }

    async updateCourse(id: number, courseData: any): Promise<any> {
        return this.makeAuthenticatedRequest(`/api/courses/${id}`, {
            method: 'PUT',
            body: JSON.stringify(courseData)
        });
    }

    async deleteCourse(id: number): Promise<void> {
        return this.makeAuthenticatedRequest(`/api/courses/${id}`, {
            method: 'DELETE'
        });
    }

    // LTI API methods
    async getLTILaunches(skip: number = 0, limit: number = 100): Promise<any[]> {
        return this.makeAuthenticatedRequest(`/api/lti/launches?skip=${skip}&limit=${limit}`);
    }

    async getUserLTILaunches(userId: string, skip: number = 0, limit: number = 100): Promise<any[]> {
        return this.makeAuthenticatedRequest(`/api/lti/user/${userId}/launches?skip=${skip}&limit=${limit}`);
    }

    async getLTIConfig(): Promise<any> {
        return this.makeAuthenticatedRequest('/api/lti/config');
    }

    // Utility methods
    isAuthenticated(): boolean {
        return !!this.token;
    }

    getToken(): string | null {
        return this.token;
    }

    getCurrentUserFromStorage(): UserData | null {
        if (typeof window === 'undefined') return null;
        
        const userData = localStorage.getItem('user_data');
        try {
            return userData ? JSON.parse(userData) : null;
        } catch (error) {
            console.error('Error parsing user data from localStorage:', error);
            return null;
        }
    }

    // Health check (no authentication required)
    async healthCheck(): Promise<{ status: string; service: string; timestamp: number }> {
        try {
            const response = await fetch(`${this.baseURL}/auth/health`);
            if (!response.ok) {
                throw new Error(`Health check failed: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Health check failed:', error);
            throw error;
        }
    }

    // Analytics methods
    async getAnalytics(dateFrom?: string, dateTo?: string): Promise<any> {
        const params = new URLSearchParams();
        if (dateFrom) params.append('from', dateFrom);
        if (dateTo) params.append('to', dateTo);
        
        const query = params.toString();
        return this.makeAuthenticatedRequest(`/api/analytics${query ? `?${query}` : ''}`);
    }

    // Notification methods
    async getNotifications(unreadOnly: boolean = false): Promise<any[]> {
        return this.makeAuthenticatedRequest(`/api/notifications${unreadOnly ? '?unread=true' : ''}`);
    }

    async markNotificationAsRead(notificationId: number): Promise<void> {
        return this.makeAuthenticatedRequest(`/api/notifications/${notificationId}/read`, {
            method: 'POST'
        });
    }
}

// Export singleton instance
export const kongApi = new KongApiService();

export default KongApiService;

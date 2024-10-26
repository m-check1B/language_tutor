import { writable, derived } from 'svelte/store';

interface AuthStore {
    token: string | null;
    sessionId: string | null;
    isLoggedIn: boolean;
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api';

function createAuthStore() {
    const { subscribe, set, update } = writable<AuthStore>({
        token: null,
        sessionId: null,
        isLoggedIn: false
    });

    return {
        subscribe,
        register: async (email: string, password: string) => {
            try {
                const response = await fetch(`${API_URL}/auth/register`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        username: email,
                        email: email,
                        password: password
                    }),
                    credentials: 'include',
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Registration failed');
                }

                const data = await response.json();
                return data;
            } catch (error) {
                throw error;
            }
        },
        login: async (email: string, password: string) => {
            try {
                const response = await fetch(`${API_URL}/auth/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        username: email,
                        password: password
                    }),
                    credentials: 'include',
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Login failed');
                }

                const data = await response.json();
                set({ 
                    token: data.access_token, 
                    sessionId: data.session_id,
                    isLoggedIn: true 
                });
                return data;
            } catch (error) {
                throw error;
            }
        },
        logout: async () => {
            try {
                await fetch(`${API_URL}/auth/logout`, {
                    method: 'POST',
                    credentials: 'include',
                });
                set({ token: null, sessionId: null, isLoggedIn: false });
            } catch (error) {
                console.error('Logout failed:', error);
                set({ token: null, sessionId: null, isLoggedIn: false });
            }
        },
        refreshToken: async () => {
            try {
                const response = await fetch(`${API_URL}/auth/refresh`, {
                    method: 'POST',
                    credentials: 'include',
                });

                if (!response.ok) {
                    throw new Error('Token refresh failed');
                }

                const data = await response.json();
                update(state => ({
                    ...state,
                    token: data.access_token,
                    isLoggedIn: true
                }));
                return data.access_token;
            } catch (error) {
                console.error('Token refresh failed:', error);
                set({ token: null, sessionId: null, isLoggedIn: false });
                throw error;
            }
        },
        setToken: (token: string, sessionId: string) => {
            set({ token, sessionId, isLoggedIn: true });
        }
    };
}

export const auth = createAuthStore();
export const isLoggedIn = derived(auth, $auth => $auth.isLoggedIn);
export const authToken = derived(auth, $auth => $auth.token);
export const authSessionId = derived(auth, $auth => $auth.sessionId);

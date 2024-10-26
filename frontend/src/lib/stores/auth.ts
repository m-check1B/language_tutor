import { writable, derived } from 'svelte/store';

interface AuthStore {
    token: string | null;
    isLoggedIn: boolean;
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api';

function createAuthStore() {
    const { subscribe, set, update } = writable<AuthStore>({
        token: null,
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
                        username: email, // Using email as username
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
                const formData = new URLSearchParams();
                formData.append('username', email); // Backend expects username field
                formData.append('password', password);

                const response = await fetch(`${API_URL}/auth/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: formData,
                    credentials: 'include', // Include cookies
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Login failed');
                }

                const data = await response.json();
                set({ token: data.access_token, isLoggedIn: true });
                return data;
            } catch (error) {
                throw error;
            }
        },
        logout: async () => {
            try {
                await fetch(`${API_URL}/auth/logout`, {
                    method: 'POST',
                    credentials: 'include', // Include cookies
                });
                set({ token: null, isLoggedIn: false });
            } catch (error) {
                console.error('Logout failed:', error);
                // Still clear the local state even if the API call fails
                set({ token: null, isLoggedIn: false });
            }
        }
    };
}

export const auth = createAuthStore();
export const authSessionId = writable<string | null>(null);
export const isLoggedIn = derived(auth, $auth => $auth.isLoggedIn);

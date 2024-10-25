import { writable } from 'svelte/store';

function createAuth() {
    const { subscribe, set } = writable({
        isLoggedIn: false,
        token: null,
        user: null
    });

    return {
        subscribe,
        login: async (email, password) => {
            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email, password }),
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Login failed');
                }

                const data = await response.json();
                set({
                    isLoggedIn: true,
                    token: data.access_token,
                    user: data.user
                });

                localStorage.setItem('token', data.access_token);
            } catch (error) {
                throw error;
            }
        },
        register: async (email, password) => {
            try {
                const response = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email, password }),
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Registration failed');
                }

                const data = await response.json();
                set({
                    isLoggedIn: true,
                    token: data.access_token,
                    user: data.user
                });

                localStorage.setItem('token', data.access_token);
            } catch (error) {
                throw error;
            }
        },
        logout: () => {
            localStorage.removeItem('token');
            set({
                isLoggedIn: false,
                token: null,
                user: null
            });
        },
        initialize: () => {
            const token = localStorage.getItem('token');
            if (token) {
                set({
                    isLoggedIn: true,
                    token,
                    user: null // We could fetch user details here if needed
                });
            }
        }
    };
}

export const auth = createAuth();

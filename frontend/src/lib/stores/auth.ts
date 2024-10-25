import { writable, derived } from 'svelte/store';
import { PUBLIC_API_URL } from '$env/static/public';

interface User {
    id: string;
    username: string;
    email: string;
}

export const token = writable<string | null>(null);
export const user = writable<User | null>(null);
export const isLoggedIn = derived(token, $token => !!$token);

export const auth = {
    subscribe: isLoggedIn.subscribe,
    async login(email: string, password: string) {
        try {
            const response = await fetch(`${PUBLIC_API_URL}/auth/login`, {
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
            token.set(data.access_token);
            // Store token in localStorage for persistence
            localStorage.setItem('token', data.access_token);
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    },

    async logout() {
        token.set(null);
        user.set(null);
        localStorage.removeItem('token');
    },

    async register(username: string, email: string, password: string) {
        try {
            const response = await fetch(`${PUBLIC_API_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, email, password }),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Registration failed');
            }

            const data = await response.json();
            token.set(data.access_token);
            // Store token in localStorage for persistence
            localStorage.setItem('token', data.access_token);
        } catch (error) {
            console.error('Registration error:', error);
            throw error;
        }
    }
};

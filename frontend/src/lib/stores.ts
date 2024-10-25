import { writable, derived } from 'svelte/store';

interface User {
    id: string;
    username: string;
    email: string;
}

export const token = writable<string | null>(null);
export const user = writable<User | null>(null);
export const chatMessages = writable<any[]>([]);
export const currentConversation = writable<any | null>(null);

export const isLoggedIn = derived(token, $token => !!$token);

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost';

export const auth = {
    subscribe: isLoggedIn.subscribe,
    async login(email: string, password: string) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });

            if (!response.ok) {
                throw new Error('Login failed');
            }

            const data = await response.json();
            token.set(data.token);
            user.set(data.user);
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    },

    async logout() {
        token.set(null);
        user.set(null);
    },

    async register(username: string, email: string, password: string) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, email, password }),
            });

            if (!response.ok) {
                throw new Error('Registration failed');
            }

            const data = await response.json();
            token.set(data.token);
            user.set(data.user);
        } catch (error) {
            console.error('Registration error:', error);
            throw error;
        }
    }
};

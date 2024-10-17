import { writable, derived, get } from 'svelte/store';

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

function createAuth() {
  const { subscribe } = isLoggedIn;

  return {
    subscribe,
    login: async (email: string, password: string): Promise<void> => {
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
    },

    logout: async (): Promise<void> => {
      const response = await fetch(`${API_BASE_URL}/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${get(token)}`,
        },
      });

      if (!response.ok) {
        throw new Error('Logout failed');
      }

      token.set(null);
      user.set(null);
    },

    register: async (username: string, email: string, password: string): Promise<void> => {
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
    },
  };
}

export const auth = createAuth();

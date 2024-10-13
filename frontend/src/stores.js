import { writable, get } from 'svelte/store';
import { browser } from '$app/environment';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000';

/** @type {import('svelte/store').Writable<string | null>} */
export const token = writable(browser ? localStorage.getItem('token') : null);

/** @type {import('svelte/store').Writable<boolean>} */
export const isLoggedIn = writable(false);

/** @type {import('svelte/store').Writable<Object | null>} */
export const user = writable(browser ? JSON.parse(localStorage.getItem('user') || 'null') : null);

/** @type {import('svelte/store').Writable<number | null>} */
export const currentConversation = writable(null);

/**
 * @typedef {Object} Message
 * @property {number} id
 * @property {string} content
 * @property {boolean} is_user
 * @property {string} created_at
 */

/** @type {import('svelte/store').Writable<Message[]>} */
export const chatMessages = writable([]);

/**
 * Update token and localStorage
 * @param {string | null} newToken
 */
export function setToken(newToken) {
  token.set(newToken);
  if (browser) {
    if (newToken) {
      localStorage.setItem('token', newToken);
    } else {
      localStorage.removeItem('token');
    }
  }
  isLoggedIn.set(!!newToken);
}

/**
 * Update user data and localStorage
 * @param {Object | null} userData
 */
export function setUser(userData) {
  user.set(userData);
  if (browser) {
    if (userData) {
      localStorage.setItem('user', JSON.stringify(userData));
    } else {
      localStorage.removeItem('user');
    }
  }
}

/**
 * Clear all authentication data
 */
export function clearAuth() {
  setToken(null);
  setUser(null);
  isLoggedIn.set(false);
}

/**
 * Add a new message to the chat
 * @param {Message} message
 */
export function addMessage(message) {
  chatMessages.update(messages => [...messages, message]);
}

/**
 * Clear all chat messages
 */
export function clearMessages() {
  chatMessages.set([]);
}

// Initialize isLoggedIn and user data based on the presence of a token and user data in localStorage
if (browser) {
  const storedToken = localStorage.getItem('token');
  const storedUser = localStorage.getItem('user');
  isLoggedIn.set(!!storedToken);
  if (storedToken && storedUser) {
    token.set(storedToken);
    user.set(JSON.parse(storedUser));
  }
}

export const auth = {
  /**
   * @param {string} email
   * @param {string} password
   */
  login: async (email, password) => {
    try {
      const response = await fetch(`${API_URL}/auth/login`, {
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
      setToken(data.token);
      setUser(data.user);
      return data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },

  logout: async () => {
    try {
      const response = await fetch(`${API_URL}/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${get(token)}`,
        },
      });

      if (!response.ok) {
        throw new Error('Logout failed');
      }

      clearAuth();
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  },

  /**
   * @param {string} username
   * @param {string} email
   * @param {string} password
   */
  register: async (username, email, password) => {
    try {
      const response = await fetch(`${API_URL}/auth/register`, {
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
      setToken(data.token);
      setUser(data.user);
      return data;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  },
};

import { writable } from 'svelte/store';
import { browser } from '$app/environment';

/** @type {import('svelte/store').Writable<string | null>} */
export const token = writable(browser ? localStorage.getItem('token') : null);

/** @type {import('svelte/store').Writable<boolean>} */
export const isLoggedIn = writable(false);

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

// Initialize isLoggedIn based on the presence of a token
if (browser) {
  isLoggedIn.set(!!localStorage.getItem('token'));
}

import { writable } from 'svelte/store';

export const isLoggedIn = writable(false);
export const token = writable(null);
export const user = writable(null);
export const chatMessages = writable([]);
export const currentConversation = writable(null);

export function setToken(newToken) {
  token.set(newToken);
}

export function setUser(newUser) {
  user.set(newUser);
}

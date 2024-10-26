import { writable } from 'svelte/store';

export const isLoggedIn = writable(false);
export const authSessionId = writable<string | null>(null);

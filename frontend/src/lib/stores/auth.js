import { writable } from 'svelte/store';

function createAuth() {
    const { subscribe, set, update } = writable({
        isAuthenticated: false,
        user: null
    });

    return {
        subscribe,
        init: async () => {
            // TODO: Implement actual authentication check
            console.log('Auth initialized');
        },
        checkAuth: () => {
            // TODO: Implement actual authentication check
            update(state => ({ ...state, isAuthenticated: true }));
        },
        logout: () => {
            set({ isAuthenticated: false, user: null });
        }
    };
}

export const auth = createAuth();

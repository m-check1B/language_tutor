import { writable } from 'svelte/store';

interface AuthStore {
    token: string | null;
    isLoggedIn: boolean;
}

function createAuthStore() {
    const { subscribe, set, update } = writable<AuthStore>({
        token: null,
        isLoggedIn: false
    });

    return {
        subscribe,
        login: (token: string) => {
            set({ token, isLoggedIn: true });
        },
        logout: () => {
            set({ token: null, isLoggedIn: false });
        }
    };
}

export const auth = createAuthStore();
export const authSessionId = writable<string | null>(null);

import { writable } from 'svelte/store';

function createThemeStore() {
    const { subscribe, set, update } = writable<boolean>(false); // false = light, true = dark

    return {
        subscribe,
        set,
        toggle: () => update(n => !n)
    };
}

export const theme = createThemeStore();

import { writable } from 'svelte/store';
import { browser } from '$app/environment';

function createThemeStore() {
    // Initialize with system preference or saved theme
    const prefersDark = browser && window.matchMedia('(prefers-color-scheme: dark)').matches;
    const savedTheme = browser && localStorage.getItem('theme');
    const initialValue = savedTheme ? savedTheme === 'dark' : prefersDark;

    const { subscribe, set, update } = writable(initialValue);

    return {
        subscribe,
        toggle: () => {
            update(isDark => {
                const newValue = !isDark;
                if (browser) {
                    if (newValue) {
                        document.documentElement.classList.add('dark');
                        localStorage.setItem('theme', 'dark');
                    } else {
                        document.documentElement.classList.remove('dark');
                        localStorage.setItem('theme', 'light');
                    }
                }
                return newValue;
            });
        },
        set: (isDark: boolean) => {
            set(isDark);
            if (browser) {
                if (isDark) {
                    document.documentElement.classList.add('dark');
                    localStorage.setItem('theme', 'dark');
                } else {
                    document.documentElement.classList.remove('dark');
                    localStorage.setItem('theme', 'light');
                }
            }
        }
    };
}

export const theme = createThemeStore();

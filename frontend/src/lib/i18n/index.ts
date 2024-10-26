import { browser } from '$app/environment';
import { init, register, waitLocale } from 'svelte-i18n';

const defaultLocale = 'en';

const locales = import.meta.glob('./*.json', { eager: true });

const load = async (locale: string) => {
    const key = `./${locale}.json`;
    if (key in locales) {
        return (locales[key] as any).default;
    }
    throw new Error(`Locale ${locale} not found`);
};

export const setupI18n = async ({ withLocale: _locale } = { withLocale: defaultLocale }) => {
    // Register all locales
    register('en', () => load('en'));
    register('cs', () => load('cs'));
    register('es', () => load('es'));

    // Initialize with fallback and initial locale
    await init({
        fallbackLocale: defaultLocale,
        initialLocale: browser ? _locale : defaultLocale,
    });

    // Wait for the locale to be loaded
    if (browser) {
        await waitLocale(_locale);
    }
};

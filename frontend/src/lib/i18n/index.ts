import { browser } from '$app/environment';
import { init, register, getLocaleFromNavigator } from 'svelte-i18n';
import { derived, writable } from 'svelte/store';

const defaultLocale = 'en';
export const locale = writable(defaultLocale);
export const locales = {
    en: 'English',
    cs: 'Čeština',
    es: 'Español'
};

// Initialize translations
function setupI18n({ withLocale: _locale } = { withLocale: defaultLocale }) {
    // Register translations
    register('en', () => import('./en.json'));
    register('cs', () => import('./cs.json'));
    register('es', () => import('./es.json'));

    init({
        fallbackLocale: defaultLocale,
        initialLocale: _locale
    });
}

// Load translations
export async function loadTranslations(newLocale: string) {
    if (!Object.keys(locales).includes(newLocale)) {
        newLocale = defaultLocale;
    }

    // If we're in the browser, update the locale
    if (browser) {
        locale.set(newLocale);
    }

    setupI18n({ withLocale: newLocale });
}

// If we're in the browser, setup with the default locale
if (browser) {
    setupI18n();
}

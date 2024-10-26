import { browser } from '$app/environment';
import { init, register } from 'svelte-i18n';

const defaultLocale = 'en';

const load = async (locale: string) => {
    const module = await import(`./${locale}.json`);
    return module.default;
};

export const setupI18n = async ({ withLocale: _locale } = { withLocale: defaultLocale }) => {
    register('en', () => load('en'));
    register('cs', () => load('cs'));
    register('es', () => load('es'));

    await init({
        fallbackLocale: defaultLocale,
        initialLocale: browser ? window.navigator.language.split('-')[0] : defaultLocale,
    });
};

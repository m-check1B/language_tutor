import type { LayoutLoad } from './$types';
import { init, register } from 'svelte-i18n';
import { browser } from '$app/environment';

const defaultLocale = 'en';
const locales = ['en', 'cs', 'es'];

export const load: LayoutLoad = async ({ params }) => {
    const { lang } = params;
    const locale = locales.includes(lang) ? lang : defaultLocale;

    if (browser) {
        register('en', () => import('$lib/i18n/en.json'));
        register('cs', () => import('$lib/i18n/cs.json'));
        register('es', () => import('$lib/i18n/es.json'));

        init({
            fallbackLocale: defaultLocale,
            initialLocale: locale
        });
    }

    return {
        lang: locale,
        form: null
    };
};

import type { LayoutLoad } from './$types';
import { init } from 'svelte-i18n';

const defaultLocale = 'en';
const locales = ['en', 'cs', 'es'];

export const load: LayoutLoad = async ({ params }) => {
    const { lang } = params;
    const locale = locales.includes(lang) ? lang : defaultLocale;

    // Update the locale when it changes
    init({
        fallbackLocale: defaultLocale,
        initialLocale: locale
    });

    return {
        lang: locale
    };
};

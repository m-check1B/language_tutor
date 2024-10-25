import type { LayoutLoad } from './$types';
import { redirect } from '@sveltejs/kit';
import { init, register } from 'svelte-i18n';

// Register translations
register('en', () => import('$lib/i18n/en.json'));
register('cs', () => import('$lib/i18n/cs.json'));
register('es', () => import('$lib/i18n/es.json'));

// Initialize with default locale
init({
    fallbackLocale: 'en',
    initialLocale: 'en'
});

export const load: LayoutLoad = async ({ url }) => {
    // If we're at the root, redirect to the default language (en)
    if (url.pathname === '/') {
        throw redirect(307, '/en');
    }
};

export const ssr = true;
export const prerender = false;

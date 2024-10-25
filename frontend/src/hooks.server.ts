import type { Handle } from '@sveltejs/kit';
import { init, register } from 'svelte-i18n';
import { redirect } from '@sveltejs/kit';

register('en', () => import('$lib/i18n/en.json'));
register('cs', () => import('$lib/i18n/cs.json'));
register('es', () => import('$lib/i18n/es.json'));

init({
    fallbackLocale: 'en',
    initialLocale: 'en'
});

const supportedLangs = ['en', 'cs', 'es'];

export const handle: Handle = async ({ event, resolve }) => {
    const { pathname } = event.url;
    const langPrefix = pathname.split('/')[1];

    // If accessing root, redirect to default language
    if (pathname === '/') {
        throw redirect(307, '/en');
    }

    // If accessing a route without language prefix, redirect to default language version
    if (!supportedLangs.includes(langPrefix) && pathname !== '/') {
        const newPath = `/en${pathname}`;
        throw redirect(307, newPath);
    }

    const response = await resolve(event);
    return response;
};

import type { Handle } from '@sveltejs/kit';
import { init, register } from 'svelte-i18n';

register('en', () => import('$lib/i18n/en.json'));
register('cs', () => import('$lib/i18n/cs.json'));
register('es', () => import('$lib/i18n/es.json'));

init({
    fallbackLocale: 'en',
    initialLocale: 'en'
});

export const handle: Handle = async ({ event, resolve }) => {
    const response = await resolve(event);
    return response;
};

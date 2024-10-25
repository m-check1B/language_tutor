import { redirect } from '@sveltejs/kit';
import type { RequestEvent } from '@sveltejs/kit';

export const load = async ({ url }: RequestEvent) => {
    // Redirect root path to English version
    if (url.pathname === '/') {
        throw redirect(307, '/en');
    }
    
    // For all other paths, redirect to the English version of that path
    throw redirect(307, '/en' + url.pathname);
};

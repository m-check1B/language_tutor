import type { LayoutLoad } from './$types';
import { redirect } from '@sveltejs/kit';

export const load: LayoutLoad = async ({ url }) => {
    // If we're at the root, redirect to the default language (en)
    if (url.pathname === '/') {
        throw redirect(307, '/en');
    }
};

export const ssr = true;
export const prerender = false;

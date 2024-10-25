import { redirect } from '@sveltejs/kit';
import type { RequestEvent } from '@sveltejs/kit';

export const load = async ({ url }: RequestEvent) => {
    throw redirect(307, '/en/login');
};

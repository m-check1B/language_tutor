import { redirect } from '@sveltejs/kit';
import type { LoadEvent } from '@sveltejs/kit';

interface ParentData {
    auth: {
        token: string | null;
    };
}

export const load = async ({ parent }: LoadEvent) => {
    const { auth } = await parent() as ParentData;
    
    if (!auth?.token) {
        throw redirect(302, '/[lang]/login');
    }

    return {
        auth
    };
};

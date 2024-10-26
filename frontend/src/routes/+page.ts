import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
    return {
        form: {
            lang: 'en' // Default language
        }
    };
};

<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { browser } from '$app/environment';

    onMount(() => {
        if (browser) {
            // Get browser language or default to 'en'
            const lang = navigator.language.split('-')[0] || 'en';
            // Only redirect if we're on the root path
            if (window.location.pathname === '/') {
                goto(`/${lang}`);
            }
        }
    });
</script>

<div class="min-h-screen flex items-center justify-center">
    <div class="text-center">
        <div class="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto"></div>
        <p class="mt-4 text-lg text-gray-600 dark:text-gray-300">Loading...</p>
    </div>
</div>

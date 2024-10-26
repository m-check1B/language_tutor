<script lang="ts">
    import '../app.css';
    import { onMount } from 'svelte';
    import { browser } from '$app/environment';
    import { theme } from '$lib/stores/theme';
    import { setupI18n } from '$lib/i18n';
    import { page } from '$app/stores';
    import { locale } from 'svelte-i18n';

    // Initialize i18n immediately with a default locale
    onMount(async () => {
        const initialLocale = $page?.params?.lang || 'en';
        await setupI18n({ withLocale: initialLocale });
    });

    // Update locale when URL changes
    $: if (browser && $page?.params?.lang && $locale !== $page.params.lang) {
        setupI18n({ withLocale: $page.params.lang });
    }

    onMount(() => {
        if (browser) {
            // Check system preference first
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const savedTheme = localStorage.getItem('theme');
            const isDark = savedTheme ? savedTheme === 'dark' : prefersDark;
            
            theme.set(isDark);
            document.documentElement.classList.toggle('dark', isDark);
        }
    });

    $: if (browser && $theme !== undefined) {
        document.documentElement.classList.toggle('dark', $theme);
        localStorage.setItem('theme', $theme ? 'dark' : 'light');
    }
</script>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white">
    <slot />
</div>

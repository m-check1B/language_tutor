<script lang="ts">
    import '../app.css';
    import { onMount } from 'svelte';
    import { browser } from '$app/environment';
    import { theme } from '$lib/stores/theme';

    onMount(() => {
        if (browser) {
            // Check system preference first
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const savedTheme = localStorage.getItem('theme');
            const isDark = savedTheme ? savedTheme === 'dark' : prefersDark;
            
            theme.set(isDark);
        }
    });
</script>

<slot />

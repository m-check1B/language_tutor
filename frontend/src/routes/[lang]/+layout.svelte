<script lang="ts">
    import { page } from '$app/stores';
    import { _ } from 'svelte-i18n';
    import { auth } from '$lib/stores/auth';
    import ThemeToggle from '$lib/components/ThemeToggle.svelte';
    import LanguageSwitcher from '$lib/components/LanguageSwitcher.svelte';
    import '../../app.css';

    $: currentLang = $page.params.lang;
    $: isAuthenticated = !!$auth?.token;
</script>

<div class="min-h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
    <nav class="bg-blue-600 dark:bg-blue-800 text-white p-4 shadow-lg">
        <div class="max-w-7xl mx-auto flex justify-between items-center">
            <div class="flex items-center space-x-4">
                <a href="/{currentLang}" class="flex items-center space-x-2">
                    <img src="/logo.png" alt="Language Tutor Logo" class="h-8 w-8" />
                    <span class="text-xl font-bold">Language Tutor</span>
                </a>
                {#if isAuthenticated}
                    <a 
                        href="/{currentLang}/chat"
                        class="px-3 py-2 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-900 transition-colors"
                        class:bg-blue-700={$page.url.pathname.includes('/chat')}
                    >
                        <div class="flex items-center space-x-2">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clip-rule="evenodd" />
                            </svg>
                            <span>{$_('chat.title')}</span>
                        </div>
                    </a>
                {/if}
            </div>
            
            <div class="flex items-center space-x-4">
                <LanguageSwitcher />
                <ThemeToggle />
                
                {#if isAuthenticated}
                    <button 
                        on:click={() => auth.logout()}
                        class="px-3 py-2 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-900 transition-colors flex items-center space-x-2"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M3 3a1 1 0 00-1 1v12a1 1 0 102 0V4a1 1 0 00-1-1zm10.293 9.293a1 1 0 001.414 1.414l3-3a1 1 0 000-1.414l-3-3a1 1 0 10-1.414 1.414L14.586 9H7a1 1 0 100 2h7.586l-1.293 1.293z" clip-rule="evenodd" />
                        </svg>
                        <span>{$_('auth.logout', { default: 'Logout' })}</span>
                    </button>
                {:else}
                    <a 
                        href="/{currentLang}/login"
                        class="px-3 py-2 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-900 transition-colors flex items-center space-x-2"
                        class:bg-blue-700={$page.url.pathname.includes('/login')}
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M3 3a1 1 0 011 1v12a1 1 0 11-2 0V4a1 1 0 011-1zm7.707 3.293a1 1 0 010 1.414L9.414 9H17a1 1 0 110 2H9.414l1.293 1.293a1 1 0 01-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0z" clip-rule="evenodd" />
                        </svg>
                        <span>{$_('auth.login.title')}</span>
                    </a>
                    <a 
                        href="/{currentLang}/register"
                        class="px-3 py-2 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-900 transition-colors flex items-center space-x-2"
                        class:bg-blue-700={$page.url.pathname.includes('/register')}
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path d="M8 9a3 3 0 100-6 3 3 0 000 6zM8 11a6 6 0 016 6H2a6 6 0 016-6zM16 7a1 1 0 10-2 0v1h-1a1 1 0 100 2h1v1a1 1 0 102 0v-1h1a1 1 0 100-2h-1V7z" />
                        </svg>
                        <span>{$_('auth.register.title')}</span>
                    </a>
                {/if}
            </div>
        </div>
    </nav>

    <main class="max-w-7xl mx-auto p-4">
        <slot />
    </main>
</div>

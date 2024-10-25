<script lang="ts">
    import { goto } from '$app/navigation';
    import { isLoggedIn } from '$lib';
    import { _ } from 'svelte-i18n';

    function handleGetStarted() {
        goto('/en/login');
    }
</script>

<div class="max-w-4xl mx-auto p-4">
    <div class="card">
        <h1 class="text-3xl font-bold text-center text-gray-900 dark:text-white mb-6">
            {$_('home.title', { default: 'Welcome to Language Tutor' })}
        </h1>

        <p class="text-lg text-center text-gray-700 dark:text-gray-300 mb-8">
            {$_('home.description', { default: 'Improve your language skills with our AI-powered tutor. Practice conversations, learn grammar, and enhance your vocabulary in a natural way.' })}
        </p>
        
        <div class="flex justify-center">
            {#if !$isLoggedIn}
                <button 
                    on:click={handleGetStarted}
                    class="btn-primary flex items-center gap-2 text-lg px-6 py-3"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clip-rule="evenodd" />
                    </svg>
                    {$_('home.getStarted', { default: 'Get Started' })}
                </button>
            {:else}
                <button 
                    on:click={() => goto('/en/chat')}
                    class="btn-primary flex items-center gap-2 text-lg px-6 py-3"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clip-rule="evenodd" />
                    </svg>
                    {$_('home.continueChat', { default: 'Continue Learning' })}
                </button>
            {/if}
        </div>
    </div>
</div>

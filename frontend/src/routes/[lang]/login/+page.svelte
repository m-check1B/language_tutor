<script lang="ts">
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';
    import { _ } from 'svelte-i18n';
    import { auth } from '$lib/stores/auth';
    import { setupWebSocket } from '$lib/stores/stores';

    let email = '';
    let password = '';
    let error = '';

    async function handleSubmit() {
        error = '';
        try {
            const response = await auth.login(email, password);
            if (response.access_token && response.session_id) {
                auth.setToken(response.access_token, response.session_id);
                await setupWebSocket();
                goto(`/${$page.params.lang}/chat`);
            } else {
                throw new Error('Invalid response from server');
            }
        } catch (err) {
            error = err instanceof Error ? err.message : $_('auth.login.error');
        }
    }
</script>

<div class="max-w-md mx-auto mt-8 px-4">
    <div class="card">
        <h1 class="text-2xl font-bold text-center text-gray-900 dark:text-white mb-6">
            {$_('auth.login.title', { default: 'Login' })}
        </h1>

        <form on:submit|preventDefault={handleSubmit} class="space-y-6">
            <div>
                <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {$_('auth.login.email', { default: 'Email:' })}
                </label>
                <input 
                    type="email" 
                    id="email" 
                    bind:value={email}
                    required 
                    autocomplete="email"
                    placeholder={$_('auth.login.emailPlaceholder', { default: 'Enter your email' })}
                    class="input-field"
                >
            </div>

            <div>
                <label for="password" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {$_('auth.login.password', { default: 'Password:' })}
                </label>
                <input 
                    type="password" 
                    id="password" 
                    bind:value={password}
                    required 
                    autocomplete="current-password"
                    placeholder={$_('auth.login.passwordPlaceholder', { default: 'Enter your password' })}
                    class="input-field"
                >
            </div>

            <button type="submit" class="btn-primary w-full">
                {$_('auth.login.submit', { default: 'Login' })}
            </button>

            {#if error}
                <p class="text-red-600 dark:text-red-400 text-sm text-center mt-2">
                    {error}
                </p>
            {/if}
        </form>

        <p class="mt-4 text-center text-sm text-gray-600 dark:text-gray-400">
            {$_('auth.login.noAccount', { default: "Don't have an account?" })}
            <a 
                href="/{$page.params.lang}/register" 
                class="font-medium text-blue-600 dark:text-blue-400 hover:text-blue-500 dark:hover:text-blue-300"
            >
                {$_('auth.login.registerLink', { default: 'Register here' })}
            </a>
        </p>
    </div>
</div>

<style lang="postcss">
    .card {
        @apply bg-white dark:bg-gray-800 shadow-lg rounded-lg p-8;
    }

    .input-field {
        @apply w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md 
               shadow-sm placeholder-gray-400 
               focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
               dark:bg-gray-700 dark:text-white;
    }

    .btn-primary {
        @apply bg-blue-600 text-white px-4 py-2 rounded-md font-medium
               hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
               dark:focus:ring-offset-gray-800 transition-colors;
    }
</style>

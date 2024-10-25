<script lang="ts">
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';
    import { _ } from 'svelte-i18n';
    import { auth } from '$lib/stores/auth';

    let email = '';
    let password = '';
    let confirmPassword = '';
    let error = '';

    async function handleSubmit() {
        error = '';
        if (password !== confirmPassword) {
            error = $_('auth.register.passwordMismatch', { default: 'Passwords do not match' });
            return;
        }
        try {
            await auth.register(email, password);
            goto(`/${$page.params.lang}/chat`);
        } catch (err) {
            error = err instanceof Error ? err.message : $_('auth.register.error');
        }
    }
</script>

<div class="max-w-md mx-auto mt-8 px-4">
    <div class="card">
        <h1 class="text-2xl font-bold text-center text-gray-900 dark:text-white mb-6">
            {$_('auth.register.title', { default: 'Register' })}
        </h1>

        <form on:submit|preventDefault={handleSubmit} class="space-y-6">
            <div>
                <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {$_('auth.register.email', { default: 'Email:' })}
                </label>
                <input 
                    type="email" 
                    id="email" 
                    bind:value={email}
                    required 
                    autocomplete="email"
                    placeholder={$_('auth.register.emailPlaceholder', { default: 'Enter your email' })}
                    class="input-field"
                >
            </div>

            <div>
                <label for="password" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {$_('auth.register.password', { default: 'Password:' })}
                </label>
                <input 
                    type="password" 
                    id="password" 
                    bind:value={password}
                    required 
                    autocomplete="new-password"
                    placeholder={$_('auth.register.passwordPlaceholder', { default: 'Enter your password' })}
                    class="input-field"
                >
            </div>

            <div>
                <label for="confirmPassword" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {$_('auth.register.confirmPassword', { default: 'Confirm Password:' })}
                </label>
                <input 
                    type="password" 
                    id="confirmPassword" 
                    bind:value={confirmPassword}
                    required 
                    autocomplete="new-password"
                    placeholder={$_('auth.register.confirmPasswordPlaceholder', { default: 'Confirm your password' })}
                    class="input-field"
                >
            </div>

            <button type="submit" class="btn-primary w-full">
                {$_('auth.register.submit', { default: 'Register' })}
            </button>

            {#if error}
                <p class="text-red-600 dark:text-red-400 text-sm text-center mt-2">
                    {error}
                </p>
            {/if}
        </form>

        <p class="mt-4 text-center text-sm text-gray-600 dark:text-gray-400">
            {$_('auth.register.haveAccount', { default: 'Already have an account?' })}
            <a 
                href="/{$page.params.lang}/login" 
                class="font-medium text-blue-600 dark:text-blue-400 hover:text-blue-500 dark:hover:text-blue-300"
            >
                {$_('auth.register.loginLink', { default: 'Login here' })}
            </a>
        </p>
    </div>
</div>

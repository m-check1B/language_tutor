<script lang="ts">
    import { onMount } from 'svelte';
    import { _ } from 'svelte-i18n';
    import { isLoggedIn } from '$lib/stores/auth';
    import ChatInterface from '$lib/components/ChatInterface.svelte';
    import AgentsManagement from '$lib/components/AgentsManagement.svelte';
</script>

<div class="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-gray-900 dark:to-gray-800">
    {#if !$isLoggedIn}
        <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
            <div class="text-center">
                <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-4">
                    {$_('chat.loginRequired', { default: 'Please log in to access the chat' })}
                </h1>
                <a 
                    href="/login"
                    class="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                    {$_('chat.login', { default: 'Log In' })}
                </a>
            </div>
        </div>
    {:else}
        <div class="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div class="grid grid-cols-1 lg:grid-cols-4 gap-8">
                <!-- Left Sidebar - Agents Management -->
                <div class="lg:col-span-1">
                    <AgentsManagement />
                </div>

                <!-- Main Content - Chat Interface -->
                <div class="lg:col-span-3">
                    <ChatInterface />
                </div>
            </div>
        </div>
    {/if}
</div>

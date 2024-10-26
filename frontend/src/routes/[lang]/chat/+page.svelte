<script lang="ts">
    import { onMount } from 'svelte';
    import { _ } from 'svelte-i18n';
    import { auth } from '$lib/stores/auth';
    import { page } from '$app/stores';
    import ChatInterface from '$lib/components/ChatInterface.svelte';
    import AgentsManagement from '$lib/components/AgentsManagement.svelte';
    import ConversationsManagement from '$lib/components/ConversationsManagement.svelte';
    import { setupWebSocket, disconnectWebSocket, wsConnection } from '$lib/stores/stores';

    $: currentLang = $page.params.lang;
    let connectionAttempts = 0;
    const MAX_CONNECTION_ATTEMPTS = 3;

    async function initializeWebSocket() {
        if ($auth.isLoggedIn && $auth.token && $auth.sessionId && !$wsConnection.isConnected) {
            try {
                await setupWebSocket();
                connectionAttempts = 0; // Reset attempts on successful connection
            } catch (error) {
                console.error('WebSocket connection error:', error);
                connectionAttempts++;
                
                if (connectionAttempts < MAX_CONNECTION_ATTEMPTS) {
                    // Retry after a delay
                    setTimeout(initializeWebSocket, 2000);
                }
            }
        }
    }

    onMount(() => {
        initializeWebSocket();
        return () => {
            disconnectWebSocket();
        };
    });

    // Watch for auth changes and reinitialize WebSocket if needed
    $: if ($auth.isLoggedIn && $auth.token && $auth.sessionId && !$wsConnection.isConnected) {
        initializeWebSocket();
    }
</script>

<div class="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-gray-900 dark:to-gray-800">
    {#if !$auth.isLoggedIn}
        <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
            <div class="text-center">
                <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-4">
                    {$_('chat.loginRequired', { default: 'Please log in to access the chat' })}
                </h1>
                <a 
                    href="/{currentLang}/login"
                    class="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                    {$_('chat.login', { default: 'Log In' })}
                </a>
            </div>
        </div>
    {:else}
        <div class="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div class="grid grid-cols-1 lg:grid-cols-4 gap-8">
                <!-- Left Sidebar - Agents and Conversations Management -->
                <div class="lg:col-span-1">
                    <div class="space-y-6">
                        <AgentsManagement />
                        <ConversationsManagement />
                    </div>
                </div>

                <!-- Main Content - Chat Interface -->
                <div class="lg:col-span-3">
                    {#if !$wsConnection.isConnected}
                        <div class="bg-yellow-100 dark:bg-yellow-900 p-4 rounded-lg mb-4">
                            <p class="text-yellow-800 dark:text-yellow-200">
                                {$_('chat.connecting', { default: 'Connecting to chat server...' })}
                            </p>
                        </div>
                    {/if}
                    <ChatInterface />
                </div>
            </div>
        </div>
    {/if}
</div>

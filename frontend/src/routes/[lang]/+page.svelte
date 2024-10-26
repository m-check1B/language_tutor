<script lang="ts">
    import { onMount } from 'svelte';
    import { _ } from 'svelte-i18n';
    import { isLoggedIn } from '$lib/stores';
    import { page } from '$app/stores';
    import ChatInterface from '$lib/components/ChatInterface.svelte';
    import AgentsManagement from '$lib/components/AgentsManagement.svelte';
</script>

<div class="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-gray-900 dark:to-gray-800">
    {#if !$isLoggedIn}
        <!-- Welcome Section -->
        <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
            <div class="relative bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-2xl shadow-xl overflow-hidden">
                <div class="absolute inset-0">
                    <div class="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-purple-500/10 dark:from-blue-500/5 dark:to-purple-500/5" />
                    <div class="absolute top-0 left-0 w-40 h-40 bg-blue-500/10 rounded-full -translate-x-1/2 -translate-y-1/2 blur-2xl" />
                    <div class="absolute bottom-0 right-0 w-40 h-40 bg-purple-500/10 rounded-full translate-x-1/2 translate-y-1/2 blur-2xl" />
                </div>
                
                <div class="relative px-8 py-12 sm:px-12 sm:py-16">
                    <div class="max-w-3xl mx-auto text-center">
                        <h1 class="text-4xl sm:text-5xl font-bold text-gray-900 dark:text-white mb-8 bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400">
                            {$_('home.title', { default: 'Welcome to Language Tutor' })}
                        </h1>

                        <p class="text-xl text-gray-600 dark:text-gray-300 mb-12 leading-relaxed">
                            {$_('home.description', { default: 'Improve your language skills with our AI-powered tutor. Practice conversations, learn grammar, and enhance your vocabulary in a natural way.' })}
                        </p>
                        
                        <a 
                            href="/{$page.params.lang}/login"
                            class="inline-flex items-center px-8 py-4 text-lg font-medium rounded-xl text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-2" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clip-rule="evenodd" />
                            </svg>
                            {$_('home.getStarted', { default: 'Get Started' })}
                        </a>
                    </div>
                </div>
            </div>
        </div>
    {:else}
        <!-- Main Language Tutor Interface -->
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

<script lang="ts">
    import { _ } from 'svelte-i18n';
    import { page } from '$app/stores';
    import { isLoggedIn } from '$lib/stores';
    import { chatStore } from '$lib/stores/chat';
    import ChatMessage from '$lib/components/ChatMessage.svelte';
    import MediaInterface from '$lib/components/MediaInterface.svelte';
    import { onMount, onDestroy } from 'svelte';

    let message = '';
    let chatContainer: HTMLDivElement;
    let showMediaInterface = false;

    $: if (chatContainer && $chatStore.messages.length > 0) {
        setTimeout(() => {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }, 0);
    }

    onMount(() => {
        chatStore.connect();
    });

    onDestroy(() => {
        chatStore.disconnect();
    });

    async function handleSubmit() {
        if (!message.trim() && !$chatStore.audioBlob) return;

        try {
            if ($chatStore.audioBlob) {
                const data = await chatStore.sendAudio($chatStore.audioBlob);
                if (data) {
                    chatStore.addMessage('', true, URL.createObjectURL($chatStore.audioBlob));
                    chatStore.addMessage(data.response, false);
                }
                chatStore.clearAudioBlob();
            } else {
                chatStore.addMessage(message, true);
                await chatStore.sendMessage(message);
            }

            message = '';
        } catch (error) {
            console.error('Error:', error);
        }
    }

    async function toggleRecording() {
        if ($chatStore.isRecording) {
            chatStore.stopRecording();
        } else {
            try {
                await chatStore.startRecording();
            } catch (error) {
                console.error('Error accessing microphone:', error);
            }
        }
    }
</script>

<div class="max-w-4xl mx-auto p-4">
    <div class="card mb-4">
        <div class="flex justify-between items-center mb-6">
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
                {$_('chat.title', { default: 'Language Tutor Chat' })}
            </h1>
            <button 
                class="btn-secondary"
                on:click={() => showMediaInterface = !showMediaInterface}
            >
                {showMediaInterface ? $_('chat.hideMedia', { default: 'Hide Media Tools' }) : $_('chat.showMedia', { default: 'Show Media Tools' })}
            </button>
        </div>

        {#if showMediaInterface}
            <div class="mb-4">
                <MediaInterface />
            </div>
        {/if}

        <div 
            bind:this={chatContainer}
            class="chat-messages min-h-[400px] max-h-[600px] overflow-y-auto bg-gray-50 dark:bg-gray-800 rounded-lg p-4 mb-4"
        >
            {#each $chatStore.messages as msg (msg.id)}
                <ChatMessage {...msg} />
            {/each}
        </div>

        <form on:submit|preventDefault={handleSubmit} class="flex gap-2">
            <input 
                type="text" 
                bind:value={message}
                placeholder={$_('chat.messagePlaceholder', { default: 'Type your message...' })}
                class="input-field flex-grow"
                disabled={$chatStore.isRecording}
            >
            <button 
                type="button" 
                class="btn-secondary flex items-center gap-2"
                class:bg-red-500={$chatStore.isRecording}
                class:hover:bg-red-600={$chatStore.isRecording}
                on:click={toggleRecording}
            >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    {#if $chatStore.isRecording}
                        <path d="M10 3a1 1 0 011 1v12a1 1 0 11-2 0V4a1 1 0 011-1z" />
                        <path d="M4 8a1 1 0 011-1h2a1 1 0 010 2H5a1 1 0 01-1-1z" />
                        <path d="M14 8a1 1 0 100 2h2a1 1 0 100-2h-2z" />
                    {:else}
                        <path fill-rule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clip-rule="evenodd" />
                    {/if}
                </svg>
                {#if $chatStore.isRecording}
                    {$_('chat.stopRecording', { default: 'Stop Recording' })}
                {:else}
                    {$_('chat.startRecording', { default: 'Start Recording' })}
                {/if}
            </button>
            <button 
                type="submit" 
                class="btn-primary flex items-center gap-2"
                disabled={!message.trim() && !$chatStore.audioBlob}
            >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                </svg>
                {$_('chat.send', { default: 'Send' })}
            </button>
        </form>
    </div>
</div>

<style>
    .card {
        @apply bg-white dark:bg-gray-900 rounded-lg shadow-lg p-6;
    }

    .input-field {
        @apply px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
               bg-white dark:bg-gray-800 text-gray-900 dark:text-white;
    }

    .btn-primary {
        @apply px-4 py-2 bg-blue-500 text-white rounded-lg 
               hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed
               transition-colors duration-200;
    }

    .btn-secondary {
        @apply px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white 
               rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600
               transition-colors duration-200;
    }

    .chat-messages {
        scrollbar-width: thin;
        scrollbar-color: rgba(156, 163, 175, 0.5) transparent;
    }

    .chat-messages::-webkit-scrollbar {
        width: 6px;
    }

    .chat-messages::-webkit-scrollbar-track {
        background: transparent;
    }

    .chat-messages::-webkit-scrollbar-thumb {
        background-color: rgba(156, 163, 175, 0.5);
        border-radius: 3px;
    }
</style>

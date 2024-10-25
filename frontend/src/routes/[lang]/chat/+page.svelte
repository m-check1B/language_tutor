<script lang="ts">
    import { _ } from 'svelte-i18n';
    import { page } from '$app/stores';
    import { auth } from '$lib/stores';
    import { chatStore } from '$lib/stores/chat';
    import ChatMessage from '$lib/components/ChatMessage.svelte';
    import { onMount, onDestroy } from 'svelte';

    let message = '';
    let chatContainer: HTMLDivElement;

    $: if (chatContainer && $chatStore.messages.length > 0) {
        // Scroll to bottom when new messages arrive
        setTimeout(() => {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }, 0);
    }

    onMount(() => {
        // Initialize WebSocket connection
        chatStore.connect();
    });

    onDestroy(() => {
        // Clean up WebSocket connection
        chatStore.disconnect();
    });

    async function handleSubmit() {
        if (!message.trim() && !$chatStore.audioBlob) return;

        try {
            if ($chatStore.audioBlob) {
                // Send audio message
                const data = await chatStore.sendAudio($chatStore.audioBlob);
                if (data) {
                    chatStore.addMessage('', true, URL.createObjectURL($chatStore.audioBlob));
                    chatStore.addMessage(data.response, false);
                }
                chatStore.clearAudioBlob();
            } else {
                // Send text message
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
        <h1 class="text-2xl font-bold text-center text-gray-900 dark:text-white mb-6">
            {$_('chat.title', { default: 'Language Tutor Chat' })}
        </h1>

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

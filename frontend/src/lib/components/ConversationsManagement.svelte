<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import { chatHistory } from '../stores/stores';
  import { auth, authToken, authSessionId } from '../stores/auth';
  import { get } from 'svelte/store';

  let isLoading: boolean = true;
  let conversations: any[] = [];
  let selectedConversation: any = null;
  const dispatch = createEventDispatcher();

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api';

  interface Conversation {
    id: number;
    title: string;
    messages: Array<{ text: string; isUser: boolean; audioUrl?: string }>;
    created_at: string;
  }

  async function loadConversations() {
    try {
      const token = get(authToken);
      const sessionId = get(authSessionId);
      
      if (!token || !sessionId) {
        console.error('Missing auth token or session ID');
        return;
      }

      const response = await fetch(`${API_URL}/chat/conversations`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId
        },
        credentials: 'include'
      });
      if (response.ok) {
        conversations = await response.json();
      } else {
        const error = await response.json();
        console.error('Failed to load conversations:', error);
      }
    } catch (error) {
      console.error('Failed to load conversations:', error);
    } finally {
      isLoading = false;
    }
  }

  async function handleSelectConversation(conversation: Conversation) {
    selectedConversation = conversation;
    chatHistory.set(conversation.messages);
  }

  async function handleDeleteConversation(id: number) {
    try {
      const token = get(authToken);
      const sessionId = get(authSessionId);
      
      if (!token || !sessionId) {
        console.error('Missing auth token or session ID');
        return;
      }

      const response = await fetch(`${API_URL}/chat/conversations/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId
        },
        credentials: 'include'
      });
      if (response.ok) {
        conversations = conversations.filter(c => c.id !== id);
        if (selectedConversation?.id === id) {
          selectedConversation = null;
          chatHistory.set([]);
        }
      } else {
        const error = await response.json();
        console.error('Failed to delete conversation:', error);
      }
    } catch (error) {
      console.error('Failed to delete conversation:', error);
    }
  }

  onMount(() => {
    if (get(auth).isLoggedIn) {
      loadConversations();
    }
  });

  $: if ($auth.isLoggedIn && $authToken && $authSessionId) {
    loadConversations();
  }

  function handleKeyDown(event: KeyboardEvent, conversation: Conversation) {
    if (event.key === 'Enter' || event.key === ' ') {
      handleSelectConversation(conversation);
    }
  }
</script>

<div class="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-2xl shadow-xl p-6 mt-6">
  <h2 class="text-xl font-bold mb-4 text-gray-900 dark:text-white">Conversations</h2>

  {#if isLoading}
    <div class="text-center text-gray-600 dark:text-gray-300">
      Loading conversations...
    </div>
  {:else if conversations.length === 0}
    <div class="text-center text-gray-600 dark:text-gray-300">
      No conversations found.
    </div>
  {:else}
    <div class="grid grid-cols-1 gap-4">
      {#each conversations as conversation (conversation.id)}
        <div class="p-4 rounded-lg border-2 transition-all duration-200">
          <div class="flex justify-between items-center">
            <button
              class="flex-1 text-left {selectedConversation?.id === conversation.id ? 'text-blue-500' : 'text-gray-900 dark:text-white'}"
              on:click={() => handleSelectConversation(conversation)}
              on:keydown={(e) => handleKeyDown(e, conversation)}
            >
              <h3 class="font-medium">{conversation.title}</h3>
              <p class="text-sm opacity-75">{new Date(conversation.created_at).toLocaleString()}</p>
            </button>
            <button
              class="p-2 text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
              on:click={() => handleDeleteConversation(conversation.id)}
              aria-label="Delete conversation"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

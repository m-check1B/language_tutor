<script lang="ts">
  import { onMount } from 'svelte';
  import { _ } from 'svelte-i18n';

  let messages = [];
  let newMessage = '';
  let selectedLanguage = 'en';
  let conversationId: number | null = null;

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'es', name: 'Spanish' },
    { code: 'fr', name: 'French' },
    // Add more languages as needed
  ];

  onMount(async () => {
    await createConversation();
  });

  async function createConversation() {
    try {
      const response = await fetch(`${API_BASE_URL}/conversation/test/conversations`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to create conversation');
      const data = await response.json();
      conversationId = data.id;
    } catch (error) {
      console.error('Error creating conversation:', error);
    }
  }

  async function sendMessage() {
    if (newMessage.trim() && conversationId) {
      try {
        const response = await fetch(`${API_BASE_URL}/conversation/test/conversations/${conversationId}/messages`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ content: newMessage }),
        });
        if (!response.ok) throw new Error('Failed to send message');
        const newMessages = await response.json();
        messages = [...messages, ...newMessages];
        newMessage = '';
      } catch (error) {
        console.error('Error sending message:', error);
      }
    }
  }
</script>

<div class="chat-interface">
  <div class="language-selector">
    <label for="language-select">{$_('selectLanguage')}</label>
    <select id="language-select" bind:value={selectedLanguage}>
      {#each languages as language}
        <option value={language.code}>{language.name}</option>
      {/each}
    </select>
  </div>

  <div class="messages">
    {#each messages as message}
      <div class="message {message.is_user ? 'user' : 'assistant'}">
        <p>{message.content}</p>
      </div>
    {/each}
  </div>

  <div class="input-area">
    <input
      type="text"
      bind:value={newMessage}
      placeholder={$_('typeYourMessage')}
      on:keypress={(e) => e.key === 'Enter' && sendMessage()}
    />
    <button on:click={sendMessage}>{$_('send')}</button>
  </div>
</div>

<style>
  .chat-interface {
    display: flex;
    flex-direction: column;
    height: 500px;
    border: 1px solid #ccc;
    border-radius: 5px;
  }

  .language-selector {
    padding: 10px;
    border-bottom: 1px solid #ccc;
  }

  .messages {
    flex-grow: 1;
    overflow-y: auto;
    padding: 10px;
  }

  .message {
    margin-bottom: 10px;
    padding: 5px 10px;
    border-radius: 5px;
  }

  .user {
    background-color: #e6f3ff;
    align-self: flex-end;
  }

  .assistant {
    background-color: #f0f0f0;
    align-self: flex-start;
  }

  .input-area {
    display: flex;
    padding: 10px;
    border-top: 1px solid #ccc;
  }

  input {
    flex-grow: 1;
    padding: 5px;
    margin-right: 10px;
  }

  button {
    padding: 5px 10px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 3px;
    cursor: pointer;
  }
</style>

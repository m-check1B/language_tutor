<script lang="ts">
  import { onMount } from 'svelte';
  import { _ } from 'svelte-i18n';
  import { user } from '../../stores';
  import { page } from '$app/stores';

  let messages = [];
  let newMessage = '';
  let conversationId = null;
  let audioElement: HTMLAudioElement;

  $: lang = $page.params.lang || 'en';

  onMount(async () => {
    await createConversation();
    audioElement = new Audio();
  });

  async function createConversation() {
    try {
      const response = await fetch('/api/conversations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${$user.token}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        conversationId = data.id;
      } else {
        console.error('Failed to create conversation');
      }
    } catch (error) {
      console.error('Error creating conversation:', error);
    }
  }

  async function sendMessage() {
    if (!newMessage.trim() || !conversationId) return;

    try {
      const response = await fetch(`/api/conversations/${conversationId}/messages?lang=${lang}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${$user.token}`
        },
        body: JSON.stringify({ content: newMessage })
      });

      if (response.ok) {
        const data = await response.json();
        messages = [...messages, ...data];
        newMessage = '';
        
        // Play audio if available
        if (data[1].audio_content) {
          const audioBlob = new Blob([data[1].audio_content], { type: 'audio/mp3' });
          audioElement.src = URL.createObjectURL(audioBlob);
          audioElement.play();
        }
      } else {
        console.error('Failed to send message');
      }
    } catch (error) {
      console.error('Error sending message:', error);
    }
  }
</script>

<div class="chat-interface">
  <div class="messages">
    {#each messages as message}
      <div class={message.is_user ? 'user-message' : 'ai-message'}>
        <p>{message.content}</p>
        {#if !message.is_user && message.audio_content}
          <button on:click={() => audioElement.play()}>
            {$_('playAudio')}
          </button>
        {/if}
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
    height: 100%;
  }

  .messages {
    flex-grow: 1;
    overflow-y: auto;
    padding: 1rem;
  }

  .user-message, .ai-message {
    margin-bottom: 1rem;
    padding: 0.5rem;
    border-radius: 0.5rem;
  }

  .user-message {
    background-color: #e6f3ff;
    align-self: flex-end;
  }

  .ai-message {
    background-color: #f0f0f0;
    align-self: flex-start;
  }

  .input-area {
    display: flex;
    padding: 1rem;
  }

  input {
    flex-grow: 1;
    padding: 0.5rem;
    margin-right: 0.5rem;
  }

  button {
    padding: 0.5rem 1rem;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 0.25rem;
    cursor: pointer;
  }

  button:hover {
    background-color: #0056b3;
  }
</style>

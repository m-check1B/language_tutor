<script lang="ts">
  import { onMount } from 'svelte';
  import { _ } from 'svelte-i18n';
  import { user } from '../../stores';
  import { page } from '$app/stores';

  let messages = [];
  let isRecording = false;
  let mediaRecorder;
  let audioChunks = [];
  let conversationId = null;
  let audioElement: HTMLAudioElement;

  $: lang = $page.params.lang || 'en';

  onMount(async () => {
    await createConversation();
    setupMediaRecorder();
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

  function setupMediaRecorder() {
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        mediaRecorder = new MediaRecorder(stream);
        
        mediaRecorder.ondataavailable = (event) => {
          audioChunks.push(event.data);
        };

        mediaRecorder.onstop = sendVoiceMessage;
      })
      .catch(error => console.error('Error accessing microphone:', error));
  }

  function startRecording() {
    if (!isRecording) {
      audioChunks = [];
      mediaRecorder.start();
      isRecording = true;
    }
  }

  function stopRecording() {
    if (isRecording) {
      mediaRecorder.stop();
      isRecording = false;
    }
  }

  async function sendVoiceMessage() {
    if (!conversationId) return;

    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
    const formData = new FormData();
    formData.append('audio_content', audioBlob, 'voice_message.wav');

    try {
      const response = await fetch(`/api/conversations/${conversationId}/voice_messages?lang=${lang}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${$user.token}`
        },
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        messages = [...messages, ...data];
        
        // Play the AI response
        if (data[1].audio_content) {
          const audioBlob = new Blob([data[1].audio_content], { type: 'audio/mp3' });
          audioElement.src = URL.createObjectURL(audioBlob);
          audioElement.play();
        }
      } else {
        console.error('Failed to send voice message');
      }
    } catch (error) {
      console.error('Error sending voice message:', error);
    }
  }
</script>

<div class="voice-interface">
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
    {#if isRecording}
      <button on:click={stopRecording} class="recording">
        {$_('stopRecording')}
      </button>
    {:else}
      <button on:click={startRecording}>
        {$_('startRecording')}
      </button>
    {/if}
  </div>
</div>

<style>
  .voice-interface {
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
    justify-content: center;
    padding: 1rem;
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

  button.recording {
    background-color: #dc3545;
  }

  button.recording:hover {
    background-color: #c82333;
  }
</style>

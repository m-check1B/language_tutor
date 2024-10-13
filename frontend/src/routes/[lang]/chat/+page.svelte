<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { goto } from '$app/navigation';
  import { currentConversation, chatMessages, token } from '../../stores';

  let message = '';
  let ws: WebSocket | null = null;
  let isRecording = false;
  let mediaRecorder: MediaRecorder | null = null;
  let audioChunks: Blob[] = [];
  let errorMessage = '';
  let isConnected = false;
  let reconnectAttempts = 0;
  let isReconnecting = false;
  const MAX_RECONNECT_ATTEMPTS = 5;
  const RECONNECT_INTERVAL = 5000; // 5 seconds
  let failedMessages: Array<{ type: string, content: string }> = [];

  $: messages = $chatMessages;

  onMount(async () => {
    if (!$token) {
      goto('/login');
      return;
    }

    if (!$currentConversation) {
      await startNewConversation();
    }

    connectWebSocket();
  });

  onDestroy(() => {
    closeWebSocket();
    if (mediaRecorder) {
      mediaRecorder.stop();
    }
  });

  async function startNewConversation() {
    try {
      const response = await fetch('http://localhost:8081/livekit/start-conversation', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${$token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        currentConversation.set(data.conversation_id);
      } else {
        throw new Error('Failed to start a new conversation');
      }
    } catch (error) {
      console.error('Error starting new conversation:', error);
      errorMessage = 'Failed to start a new conversation. Please try again.';
    }
  }

  function connectWebSocket() {
    closeWebSocket(); // Close any existing connection before creating a new one
    ws = new WebSocket(`ws://localhost:8081/livekit/ws/chat/${$currentConversation}`);

    ws.onopen = () => {
      console.log('WebSocket connection established');
      isConnected = true;
      isReconnecting = false;
      errorMessage = '';
      reconnectAttempts = 0;
      resendFailedMessages();
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.error) {
        errorMessage = data.error;
      } else {
        chatMessages.update(msgs => [...msgs, { content: data.content, isUser: false, type: data.type }]);
        if (data.type === 'audio') {
          playAudioResponse(data.content);
        }
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      errorMessage = 'Connection error. Attempting to reconnect...';
      isConnected = false;
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed');
      isConnected = false;
      attemptReconnect();
    };
  }

  function closeWebSocket() {
    if (ws) {
      ws.onclose = null; // Remove onclose handler to prevent attemptReconnect from being called
      ws.close();
      ws = null;
    }
  }

  function attemptReconnect() {
    if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
      reconnectAttempts++;
      isReconnecting = true;
      errorMessage = `Connection lost. Attempting to reconnect (${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})...`;
      setTimeout(connectWebSocket, RECONNECT_INTERVAL);
    } else {
      isReconnecting = false;
      errorMessage = 'Failed to reconnect. Please refresh the page to try again.';
    }
  }

  async function sendMessage() {
    if (!isConnected) {
      errorMessage = 'Not connected to the server. Please wait or refresh the page.';
      return;
    }

    if (message.trim()) {
      try {
        await sendMessageToServer('text', message);
        chatMessages.update(msgs => [...msgs, { content: message, isUser: true, type: 'text' }]);
        message = '';
        errorMessage = '';
      } catch (error) {
        console.error('Error sending message:', error);
        errorMessage = 'Failed to send message. It will be resent when connection is restored.';
        failedMessages.push({ type: 'text', content: message });
      }
    }
  }

  async function sendMessageToServer(type: string, content: string) {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket is not open');
    }
    ws.send(JSON.stringify({ type, content }));
  }

  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      audioChunks = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        await sendAudioMessage(audioBlob);
      };

      mediaRecorder.start();
      isRecording = true;
      errorMessage = '';
    } catch (error) {
      console.error('Error starting recording:', error);
      errorMessage = 'Failed to start recording. Please check your microphone permissions.';
    }
  }

  function stopRecording() {
    if (mediaRecorder) {
      mediaRecorder.stop();
      isRecording = false;
    }
  }

  async function sendAudioMessage(audioBlob: Blob) {
    if (!isConnected) {
      errorMessage = 'Not connected to the server. Audio will be sent when connection is restored.';
      failedMessages.push({ type: 'audio', content: await blobToBase64(audioBlob) });
      return;
    }

    try {
      const audioData = await audioBlob.arrayBuffer();
      const response = await fetch('http://localhost:8081/deepgram/transcribe', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${$token}`,
          'Content-Type': 'application/octet-stream',
        },
        body: audioData,
      });

      if (response.ok) {
        const data = await response.json();
        await sendMessageToServer('text', data.transcription); // Send the transcription as a text message
        chatMessages.update(msgs => [...msgs, { content: 'Audio message sent', isUser: true, type: 'audio' }]);
        errorMessage = '';
      } else {
        throw new Error('Failed to send audio message to Deepgram');
      }
    } catch (error) {
      console.error('Error sending audio message:', error);
      errorMessage = 'Failed to send audio message. It will be resent when connection is restored.';
      failedMessages.push({ type: 'audio', content: await blobToBase64(audioBlob) });
    }
  }

  function blobToBase64(blob: Blob): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result as string);
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }

  function playAudioResponse(audioBase64: string) {
    const audio = new Audio(audioBase64);
    audio.play().catch(error => {
      console.error('Error playing audio:', error);
      errorMessage = 'Failed to play audio response. Please try again.';
    });
  }
</script>

<div class="chat-container">
  {#if errorMessage}
    <div class="error-message">{errorMessage}</div>
  {/if}
  {#if isReconnecting}
    <div class="reconnecting-indicator">
      <div class="spinner"></div>
      <span>Reconnecting...</span>
    </div>
  {/if}
  <div class="message-container">
    {#each messages as message}
      <div class={message.isUser ? 'user-message' : 'ai-message'}>
        {#if message.type === 'text'}
          {message.content}
        {:else if message.type === 'audio' && message.isUser}
          <span>Audio message sent</span>
        {:else if message.type === 'audio' && !message.isUser}
          <span>Audio response received</span>
          <button on:click={() => playAudioResponse(message.content)}>Play</button>
        {/if}
      </div>
    {/each}
  </div>
  <div class="input-container">
    <input
      type="text"
      bind:value={message}
      on:keypress={(e) => e.key === 'Enter' && sendMessage()}
      placeholder="Type your message..."
      disabled={!isConnected || isReconnecting}
    />
    <button on:click={sendMessage} disabled={!isConnected || isReconnecting}>Send</button>
    <button
      on:mousedown={startRecording}
      on:mouseup={stopRecording}
      on:mouseleave={stopRecording}
      class="audio-button"
      disabled={!isConnected || isReconnecting}
    >
      {isRecording ? '🔴 Recording...' : '🎙️ Hold to Record'}
    </button>
  </div>
</div>

<style>
  /* ... (styles remain unchanged) ... */
</style>

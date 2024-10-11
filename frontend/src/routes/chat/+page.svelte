<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { goto } from '$app/navigation';
  import { currentConversation, chatMessages, token } from '../../stores';
  import { Room, RoomEvent, RemoteParticipant, LocalParticipant, RemoteTrack } from 'livekit-client';

  let message = '';
  let ws: WebSocket;
  let room: Room;
  let localParticipant: LocalParticipant;
  let remoteParticipant: RemoteParticipant;
  let isAudioEnabled = false;

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
    initializeLiveKit();
  });

  onDestroy(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.close();
    }
    if (room) {
      room.disconnect();
    }
  });

  async function startNewConversation() {
    const response = await fetch('http://localhost:8000/api/conversations', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${$token}`,
        'Content-Type': 'application/json'
      }
    });

    if (response.ok) {
      const data = await response.json();
      currentConversation.set(data.id);
    } else {
      console.error('Failed to start a new conversation');
    }
  }

  function connectWebSocket() {
    ws = new WebSocket(`ws://localhost:8000/ws/${$token}`);

    ws.onmessage = (event) => {
      const [conversationId, content, isUser] = event.data.split(':');
      if (parseInt(conversationId) === $currentConversation) {
        chatMessages.update(msgs => [...msgs, { content, isUser: isUser === 'True' }]);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  async function sendMessage() {
    if (message.trim() && ws.readyState === WebSocket.OPEN) {
      ws.send(`${$currentConversation}:${message}`);
      message = '';
    }
  }

  async function initializeLiveKit() {
    const response = await fetch('http://localhost:8000/livekit/join-room', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${$token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ room_name: `conversation_${$currentConversation}` })
    });

    if (response.ok) {
      const { access_token } = await response.json();
      room = new Room();

      room.on(RoomEvent.ParticipantConnected, (participant: RemoteParticipant) => {
        console.log('A remote participant connected:', participant);
        remoteParticipant = participant;
      });

      room.on(RoomEvent.TrackSubscribed, (track: RemoteTrack, publication, participant) => {
        if (track.kind === 'audio') {
          const audioElement = new Audio();
          audioElement.srcObject = new MediaStream([track.mediaStreamTrack]);
          audioElement.play();
        }
      });

      await room.connect('wss://your-livekit-server-url', access_token);
      console.log('Connected to LiveKit room');
      localParticipant = room.localParticipant;
    } else {
      console.error('Failed to join LiveKit room');
    }
  }

  async function toggleAudio() {
    if (!localParticipant) return;

    if (isAudioEnabled) {
      await localParticipant.setMicrophoneEnabled(false);
    } else {
      await localParticipant.setMicrophoneEnabled(true);
    }
    isAudioEnabled = !isAudioEnabled;
  }
</script>

<div class="chat-container">
  <div class="message-container">
    {#each messages as message}
      <div class={message.isUser ? 'user-message' : 'ai-message'}>
        {message.content}
      </div>
    {/each}
  </div>
  <div class="input-container">
    <input
      type="text"
      bind:value={message}
      on:keypress={(e) => e.key === 'Enter' && sendMessage()}
      placeholder="Type your message..."
    />
    <button on:click={sendMessage}>Send</button>
    <button on:click={toggleAudio}>
      {isAudioEnabled ? 'Disable Audio' : 'Enable Audio'}
    </button>
  </div>
</div>

<style>
  .chat-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    padding: 20px;
  }

  .message-container {
    flex-grow: 1;
    overflow-y: auto;
    margin-bottom: 20px;
  }

  .user-message, .ai-message {
    margin-bottom: 10px;
    padding: 10px;
    border-radius: 5px;
  }

  .user-message {
    background-color: #e6f3ff;
    align-self: flex-end;
  }

  .ai-message {
    background-color: #f0f0f0;
    align-self: flex-start;
  }

  .input-container {
    display: flex;
  }

  input {
    flex-grow: 1;
    padding: 10px;
    margin-right: 10px;
  }

  button {
    padding: 10px 20px;
    background-color: #007bff;
    color: white;
    border: none;
    cursor: pointer;
  }
</style>

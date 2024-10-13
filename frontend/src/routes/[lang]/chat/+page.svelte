<script lang="ts">
import { chatMessages, token, currentConversation } from "$lib/stores";
import { onMount, onDestroy } from "svelte";
import { goto } from "$app/navigation";

let message = "";
let ws: WebSocket;
let isConnected = false;
let tortureAudioUrl = null;
let selectedLanguage = "en";
$: messages = $chatMessages;
const languages = [
  { code: "en", name: "English" },
  { code: "cs", name: "Czech" },
  { code: "es", name: "Spanish" }
];

onMount(async () => {
  if (!$token) {
    goto("/login");
    return;
  }
  if (!$currentConversation) {
    await startNewConversation();
  }
  connectWebSocket();
});

onDestroy(() => {
  if (ws) {
    ws.close();
  }
});

function connectWebSocket() {
  ws = new WebSocket(`ws://localhost:8000/ws?token=${$token}`);
  ws.onopen = () => {
    isConnected = true;
  };
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === "chat_message") {
      chatMessages.update(messages => [...messages, data.message]);
    } else if (data.type === "torture_audio") {
      tortureAudioUrl = data.url;
    }
  };
  ws.onclose = () => {
    isConnected = false;
    setTimeout(connectWebSocket, 1000);
  };
}

async function startNewConversation() {
  const response = await fetch("http://localhost:8000/api/conversations", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${$token}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ language: selectedLanguage })
  });
  if (response.ok) {
    const data = await response.json();
    currentConversation.set(data.id);
  } else {
    console.error("Failed to start new conversation");
  }
}

function sendMessage() {
  if (!message.trim()) return;
  const messageData = {
    conversation_id: $currentConversation,
    content: message,
    type: "text"
  };
  ws.send(JSON.stringify(messageData));
  message = "";
}

function changeLanguage() {
  startNewConversation();
}
</script>

<div class="chat-container">
  <div class="language-selector">
    <select bind:value={selectedLanguage} on:change={changeLanguage}>
      {#each languages as language}
        <option value={language.code}>{language.name}</option>
      {/each}
    </select>
  </div>
  <div class="messages">
    {#each messages as message}
      <div class="message {message.role}">
        {message.content}
      </div>
    {/each}
  </div>
  <div class="input-area">
    <input type="text" bind:value={message} on:keypress={(e) => e.key === 'Enter' && sendMessage()} placeholder="Type your message...">
    <button on:click={sendMessage}>Send</button>
  </div>
  {#if tortureAudioUrl}
    <audio src={tortureAudioUrl} controls></audio>
  {/if}
</div>

<style>
  .chat-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
  }
  .messages {
    height: 400px;
    overflow-y: auto;
    border: 1px solid #ccc;
    padding: 10px;
    margin-bottom: 20px;
  }
  .message {
    margin-bottom: 10px;
    padding: 5px;
    border-radius: 5px;
  }
  .message.user {
    background-color: #e6f3ff;
    text-align: right;
  }
  .message.assistant {
    background-color: #f0f0f0;
  }
  .input-area {
    display: flex;
  }
  input {
    flex-grow: 1;
    padding: 5px;
  }
  button {
    padding: 5px 10px;
    background-color: #007bff;
    color: white;
    border: none;
    cursor: pointer;
  }
  .language-selector {
    margin-bottom: 20px;
  }
</style>

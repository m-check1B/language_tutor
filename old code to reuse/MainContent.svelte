<script lang="ts">
  import { onMount } from 'svelte';
  import WebSocketHandler from './WebSocketHandler.svelte';
  import MultimediaChat from './MultimediaChat.svelte';
  import VoiceSettings from './VoiceSettings.svelte';
  import AgentsManagement from './AgentsManagement.svelte';
  import ProjectsManagement from './ProjectsManagement.svelte';
  import ToolsManagement from './ToolsManagement.svelte';
  import { isLoading, errorStore } from '../stores/stores';

  // Define the type of chatWindow, adjust according to its actual type
  export let chatWindow: any;

  onMount(() => {
    console.log('MainContent component mounted');
  });
</script>

<div class="container">
  {#if $isLoading}
    <div class="loading-overlay">
      <p>Loading content...</p>
    </div>
  {:else if $errorStore}
    <p class="error">Error: {$errorStore}</p>
  {:else}
    <WebSocketHandler />
    <div class="main_left">
      <MultimediaChat bind:this={chatWindow} />
      <VoiceSettings />
    </div>
    <div class="main_right">
      <AgentsManagement />
      <ProjectsManagement />
      <ToolsManagement />
    </div>
  {/if}
</div>

<style>
  .container {
    display: flex;
    width: 100%;
    height: 100%;
  }
  .main_left, .main_right {
    width: 50%;
    height: 100%;
    background-color: var(--color-background);
    padding: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    overflow-y: auto;
  }
  .main_left {
    border-right: 1px solid rgba(0, 0, 0, 0.1);
  }
  .error {
    color: var(--color-error);
    margin-top: 10px;
  }
  @media (max-width: 768px) {
    .container {
      flex-direction: column;
    }
    .main_left, .main_right {
      width: 100%;
      height: auto;
    }
    .main_right {
      display: none;
    }
  }
  .loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }
  .loading-overlay p {
    background-color: var(--color-background);
    padding: 20px;
    border-radius: 8px;
  }
</style>

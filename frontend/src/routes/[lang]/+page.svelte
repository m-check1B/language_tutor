<script lang="ts">
  import { _ } from 'svelte-i18n';
  import { page } from '$app/stores';
  import ChatInterface from '$lib/components/ChatInterface.svelte';
  import VoiceInterface from '$lib/components/VoiceInterface.svelte';

  let isVoiceMode = false;

  $: lang = $page.params.lang;

  function toggleMode() {
    isVoiceMode = !isVoiceMode;
  }
</script>

<svelte:head>
  <title>{$_('languageTutor')}</title>
</svelte:head>

<div class="container mx-auto px-4 py-8">
  <h1 class="text-4xl font-bold mb-6 text-center">{$_('welcomeToLanguageTutor')}</h1>

  <div class="mb-4 text-center">
    <button
      on:click={toggleMode}
      class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
    >
      {isVoiceMode ? $_('switchToTextMode') : $_('switchToVoiceMode')}
    </button>
  </div>

  <div class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
    {#if isVoiceMode}
      <VoiceInterface />
    {:else}
      <ChatInterface />
    {/if}
  </div>
</div>

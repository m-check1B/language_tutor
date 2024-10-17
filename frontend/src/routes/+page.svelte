<script lang="ts">
  import { _ } from 'svelte-i18n';
  import ChatInterface from '$lib/components/ChatInterface.svelte';
  import { isLoggedIn } from '../stores';
</script>

<svelte:head>
  <title>{$_('languageTutor')}</title>
</svelte:head>

<main>
  <h1>{$_('welcomeToLanguageTutor')}</h1>
  
  {#if $isLoggedIn}
    <p>{$_('startChatting')}</p>
    <ChatInterface />
  {:else}
    <p>{$_('loginToStart')}</p>
  {/if}
</main>

<style>
  main {
    text-align: center;
    padding: 1em;
    max-width: 800px;
    margin: 0 auto;
  }

  h1 {
    color: #ff3e00;
    text-transform: uppercase;
    font-size: 4em;
    font-weight: 100;
  }

  @media (min-width: 640px) {
    main {
      max-width: none;
    }
  }
</style>

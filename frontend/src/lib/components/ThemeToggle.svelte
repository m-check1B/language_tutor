<script lang="ts">
  import { _ } from 'svelte-i18n';
  import { theme } from '$lib/stores/theme';
</script>

<button
  on:click={() => theme.toggle()}
  class="inline-flex items-center justify-center rounded-lg p-2 
         hover:bg-blue-700 dark:hover:bg-blue-900 
         focus:outline-none focus:ring-2 focus:ring-blue-500
         transition-colors duration-200"
  aria-label={$theme ? $_('theme.lightMode') : $_('theme.darkMode')}
>
  {#if $theme}
    <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
    </svg>
  {:else}
    <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
    </svg>
  {/if}
</button>

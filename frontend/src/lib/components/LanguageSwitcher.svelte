<script lang="ts">
  import { locale } from 'svelte-i18n';
  import { page } from '$app/stores';

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'cs', name: 'Čeština' },
    { code: 'es', name: 'Español' }
  ];

  $: currentPath = $page.url.pathname;
  $: currentLang = $page?.params?.lang || 'en';

  function switchLanguage(event: Event) {
    const select = event.target as HTMLSelectElement;
    const newLang = select.value;
    const newPath = currentPath.replace(/^\/[^/]+/, `/${newLang}`);
    window.location.pathname = newPath;
  }
</script>

<select
  value={currentLang}
  on:change={switchLanguage}
  class="bg-white dark:bg-gray-700 text-gray-900 dark:text-white 
         border border-gray-300 dark:border-gray-600 rounded-lg 
         px-3 py-2 appearance-none cursor-pointer
         focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
         hover:bg-gray-50 dark:hover:bg-gray-600
         transition-colors duration-200"
>
  {#each languages as lang}
    <option 
      value={lang.code}
      class="bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
    >
      {lang.name}
    </option>
  {/each}
</select>

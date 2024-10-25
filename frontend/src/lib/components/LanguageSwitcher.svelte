<script>
  import { locale, _ } from 'svelte-i18n';
  import { page } from '$app/stores';

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'cs', name: 'Čeština' },
    { code: 'es', name: 'Español' }
  ];

  $: currentPath = $page.url.pathname;
  $: currentLang = $locale;

  function switchLanguage(lang) {
    const newPath = currentPath.replace(/^\/[^/]+/, `/${lang}`);
    window.location.href = newPath;
  }
</script>

<div class="relative inline-block text-left">
  <select
    bind:value={currentLang}
    on:change={() => switchLanguage(currentLang)}
    class="appearance-none block w-full pl-3 pr-10 py-2 text-base rounded-md
           bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600
           text-gray-900 dark:text-white
           focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
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
  <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700 dark:text-gray-300">
    <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
      <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
    </svg>
  </div>
</div>

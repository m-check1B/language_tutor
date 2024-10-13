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

<div class="language-switcher">
  <select bind:value={currentLang} on:change={() => switchLanguage(currentLang)} class="bg-gray-700 text-white px-2 py-1 rounded">
    {#each languages as lang}
      <option value={lang.code}>{lang.name}</option>
    {/each}
  </select>
</div>

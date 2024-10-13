<script>
  import { onMount } from 'svelte';
  import { _ } from 'svelte-i18n';

  let darkMode = false;

  onMount(() => {
    const savedTheme = localStorage.getItem('theme');
    darkMode = savedTheme === 'dark';
    setTheme(darkMode);
  });

  function toggleTheme() {
    darkMode = !darkMode;
    setTheme(darkMode);
  }

  function setTheme(isDark) {
    if (isDark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }
</script>

<button on:click={toggleTheme} class="px-3 py-2 rounded-md text-sm font-medium bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-white">
  {darkMode ? $_('lightMode') : $_('darkMode')}
</button>

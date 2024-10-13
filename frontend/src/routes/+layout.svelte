<script>
  import { isLoggedIn, setToken, setUser } from '../stores.js';
  import { onMount } from 'svelte';
  import { _, locale } from 'svelte-i18n';
  import { page } from '$app/stores';
  import LanguageSwitcher from '$lib/components/LanguageSwitcher.svelte';
  import ThemeToggle from '$lib/components/ThemeToggle.svelte';
  import '../lib/i18n'; // Import i18n configuration

  let showAuth = false;
  let showSubscriptionManager = false;
  let error = '';

  $: lang = $page.params.lang || 'en';
  $: $locale = lang;

  // Use the PUBLIC_API_URL as a base, but with a different port for auth_and_paywall
  const baseUrl = import.meta.env.PUBLIC_API_URL.replace(':8081', ':3000');
  const authUrl = `${baseUrl}/${lang}/auth`;
  const subscriptionUrl = `${baseUrl}/${lang}/subscription`;

  onMount(() => {
    // Check if the user is already logged in
    if (!$isLoggedIn) {
      showAuth = true;
    }

    // Listen for messages from iframes
    window.addEventListener('message', handleMessage);

    return () => {
      window.removeEventListener('message', handleMessage);
    };
  });

  function handleMessage(event) {
    // Ensure the message is from our auth_and_paywall service
    if (event.origin !== baseUrl) {
      console.error('Received message from unknown origin:', event.origin);
      return;
    }

    switch (event.data.type) {
      case 'AUTH_SUCCESS':
        setToken(event.data.token);
        setUser(event.data.user);
        showAuth = false;
        $isLoggedIn = true;
        error = '';
        break;
      case 'LOGOUT_SUCCESS':
        setToken(null);
        setUser(null);
        showAuth = true;
        $isLoggedIn = false;
        error = '';
        // Redirect to home page
        window.location.href = `/${lang}`;
        break;
      case 'AUTH_ERROR':
        error = event.data.error;
        break;
      default:
        console.warn('Received unknown message type:', event.data.type);
    }
  }

  function login() {
    showAuth = true;
    error = '';
  }

  function logout() {
    // Send logout message to auth iframe
    const authFrame = document.getElementById('auth-frame');
    if (authFrame && authFrame.contentWindow) {
      try {
        authFrame.contentWindow.postMessage({ type: 'LOGOUT' }, baseUrl);
      } catch (error) {
        console.error('Error sending logout message:', error);
      }
    } else {
      console.error('Auth iframe not found');
    }
  }

  function toggleSubscriptionManager() {
    showSubscriptionManager = !showSubscriptionManager;
  }
</script>

<nav class="bg-gray-800 dark:bg-gray-900 text-white p-4">
  <ul class="flex justify-around items-center">
    <li><a href="/{lang}" class="hover:text-gray-300">{$_('home')}</a></li>
    {#if $isLoggedIn}
      <li><a href="/{lang}/chat" class="hover:text-gray-300">{$_('chat')}</a></li>
      <li><button on:click={toggleSubscriptionManager} class="hover:text-gray-300">{$_('manageSubscription')}</button></li>
      <li><button on:click={logout} class="hover:text-gray-300">{$_('logout')}</button></li>
    {:else}
      <li><button on:click={login} class="hover:text-gray-300">{$_('loginRegister')}</button></li>
    {/if}
    <li><LanguageSwitcher /></li>
    <li><ThemeToggle /></li>
  </ul>
</nav>

<main class="container mx-auto p-4 bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
  {#if showAuth}
    <!-- Auth iframe: Embedded authentication page from auth_and_paywall service -->
    <iframe id="auth-frame" src={authUrl} title={$_('authentication')} class="w-full h-screen border-none"></iframe>
  {:else if showSubscriptionManager}
    <!-- Subscription iframe: Embedded subscription management page from auth_and_paywall service -->
    <iframe id="subscription-frame" src={subscriptionUrl} title={$_('subscriptionManagement')} class="w-full h-screen border-none"></iframe>
  {:else}
    <slot></slot>
  {/if}

  {#if error}
    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
      <strong class="font-bold">Error:</strong>
      <span class="block sm:inline">{error}</span>
    </div>
  {/if}
</main>

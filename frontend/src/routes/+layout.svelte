<script lang="ts">
  import { onMount } from 'svelte';
  import { _, locale } from 'svelte-i18n';
  import { page } from '$app/stores';
  import { isLoggedIn } from '../stores';
  import LanguageSwitcher from '$lib/components/LanguageSwitcher.svelte';
  import ThemeToggle from '$lib/components/ThemeToggle.svelte';
  import '../lib/i18n'; // Import i18n configuration

  let showAuth = false;
  let showSubscriptionManager = false;
  let error = '';

  $: lang = $page.params.lang || 'en';
  $: $locale = lang;

  // Use an environment variable for the auth_and_paywall module URL
  const authPaywallUrl = import.meta.env.VITE_AUTH_PAYWALL_URL || 'http://localhost:5000';
  const authUrl = `${authPaywallUrl}/auth/${lang}`;
  const subscriptionUrl = `${authPaywallUrl}/subscription/${lang}`;

  onMount(() => {
    // Listen for messages from iframes
    window.addEventListener('message', handleMessage);

    return () => {
      window.removeEventListener('message', handleMessage);
    };
  });

  function handleMessage(event: MessageEvent) {
    // Ensure the message is from our auth_paywall service
    if (event.origin !== authPaywallUrl) {
      console.error('Received message from unknown origin:', event.origin);
      return;
    }

    switch (event.data.type) {
      case 'AUTH_SUCCESS':
        isLoggedIn.set(true);
        showAuth = false;
        error = '';
        break;
      case 'LOGOUT_SUCCESS':
        isLoggedIn.set(false);
        showAuth = true;
        showSubscriptionManager = false;
        error = '';
        break;
      case 'AUTH_ERROR':
        error = event.data.error;
        break;
      case 'CHECKOUT_SESSION_CREATED':
        // Redirect to Stripe Checkout
        window.location.href = event.data.url;
        break;
      case 'CUSTOMER_PORTAL_CREATED':
        // Redirect to Stripe Customer Portal
        window.location.href = event.data.url;
        break;
      case 'SUBSCRIPTION_ERROR':
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
    const authFrame = document.getElementById('auth-frame') as HTMLIFrameElement;
    if (authFrame && authFrame.contentWindow) {
      authFrame.contentWindow.postMessage({ type: 'LOGOUT' }, authPaywallUrl);
    } else {
      console.error('Auth iframe not found');
    }
  }

  function toggleSubscriptionManager() {
    showSubscriptionManager = !showSubscriptionManager;
  }
</script>

<div class="app">
  <header>
    <LanguageSwitcher />
    <ThemeToggle />
    {#if $isLoggedIn}
      <button on:click={logout}>{$_('logout')}</button>
      <button on:click={toggleSubscriptionManager}>{$_('manageSubscription')}</button>
    {:else}
      <button on:click={login}>{$_('login')}</button>
    {/if}
  </header>

  <main>
    {#if showAuth}
      <iframe id="auth-frame" src={authUrl} title="Authentication" />
    {/if}

    {#if showSubscriptionManager}
      <iframe id="subscription-frame" src={subscriptionUrl} title="Subscription Management" />
    {/if}

    {#if error}
      <p class="error">{error}</p>
    {/if}

    <slot />
  </main>

  <footer>
    <!-- Add your footer content here -->
  </footer>
</div>

<style>
  iframe {
    width: 100%;
    height: 400px;
    border: none;
  }
  /* Add your other styles here */
</style>

<script lang="ts">
  import { auth, isLoggedIn, user } from '../../stores';
  import { _ } from 'svelte-i18n';
  import { onMount } from 'svelte';

  let error = '';
  let isLoading = false;
  let email = '';
  let password = '';
  let username = '';
  let isRegistering = false;

  $: loggedInUser = $user;

  onMount(() => {
    window.addEventListener('message', handleParentMessage);
    return () => window.removeEventListener('message', handleParentMessage);
  });

  function handleParentMessage(event) {
    // TODO: Replace with the actual origin of the language tutor application
    const LANGUAGE_TUTOR_ORIGIN = import.meta.env.VITE_LANGUAGE_TUTOR_ORIGIN || "http://localhost:3000";
    
    if (event.origin !== LANGUAGE_TUTOR_ORIGIN) return;

    switch (event.data.type) {
      case 'LOGOUT':
        handleLogout();
        break;
      default:
        console.warn('Received unknown message type:', event.data.type);
    }
  }

  async function handleLogin() {
    isLoading = true;
    error = '';
    try {
      await auth.login(email, password);
      window.parent.postMessage({ type: 'AUTH_SUCCESS', token: $user.token }, '*');
    } catch (err) {
      error = $_('loginFailed');
      console.error('Login error:', err);
      window.parent.postMessage({ type: 'AUTH_ERROR', error: error }, '*');
    } finally {
      isLoading = false;
    }
  }

  async function handleLogout() {
    isLoading = true;
    error = '';
    try {
      await auth.logout();
      window.parent.postMessage({ type: 'LOGOUT_SUCCESS' }, '*');
    } catch (err) {
      error = $_('logoutFailed');
      console.error('Logout error:', err);
      window.parent.postMessage({ type: 'AUTH_ERROR', error: error }, '*');
    } finally {
      isLoading = false;
    }
  }

  async function handleRegister() {
    isLoading = true;
    error = '';
    try {
      await auth.register(username, email, password);
      window.parent.postMessage({ type: 'REGISTER_SUCCESS' }, '*');
    } catch (err) {
      error = $_('registrationFailed');
      console.error('Registration error:', err);
      window.parent.postMessage({ type: 'AUTH_ERROR', error: error }, '*');
    } finally {
      isLoading = false;
    }
  }

  function toggleAuthMode() {
    isRegistering = !isRegistering;
    error = '';
  }
</script>

<div class="auth-container">
  {#if $isLoggedIn}
    <p class="mb-4">{$_('welcomeUser', { values: { username: loggedInUser?.username } })}</p>
    <button 
      on:click={handleLogout}
      class="w-full py-2 px-4 bg-red-500 text-white rounded hover:bg-red-600 transition-colors duration-200"
      disabled={isLoading}
    >
      {isLoading ? $_('loggingOut') : $_('logout')}
    </button>
  {:else}
    <h2 class="text-2xl mb-4">{isRegistering ? $_('register') : $_('login')}</h2>
    <form on:submit|preventDefault={isRegistering ? handleRegister : handleLogin} class="space-y-4">
      {#if isRegistering}
        <input
          type="text"
          bind:value={username}
          placeholder={$_('username')}
          class="w-full p-2 border rounded"
          required
        />
      {/if}
      <input
        type="email"
        bind:value={email}
        placeholder={$_('email')}
        class="w-full p-2 border rounded"
        required
      />
      <input
        type="password"
        bind:value={password}
        placeholder={$_('password')}
        class="w-full p-2 border rounded"
        required
      />
      <button
        type="submit"
        class="w-full py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors duration-200"
        disabled={isLoading}
      >
        {isLoading ? $_('processing') : (isRegistering ? $_('register') : $_('login'))}
      </button>
    </form>
    <button
      on:click={toggleAuthMode}
      class="mt-4 text-blue-500 hover:underline"
    >
      {isRegistering ? $_('alreadyHaveAccount') : $_('needAccount')}
    </button>
  {/if}
  
  {#if error}
    <p class="mt-4 text-red-500 dark:text-red-400">{error}</p>
  {/if}
</div>

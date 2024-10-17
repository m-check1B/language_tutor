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

  function handleParentMessage(event: MessageEvent) {
    const LANGUAGE_TUTOR_ORIGIN = import.meta.env.VITE_API_BASE_URL || "http://localhost";
    
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
      window.parent.postMessage({ type: 'AUTH_SUCCESS', token: $user?.token, user: $user }, '*');
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

<!-- The rest of the component remains unchanged -->

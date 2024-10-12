<script>
  import { goto } from '$app/navigation';
  import { setToken } from '../../stores.js';

  let email = '';
  let password = '';
  let error = '';

  async function handleSubmit() {
    error = '';
    try {
      const response = await fetch('http://localhost:8081/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setToken(data.access_token);
        goto('/chat');
      } else {
        const errorData = await response.json();
        error = errorData.detail || 'An error occurred during login.';
      }
    } catch (err) {
      console.error('Login error:', err);
      error = 'An error occurred during login. Please try again.';
    }
  }
</script>

<svelte:head>
  <title>Language Tutor - Login</title>
</svelte:head>

<h1>Login</h1>

<form on:submit|preventDefault={handleSubmit}>
  <div>
    <label for="email">Email:</label>
    <input type="email" id="email" bind:value={email} required autocomplete="email">
  </div>
  <div>
    <label for="password">Password:</label>
    <input type="password" id="password" bind:value={password} required autocomplete="current-password">
  </div>
  <button type="submit">Login</button>
</form>

{#if error}
  <p class="error">{error}</p>
{/if}

<p>Don't have an account? <a href="/register">Register here</a></p>

<style>
  h1 {
    color: #333;
    font-size: 2rem;
    margin-bottom: 1rem;
  }

  form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    max-width: 300px;
  }

  label {
    font-weight: bold;
  }

  input {
    width: 100%;
    padding: 0.5rem;
    font-size: 1rem;
  }

  button {
    background-color: #0066cc;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    font-size: 1rem;
    cursor: pointer;
  }

  button:hover {
    background-color: #0052a3;
  }

  .error {
    color: red;
    margin-top: 1rem;
  }

  a {
    color: #0066cc;
    text-decoration: none;
  }

  a:hover {
    text-decoration: underline;
  }
</style>

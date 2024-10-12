<script>
  import { goto } from '$app/navigation';
  import { PUBLIC_API_URL } from '$env/static/public';

  let username = '';
  let email = '';
  let password = '';
  let confirmPassword = '';
  let error = '';

  async function login(email, password) {
    try {
      const response = await fetch(`${PUBLIC_API_URL}/auth/login`, {
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
        // Here you would typically store the token in localStorage or a secure cookie
        // For example: localStorage.setItem('token', data.access_token);
        goto('/'); // Redirect to home page or dashboard
      } else {
        throw new Error('Login failed');
      }
    } catch (err) {
      console.error('Login error:', err);
      error = 'An error occurred during login. Please try logging in manually.';
    }
  }

  async function handleSubmit() {
    error = '';

    if (password !== confirmPassword) {
      error = 'Passwords do not match.';
      return;
    }

    try {
      const response = await fetch(`${PUBLIC_API_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username,
          email,
          password,
        }),
      });

      if (response.ok) {
        // Registration successful, attempt to log in
        await login(email, password);
      } else if (response.status === 0) {
        // Handle empty response
        error = 'No response from server. Please try again.';
      } else {
        const errorData = await response.json();
        error = errorData.detail || 'An error occurred during registration.';
      }
    } catch (err) {
      console.error('Registration error:', err);
      error = 'An error occurred during registration. Please try again.';
    }
  }
</script>

<svelte:head>
  <title>Language Tutor - Register</title>
</svelte:head>

<h1>Register</h1>

<form on:submit|preventDefault={handleSubmit}>
  <div>
    <label for="username">Username:</label>
    <input type="text" id="username" bind:value={username} required autocomplete="username">
  </div>
  <div>
    <label for="email">Email:</label>
    <input type="email" id="email" bind:value={email} required autocomplete="email">
  </div>
  <div>
    <label for="password">Password:</label>
    <input type="password" id="password" bind:value={password} required autocomplete="new-password">
  </div>
  <div>
    <label for="confirmPassword">Confirm Password:</label>
    <input type="password" id="confirmPassword" bind:value={confirmPassword} required autocomplete="new-password">
  </div>
  <button type="submit">Register</button>
</form>

{#if error}
  <p class="error">{error}</p>
{/if}

<p>Already have an account? <a href="/login">Login here</a></p>

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

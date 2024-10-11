<script>
  import { isLoggedIn, setToken } from '../stores.js';

  function logout() {
    setToken(null);
    // Redirect to home page
    window.location.href = '/';
  }
</script>

<nav>
  <ul>
    <li><a href="/">Home</a></li>
    {#if $isLoggedIn}
      <li><a href="/chat">Chat</a></li>
      <li><button on:click={logout}>Logout</button></li>
    {:else}
      <li><a href="/login">Login</a></li>
      <li><a href="/register">Register</a></li>
    {/if}
  </ul>
</nav>

<main>
  <slot></slot>
</main>

<style>
  nav {
    background-color: #f0f0f0;
    padding: 1rem;
  }

  ul {
    list-style-type: none;
    padding: 0;
    display: flex;
    justify-content: space-around;
  }

  li {
    display: inline;
  }

  a {
    text-decoration: none;
    color: #333;
  }

  button {
    background: none;
    border: none;
    cursor: pointer;
    color: #333;
    font-size: 1rem;
  }

  main {
    padding: 2rem;
  }
</style>

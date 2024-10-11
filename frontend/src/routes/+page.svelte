<script>
  import { onMount } from 'svelte';

  let isLoggedIn = false;

  onMount(() => {
    // Check if user is logged in (e.g., by checking for a token in localStorage)
    isLoggedIn = !!localStorage.getItem('token');
  });
</script>

<svelte:head>
  <title>Language Tutor - Home</title>
</svelte:head>

<h1>Welcome to Language Tutor</h1>

<p>Improve your language skills with our AI-powered tutor!</p>

{#if isLoggedIn}
  <p>You're logged in. <a href="/chat">Start chatting</a> with our AI tutor now!</p>
{:else}
  <p><a href="/login">Log in</a> or <a href="/register">register</a> to start improving your language skills.</p>
{/if}

<h2>Features</h2>
<ul>
  <li>Practice conversations in multiple languages</li>
  <li>Get instant feedback on your grammar and vocabulary</li>
  <li>Learn at your own pace</li>
  <li>Track your progress over time</li>
</ul>

<style>
  h1 {
    color: #333;
    font-size: 2.5rem;
  }

  h2 {
    color: #444;
    font-size: 1.8rem;
  }

  p {
    font-size: 1.2rem;
    line-height: 1.6;
  }

  ul {
    list-style-type: disc;
    margin-left: 2rem;
  }

  li {
    margin-bottom: 0.5rem;
  }

  a {
    color: #0066cc;
    text-decoration: none;
  }

  a:hover {
    text-decoration: underline;
  }
</style>

<script lang="ts">
    import { goto } from '$app/navigation';
    import { isLoggedIn } from '$lib';

    function handleGetStarted() {
        goto('/en/login');
    }
</script>

<div class="container">
    <h1>Welcome to Language Tutor</h1>
    <p class="description">
        Improve your language skills with our AI-powered tutor. Practice conversations,
        learn grammar, and enhance your vocabulary in a natural way.
    </p>
    
    {#if !$isLoggedIn}
        <button on:click={handleGetStarted}>Get Started</button>
    {:else}
        <button on:click={() => goto('/en/chat')}>Continue Learning</button>
    {/if}
</div>

<style>
    .container {
        max-width: 800px;
        margin: 4rem auto;
        padding: 2rem;
        text-align: center;
    }

    h1 {
        font-size: 2.5rem;
        color: #2d3748;
        margin-bottom: 1.5rem;
    }

    .description {
        font-size: 1.2rem;
        color: #4a5568;
        margin-bottom: 2rem;
        line-height: 1.6;
    }

    button {
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        background-color: #4299e1;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        transition: background-color 0.2s;
    }

    button:hover {
        background-color: #3182ce;
    }
</style>

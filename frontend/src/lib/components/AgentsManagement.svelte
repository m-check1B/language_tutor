<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import {
    agents,
    selectedAgent,
    agentName,
    agentSystemPrompt,
    agentProvider,
    agentModel,
    agentVoice,
    errorStore
  } from '../stores/stores';
  import { auth, authToken, authSessionId } from '../stores/auth';
  import { get } from 'svelte/store';

  let isLoading: boolean = true;
  const dispatch = createEventDispatcher();
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api';

  // Get available options from environment variables
  const availableProviders = import.meta.env.VITE_AVAILABLE_PROVIDERS?.split(',') || ['openai', 'anthropic'];
  const openaiModels = import.meta.env.VITE_OPENAI_MODELS?.split(',') || ['gpt-4-turbo-preview', 'gpt-3.5-turbo'];
  const anthropicModels = import.meta.env.VITE_ANTHROPIC_MODELS?.split(',') || ['claude-3-opus', 'claude-3-sonnet'];
  const availableVoices = import.meta.env.VITE_AVAILABLE_VOICES?.split(',') || ['alloy', 'echo', 'fable', 'nova', 'shimmer'];

  let availableModels: string[] = [];

  // Update available models when provider changes
  $: {
    if ($agentProvider === 'openai') {
      availableModels = openaiModels;
    } else if ($agentProvider === 'anthropic') {
      availableModels = anthropicModels;
    } else {
      availableModels = [];
    }
  }

  interface Agent {
    id: number;
    name: string;
    system_prompt: string;
    provider: string;
    model: string;
    voice: string;
  }

  async function loadAgents() {
    try {
      const token = get(authToken);
      const sessionId = get(authSessionId);
      
      if (!token || !sessionId) {
        console.error('Missing auth token or session ID');
        return;
      }

      const response = await fetch(`${API_URL}/agents`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId
        },
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        agents.set(data);
      } else {
        const error = await response.json();
        errorStore.set(error.detail || 'Failed to load agents');
      }
    } catch (error) {
      console.error('Failed to load agents:', error);
      errorStore.set('Failed to load agents');
    } finally {
      isLoading = false;
    }
  }

  async function handleSelectAgent(agent: Agent) {
    selectedAgent.set(agent);
    agentName.set(agent.name);
    agentSystemPrompt.set(agent.system_prompt);
    agentProvider.set(agent.provider);
    agentModel.set(agent.model);
    agentVoice.set(agent.voice);
  }

  function handleCreateAgent() {
    selectedAgent.set(null);
    agentName.set('');
    agentSystemPrompt.set(import.meta.env.VITE_DEFAULT_SYSTEM_PROMPT || 'You are a helpful assistant');
    agentProvider.set(import.meta.env.VITE_DEFAULT_PROVIDER || 'openai');
    agentModel.set(import.meta.env.VITE_DEFAULT_MODEL || 'gpt-4-turbo-preview');
    agentVoice.set(import.meta.env.VITE_DEFAULT_VOICE || 'alloy');
  }

  async function handleSaveAgent() {
    try {
      const token = get(authToken);
      const sessionId = get(authSessionId);
      
      if (!token || !sessionId) {
        console.error('Missing auth token or session ID');
        return;
      }

      const newAgent = {
        id: get(selectedAgent)?.id,
        name: get(agentName),
        system_prompt: get(agentSystemPrompt),
        provider: get(agentProvider),
        model: get(agentModel),
        voice: get(agentVoice)
      };

      const method = newAgent.id ? 'PUT' : 'POST';
      const url = newAgent.id ? `${API_URL}/agents/${newAgent.id}` : `${API_URL}/agents`;

      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId
        },
        body: JSON.stringify(newAgent),
        credentials: 'include'
      });

      if (response.ok) {
        const savedAgent = await response.json();
        agents.update(currentAgents => {
          const index = currentAgents.findIndex(a => a.id === savedAgent.id);
          if (index >= 0) {
            currentAgents[index] = savedAgent;
            return [...currentAgents];
          } else {
            return [...currentAgents, savedAgent];
          }
        });
        selectedAgent.set(savedAgent);
      } else {
        const error = await response.json();
        errorStore.set(error.detail || 'Failed to save agent');
      }
    } catch (error) {
      console.error('Failed to save agent:', error);
      errorStore.set('Failed to save agent');
    }
  }

  async function handleDeleteAgent() {
    try {
      const currentAgent = get(selectedAgent);
      if (!currentAgent) return;

      const token = get(authToken);
      const sessionId = get(authSessionId);
      
      if (!token || !sessionId) {
        console.error('Missing auth token or session ID');
        return;
      }

      const response = await fetch(`${API_URL}/agents/${currentAgent.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId
        },
        credentials: 'include'
      });

      if (response.ok) {
        agents.update(currentAgents => currentAgents.filter(a => a.id !== currentAgent.id));
        handleCreateAgent();
      } else {
        const error = await response.json();
        errorStore.set(error.detail || 'Failed to delete agent');
      }
    } catch (error) {
      console.error('Failed to delete agent:', error);
      errorStore.set('Failed to delete agent');
    }
  }

  onMount(() => {
    if (get(auth).isLoggedIn) {
      loadAgents();
    }
  });

  $: if ($auth.isLoggedIn && $authToken && $authSessionId) {
    loadAgents();
  }
</script>

<div class="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-2xl shadow-xl p-6">
  {#if isLoading}
    <div class="text-center text-gray-600 dark:text-gray-300">
      Loading agents... {$errorStore ? `Error: ${$errorStore}` : ''}
    </div>
  {:else if $agents.length === 0}
    <div class="text-center text-gray-600 dark:text-gray-300">
      No agents found. {$errorStore ? `Error: ${$errorStore}` : 'Create a new agent to get started.'}
    </div>
  {:else}
    <!-- Agent Selection -->
    <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-6">
      {#each $agents as agent (agent.id)}
        <button
          class="px-4 py-2 rounded-lg border-2 transition-all duration-200
            {$selectedAgent?.id === agent.id ? 
              'border-blue-500 bg-blue-500 text-white' : 
              'border-gray-300 dark:border-gray-600 hover:border-blue-500 dark:hover:border-blue-400'}"
          on:click={() => handleSelectAgent(agent)}
        >
          {agent.name}
        </button>
      {/each}
    </div>

    <!-- Agent Actions -->
    <div class="flex gap-3 mb-6">
      <button
        class="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
        on:click={handleSaveAgent}
      >
        Save Agent
      </button>
      <button
        class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        on:click={handleCreateAgent}
      >
        Create Agent
      </button>
      <button
        class="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        on:click={handleDeleteAgent}
      >
        Delete Agent
      </button>
    </div>

    <!-- Agent Configuration -->
    <div class="space-y-4">
      <input
        type="text"
        bind:value={$agentName}
        placeholder="Agent Name"
        class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      
      <textarea
        bind:value={$agentSystemPrompt}
        placeholder="System Prompt"
        class="w-full h-32 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
      ></textarea>

      <div class="grid grid-cols-2 gap-4">
        <select
          bind:value={$agentProvider}
          class="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {#each availableProviders as provider}
            <option value={provider}>{provider}</option>
          {/each}
        </select>

        <select
          bind:value={$agentModel}
          class="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {#each availableModels as model}
            <option value={model}>{model}</option>
          {/each}
        </select>
      </div>

      <select
        bind:value={$agentVoice}
        class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        {#each availableVoices as voice}
          <option value={voice}>{voice}</option>
        {/each}
      </select>
    </div>
  {/if}
</div>

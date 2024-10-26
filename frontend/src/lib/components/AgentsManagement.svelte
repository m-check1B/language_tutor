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
  import { get } from 'svelte/store';

  let isLoading: boolean = true;
  const dispatch = createEventDispatcher();

  // Get available options from environment variables
  const availableProviders = import.meta.env.VITE_AVAILABLE_PROVIDERS.split(',');
  const openaiModels = import.meta.env.VITE_OPENAI_MODELS.split(',');
  const anthropicModels = import.meta.env.VITE_ANTHROPIC_MODELS.split(',');
  const availableVoices = import.meta.env.VITE_AVAILABLE_VOICES.split(',');

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
    agentSystemPrompt.set(import.meta.env.VITE_DEFAULT_SYSTEM_PROMPT);
    agentProvider.set(import.meta.env.VITE_DEFAULT_PROVIDER);
    agentModel.set(import.meta.env.VITE_DEFAULT_MODEL);
    agentVoice.set(import.meta.env.VITE_DEFAULT_VOICE);
  }

  function handleSaveAgent() {
    const newAgent: Agent = {
      id: get(selectedAgent)?.id || Date.now(),
      name: get(agentName),
      system_prompt: get(agentSystemPrompt),
      provider: get(agentProvider),
      model: get(agentModel),
      voice: get(agentVoice)
    };

    agents.update(currentAgents => {
      const index = currentAgents.findIndex(a => a.id === newAgent.id);
      if (index >= 0) {
        currentAgents[index] = newAgent;
        return [...currentAgents];
      } else {
        return [...currentAgents, newAgent];
      }
    });

    selectedAgent.set(newAgent);
  }

  function handleDeleteAgent() {
    const currentAgent = get(selectedAgent);
    if (currentAgent) {
      agents.update(currentAgents => currentAgents.filter(a => a.id !== currentAgent.id));
      handleCreateAgent();
    }
  }

  onMount(() => {
    // For testing, create some dummy agents
    agents.set([
      {
        id: 1,
        name: "Language Tutor",
        system_prompt: import.meta.env.VITE_DEFAULT_SYSTEM_PROMPT,
        provider: "openai",
        model: "gpt-4-turbo-preview",
        voice: "alloy"
      },
      {
        id: 2,
        name: "Grammar Expert",
        system_prompt: "You are a grammar expert",
        provider: "anthropic",
        model: "claude-3-opus",
        voice: "nova"
      }
    ]);
    isLoading = false;
  });
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

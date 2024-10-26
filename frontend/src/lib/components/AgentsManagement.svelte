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
    agentTemperature,
    agentMaxTokens,
    agentTopP,
    agentFrequencyPenalty,
    agentPresencePenalty,
    agentRole,
    agentConnections,
    agentTools,
    flashingButtons,
    errorStore,
    responseError
  } from '../stores/stores';
  import { get } from 'svelte/store';

  let isLoading: boolean = true;
  const dispatch = createEventDispatcher();

  interface Agent {
    id: number;
    name: string;
    system_prompt: string;
    provider: string;
    model: string;
    voice: string;
    temperature: number;
    max_tokens: number;
    top_p: number;
    frequency_penalty: number;
    presence_penalty: number;
    role: string;
    connections: string;
    tools: string;
  }

  // Placeholder functions for now
  async function handleSelectAgent(agent: Agent) {
    selectedAgent.set(agent);
    agentName.set(agent.name);
    agentSystemPrompt.set(agent.system_prompt);
    agentProvider.set(agent.provider);
    agentModel.set(agent.model);
    agentVoice.set(agent.voice);
    agentTemperature.set(agent.temperature);
    agentMaxTokens.set(agent.max_tokens);
    agentTopP.set(agent.top_p);
    agentFrequencyPenalty.set(agent.frequency_penalty);
    agentPresencePenalty.set(agent.presence_penalty);
    agentRole.set(agent.role);
    agentConnections.set(agent.connections);
    agentTools.set(agent.tools);
  }

  function handleCreateAgent() {
    selectedAgent.set(null);
    agentName.set('');
    agentSystemPrompt.set('');
    agentProvider.set('');
    agentModel.set('');
    agentVoice.set('');
    agentTemperature.set(0.7);
    agentMaxTokens.set(1000);
    agentTopP.set(1.0);
    agentFrequencyPenalty.set(0.0);
    agentPresencePenalty.set(0.0);
    agentRole.set('');
    agentConnections.set('');
    agentTools.set('');
  }

  function handleSaveAgent() {
    const newAgent: Agent = {
      id: get(selectedAgent)?.id || Date.now(),
      name: get(agentName),
      system_prompt: get(agentSystemPrompt),
      provider: get(agentProvider),
      model: get(agentModel),
      voice: get(agentVoice),
      temperature: get(agentTemperature),
      max_tokens: get(agentMaxTokens),
      top_p: get(agentTopP),
      frequency_penalty: get(agentFrequencyPenalty),
      presence_penalty: get(agentPresencePenalty),
      role: get(agentRole),
      connections: get(agentConnections),
      tools: get(agentTools)
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
        system_prompt: "You are a helpful language tutor",
        provider: "OpenAI",
        model: "gpt-4",
        voice: "en-US-Standard-A",
        temperature: 0.7,
        max_tokens: 1000,
        top_p: 1.0,
        frequency_penalty: 0.0,
        presence_penalty: 0.0,
        role: "tutor",
        connections: "",
        tools: ""
      },
      {
        id: 2,
        name: "Grammar Expert",
        system_prompt: "You are a grammar expert",
        provider: "OpenAI",
        model: "gpt-4",
        voice: "en-US-Standard-B",
        temperature: 0.7,
        max_tokens: 1000,
        top_p: 1.0,
        frequency_penalty: 0.0,
        presence_penalty: 0.0,
        role: "expert",
        connections: "",
        tools: ""
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
        <input
          type="text"
          bind:value={$agentProvider}
          placeholder="Provider"
          class="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <input
          type="text"
          bind:value={$agentModel}
          placeholder="Model"
          class="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div class="grid grid-cols-2 gap-4">
        <input
          type="text"
          bind:value={$agentVoice}
          placeholder="Voice"
          class="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <input
          type="number"
          bind:value={$agentTemperature}
          placeholder="Temperature"
          step="0.1"
          min="0"
          max="1"
          class="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div class="grid grid-cols-2 gap-4">
        <input
          type="number"
          bind:value={$agentMaxTokens}
          placeholder="Max Tokens"
          class="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <input
          type="number"
          bind:value={$agentTopP}
          placeholder="Top P"
          step="0.1"
          min="0"
          max="1"
          class="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div class="grid grid-cols-2 gap-4">
        <input
          type="number"
          bind:value={$agentFrequencyPenalty}
          placeholder="Frequency Penalty"
          step="0.1"
          min="0"
          max="2"
          class="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <input
          type="number"
          bind:value={$agentPresencePenalty}
          placeholder="Presence Penalty"
          step="0.1"
          min="0"
          max="2"
          class="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <input
        type="text"
        bind:value={$agentRole}
        placeholder="Role"
        class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
      />

      <input
        type="text"
        bind:value={$agentConnections}
        placeholder="Connections"
        class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
      />

      <input
        type="text"
        bind:value={$agentTools}
        placeholder="Tools"
        class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    </div>
  {/if}
</div>

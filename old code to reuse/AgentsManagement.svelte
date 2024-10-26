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
    responseError,
    authSessionId
  } from '../stores/stores';
  import { get } from 'svelte/store';
  import { handleError, api } from '../lib/api';

  let isLoading: boolean = true;
  const dispatch = createEventDispatcher();

  const getAuthHeaders = () => {
    const sessionId = get(authSessionId);
    console.log('Current session ID:', sessionId);
    return sessionId ? { Authorization: `Bearer ${sessionId}` } : {};
  };

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

  async function fetchAgents(): Promise<Agent[]> {
    try {
      console.log('Fetching agents...');
      const response = await api.get('/api/agents/', { headers: getAuthHeaders() });
      console.log('Agents fetch response:', response);
      agents.set(response.data);
      console.log('Agents set in store:', get(agents));

      const storedAgentName = sessionStorage.getItem('lastSelectedAgent');
      const availableAgents = response.data;

      if (storedAgentName && availableAgents.find((agent: Agent) => agent.name === storedAgentName)) {
        await selectAgent({ name: storedAgentName } as Agent);
      } else if (availableAgents.length > 0) {
        await selectAgent(availableAgents[0]);
      }

      return availableAgents;
    } catch (error) {
      console.error('Error fetching agents:', error);
      errorStore.set(`Failed to fetch agents: ${(error as Error).message}`);
      handleError(error, responseError);
      return [];
    }
  }

  async function selectAgent(agent: Agent): Promise<Agent | void> {
    try {
      selectedAgent.set(agent);
      const response = await api.get(`/api/agents/details/${agent.name}/`, { headers: getAuthHeaders() });
      const agentData: Agent = response.data;
      agentName.set(agentData.name);
      agentSystemPrompt.set(agentData.system_prompt);
      agentProvider.set(agentData.provider);
      agentModel.set(agentData.model);
      agentVoice.set(agentData.voice);
      agentTemperature.set(agentData.temperature);
      agentMaxTokens.set(agentData.max_tokens);
      agentTopP.set(agentData.top_p);
      agentFrequencyPenalty.set(agentData.frequency_penalty);
      agentPresencePenalty.set(agentData.presence_penalty);
      agentRole.set(agentData.role);
      agentConnections.set(agentData.connections);
      agentTools.set(agentData.tools);
      sessionStorage.setItem('lastSelectedAgent', agent.name);
      return agentData;
    } catch (error) {
      console.error('Error selecting agent:', error);
      errorStore.set(`Failed to select agent: ${(error as Error).message}`);
      handleError(error, responseError);
    }
  }

  async function saveAgent(agentData: Agent) {
    try {
      await api.put(`/api/agents/${agentData.name}/update/`, agentData, { headers: getAuthHeaders() });
      await fetchAgents();
      await selectAgent({ name: agentData.name } as Agent);
    } catch (error) {
      console.error('Error saving agent:', error);
      errorStore.set(`Failed to save agent: ${(error as Error).message}`);
      handleError(error, responseError);
    }
  }

  async function deleteAgent(agent: Agent) {
    try {
      await api.post('/api/agents/delete/', { agent_name: agent.name }, { headers: getAuthHeaders() });
      await fetchAgents();

      const updatedAgents = get(agents);
      if (updatedAgents.length > 0) {
        await selectAgent(updatedAgents[0]);
      } else {
        resetAgentData();
        sessionStorage.removeItem('lastSelectedAgent');
      }
    } catch (error) {
      console.error('Error deleting agent:', error);
      errorStore.set(`Failed to delete agent: ${(error as Error).message}`);
      handleError(error, responseError);
    }
  }

  async function updateAgent(agentData: Agent) {
    try {
      await api.put(`/api/agents/${agentData.name}/update/`, agentData, { headers: getAuthHeaders() });
      await fetchAgents();
      await selectAgent({ name: agentData.name } as Agent);
    } catch (error) {
      console.error('Error updating agent:', error);
      errorStore.set(`Failed to update agent: ${(error as Error).message}`);
      handleError(error, responseError);
    }
  }

  async function createAgent(agentData: Agent) {
    try {
      await api.post('/api/agents/create/', agentData, { headers: getAuthHeaders() });
      await fetchAgents();
      await selectAgent({ name: agentData.name } as Agent);
    } catch (error) {
      console.error('Error creating agent:', error);
      errorStore.set(`Failed to create agent: ${(error as Error).message}`);
      handleError(error, responseError);
    }
  }

  async function handleSaveAgent() {
    try {
      const agentData: Agent = {
        id: get(selectedAgent)?.id || 0,
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
        tools: get(agentTools),
      };

      const existingAgent = get(agents).find((agent: Agent) => agent.name === get(agentName));
      if (existingAgent) {
        await updateAgent(agentData);
      } else {
        await createAgent(agentData);
      }
    } catch (error) {
      console.error('Error saving agent:', error);
      errorStore.set(`Failed to save agent: ${(error as Error).message}`);
      handleError(error, responseError);
    }
  }

  function handleCreateAgent() {
    selectedAgent.set(null);
    resetAgentData();
  }

  async function handleDeleteAgent() {
    try {
      const currentAgent = get(selectedAgent);
      if (currentAgent) {
        await deleteAgent({ ...currentAgent, name: currentAgent.name });
        selectedAgent.set(null);
        resetAgentData();

        const updatedAgents = get(agents);
        if (updatedAgents.length > 0) {
          await handleSelectAgent(updatedAgents[0]);
        } else {
          sessionStorage.removeItem('lastSelectedAgent');
        }
      }
    } catch (error) {
      console.error('Error deleting agent:', error);
      errorStore.set(`Failed to delete agent: ${(error as Error).message}`);
      handleError(error, responseError);
    }
  }

  async function handleSelectAgent(agent: Agent) {
    try {
      const agentDetails = await selectAgent(agent);
      if (agentDetails) {
        selectedAgent.set(agentDetails);
        agentName.set(agentDetails.name);
        agentSystemPrompt.set(agentDetails.system_prompt);
        agentProvider.set(agentDetails.provider);
        agentModel.set(agentDetails.model);
        agentVoice.set(agentDetails.voice);
        agentTemperature.set(agentDetails.temperature);
        agentMaxTokens.set(agentDetails.max_tokens);
        agentTopP.set(agentDetails.top_p);
        agentFrequencyPenalty.set(agentDetails.frequency_penalty);
        agentPresencePenalty.set(agentDetails.presence_penalty);
        agentRole.set(agentDetails.role);
        agentConnections.set(agentDetails.connections);
        agentTools.set(agentDetails.tools);
        sessionStorage.setItem('lastSelectedAgent', agent.name);
      }
    } catch (error) {
      console.error('Error selecting agent:', error);
      errorStore.set(`Failed to select agent: ${(error as Error).message}`);
      handleError(error, responseError);
    }
  }

  async function initializeAgents() {
    try {
      await fetchAgents();
    } catch (error) {
      console.error('Error initializing agents:', error);
      errorStore.set(`Failed to initialize agents: ${(error as Error).message}`);
    }
  }

  function resetAgentData() {
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

  async function loadAgents() {
    isLoading = true;
    try {
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Agents loading timed out')), 10000)
      );
      await Promise.race([initializeAgents(), timeoutPromise]);
      dispatch('agentsLoaded');
    } catch (error) {
      console.error('Error initializing agents:', error);
      errorStore.set(`Failed to initialize agents: ${(error as Error).message}`);
      dispatch('agentsError', (error as Error).message);
    } finally {
      isLoading = false;
    }
  }

  onMount(() => {
    console.log('AgentsManagement component mounted');
    loadAgents().catch(error => {
      console.error('Error during onMount:', error);
      errorStore.set(`Error during component mount: ${(error as Error).message}`);
      dispatch('agentsError', (error as Error).message);
    });
  });
</script>

<div class="agents-management">
  {#if isLoading}
    <p>Loading agents... {$errorStore ? `Error: ${$errorStore}` : ''}</p>
  {:else if $agents.length === 0}
    <p>No agents found. {$errorStore ? `Error: ${$errorStore}` : 'Create a new agent to get started.'}</p>
  {:else}
    <div class="agent-list">
      {#each $agents as agent (agent.id)}
        <button
          id={`agent-${agent.id}-button`}
          name={`agent-${agent.id}-button`}
          class:active={$selectedAgent && $selectedAgent.id === agent.id}
          class:flash={$flashingButtons.has(`agent-${agent.id}-button`)}
          on:click={() => handleSelectAgent(agent)}
        >
          {agent.name}
        </button>
      {/each}
    </div>
    <div class="agent-buttons">
      <button id="save-agent-button" name="save-agent-button" class:flash={$flashingButtons.has('save-agent-button')} on:click={handleSaveAgent}>Save Agent</button>
      <button id="create-agent-button" name="create-agent-button" class:flash={$flashingButtons.has('create-agent-button')} on:click={handleCreateAgent}>Create Agent</button>
      <button id="delete-agent-button" name="delete-agent-button" class:flash={$flashingButtons.has('delete-agent-button')} on:click={handleDeleteAgent}>Delete Agent</button>
    </div>

    <input type="text" id="agent-name" name="agent-name" bind:value={$agentName} placeholder="Agent Name" />
    <textarea id="agent-system-prompt" name="agent-system-prompt" bind:value={$agentSystemPrompt} placeholder="System Prompt" class="agent-system-prompt"></textarea>
    <input type="text" id="agent-provider" name="agent-provider" bind:value={$agentProvider} placeholder="Provider" />
    <input type="text" id="agent-model" name="agent-model" bind:value={$agentModel} placeholder="Model" />
    <input type="text" id="agent-voice" name="agent-voice" bind:value={$agentVoice} placeholder="Voice" />
    <input type="number" id="agent-temperature" name="agent-temperature" bind:value={$agentTemperature} placeholder="Temperature" step="0.01" min="0.0" max="1.0" />
    <input type="number" id="agent-max-tokens" name="agent-max-tokens" bind:value={$agentMaxTokens} placeholder="Max Tokens" min="1" />
    <input type="number" id="agent-top-p" name="agent-top-p" bind:value={$agentTopP} placeholder="Top P" step="0.01" min="0.0" max="1.0" />
    <input type="number" id="agent-frequency-penalty" name="agent-frequency-penalty" bind:value={$agentFrequencyPenalty} placeholder="Frequency Penalty" step="0.01" min="0.0" max="2.0" />
    <input type="number" id="agent-presence-penalty" name="agent-presence-penalty" bind:value={$agentPresencePenalty} placeholder="Presence Penalty" step="0.01" min="0.0" max="2.0" />
    <input type="text" id="agent-role" name="agent-role" bind:value={$agentRole} placeholder="Role" />
    <input type="text" id="agent-connections" name="agent-connections" bind:value={$agentConnections} placeholder="Connections" />
    <input type="text" id="agent-tools" name="agent-tools" bind:value={$agentTools} placeholder="Tools" />
  {/if}
</div>

<style>
  .agents-management {
    margin-top: 10px;
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .agent-list {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    justify-content: center;
    margin-bottom: 10px;
  }

  .agent-list button {
    flex: 1 1 calc(33.33% - 10px);
    padding: 10px 20px;
    border-radius: 10px;
    border: 2px solid #556B2F;
    background-color: #C2D2C0;
    cursor: pointer;
  }

  .agent-list button.active {
    background-color: #ff4c4c;
    color: white;
  }

  .agent-buttons {
    display: flex;
    justify-content: space-between;
    gap: 10px;
  }

  .agent-buttons button {
    flex: 1;
  }

  input, textarea {
    width: 100%;
    padding: 10px;
    border-radius: 5px;
    border: 2px solid #556B2F;
  }

  .agent-system-prompt {
    height: 100px;
    resize: vertical;
  }

  .flash {
    animation: flash 0.5s ease-in-out;
  }

  @keyframes flash {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.5;
    }
  }
</style>

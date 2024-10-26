<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { get } from 'svelte/store';
  import { chatHistory, errorStore, isAuthenticated, authSessionId } from '../stores/stores';
  import { api, handleError } from '../lib/api';

  let websocket: WebSocket | null = null;
  let reconnectAttempts = 0;
  const MAX_RECONNECT_ATTEMPTS = 5;
  const RECONNECT_INTERVAL = 5000;

  function setupWebSocket(): void {
    const sessionId = get(authSessionId);
    if (!sessionId) {
      console.error('Auth Session ID is undefined');
      return;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;  // Use window.location.host to ensure correct host in production
    const websocketUrl = `${protocol}//${host}/ws/${sessionId}`;

    console.log(`Connecting to WebSocket at ${websocketUrl}`);
    websocket = new WebSocket(websocketUrl);

    websocket.onopen = (): void => {
      console.log('WebSocket connection established');
      errorStore.set('');
      reconnectAttempts = 0;
    };

    websocket.onmessage = (event: MessageEvent): void => {
      const message = JSON.parse(event.data);
      console.log('Received message:', message);
      if (message.type === 'history_update') {
        chatHistory.set(message.history);
      } else if (message.type === 'chat_message' || message.type === 'agent_response') {
        chatHistory.update(currentHistory => [...currentHistory, message.content]);
      } else if (message.type === 'error') {
        errorStore.set(message.content);
      }
    };

    websocket.onclose = (event: CloseEvent): void => {
      console.log('WebSocket connection closed', event);
      if (event.code === 1000) {
        console.log('WebSocket closed normally, not attempting to reconnect.');
      } else {
        console.log('WebSocket closed unexpectedly, attempting to reconnect...');
        reconnect();
      }
    };

    websocket.onerror = (error: Event): void => {
      console.error('WebSocket error:', error);
      handleError(error as Error, errorStore);
    };
  }

  function reconnect(): void {
    if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
      reconnectAttempts++;
      console.log(`Reconnection attempt ${reconnectAttempts} of ${MAX_RECONNECT_ATTEMPTS}`);
      setTimeout(setupWebSocket, RECONNECT_INTERVAL * reconnectAttempts);
    } else {
      console.error('Max reconnection attempts reached. Please refresh the page.');
      errorStore.set('Unable to establish WebSocket connection. Please refresh the page.');
    }
  }

  function initializeWebSocketHandler(): void {
    if (get(isAuthenticated)) {
      setupWebSocket();
    }

    const unsubscribe = isAuthenticated.subscribe(authenticated => {
      if (authenticated) {
        if (websocket) {
          websocket.close();
        }
        setupWebSocket();
      } else if (websocket) {
        websocket.close();
        websocket = null;
      }
    });

    onDestroy(() => {
      if (websocket) {
        websocket.close();
      }
      unsubscribe();
    });
  }

  onMount(() => {
    initializeWebSocketHandler();
  });
</script>

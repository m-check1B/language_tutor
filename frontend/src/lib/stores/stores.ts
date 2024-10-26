import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

// Types
interface WebSocketState {
    socket: WebSocket | null;
    connected: boolean;
    reconnectAttempts: number;
    lastMessage: any;
    error: string | null;
}

interface ChatMessage {
    id: string;
    content: string;
    user_id: number;
    timestamp: string;
    type: 'user' | 'assistant' | 'system';
    session_id?: string;
}

// Constants
const WS_RECONNECT_INTERVAL = 5000;
const WS_MAX_RECONNECT_ATTEMPTS = 5;

// Initial states
const initialWebSocketState: WebSocketState = {
    socket: null,
    connected: false,
    reconnectAttempts: 0,
    lastMessage: null,
    error: null
};

// Create stores
export const wsState = writable<WebSocketState>(initialWebSocketState);
export const chatMessages = writable<ChatMessage[]>([]);
export const currentSessionId = writable<string | null>(null);

// WebSocket connection management
function setupWebSocket(token: string, sessionId: string) {
    if (!browser) return;

    const wsUrl = `ws://localhost:8001/api/ws/${token}?session=${sessionId}`;
    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
        wsState.update(state => ({
            ...state,
            socket,
            connected: true,
            reconnectAttempts: 0,
            error: null
        }));

        // Start heartbeat
        const heartbeat = setInterval(() => {
            if (socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({ type: 'heartbeat' }));
            } else {
                clearInterval(heartbeat);
            }
        }, 30000);
    };

    socket.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            wsState.update(state => ({ ...state, lastMessage: data }));

            if (data.type === 'message') {
                chatMessages.update(messages => [...messages, {
                    id: crypto.randomUUID(),
                    content: data.content,
                    user_id: data.user_id,
                    timestamp: data.timestamp,
                    type: data.user_id ? 'user' : 'assistant',
                    session_id: data.session_id
                }]);
            } else if (data.type === 'system') {
                chatMessages.update(messages => [...messages, {
                    id: crypto.randomUUID(),
                    content: data.content,
                    user_id: 0,
                    timestamp: data.timestamp,
                    type: 'system'
                }]);
            }
        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    };

    socket.onclose = () => {
        wsState.update(state => {
            const newState = {
                ...state,
                socket: null,
                connected: false
            };

            if (state.reconnectAttempts < WS_MAX_RECONNECT_ATTEMPTS) {
                setTimeout(() => {
                    setupWebSocket(token, sessionId);
                }, WS_RECONNECT_INTERVAL);

                return {
                    ...newState,
                    reconnectAttempts: state.reconnectAttempts + 1
                };
            }

            return {
                ...newState,
                error: 'WebSocket connection failed after maximum retry attempts'
            };
        });
    };

    socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        wsState.update(state => ({
            ...state,
            error: 'WebSocket connection error'
        }));
    };

    return () => {
        if (socket.readyState === WebSocket.OPEN) {
            socket.close();
        }
    };
}

// Derived store for connection status
export const isConnected = derived(wsState, $state => $state.connected);

// Helper function to send messages
export function sendMessage(content: string, sessionId: string) {
    wsState.update(state => {
        if (state.socket?.readyState === WebSocket.OPEN) {
            state.socket.send(JSON.stringify({
                type: 'chat',
                content,
                session_id: sessionId
            }));
        }
        return state;
    });
}

// Export the setup function
export { setupWebSocket };

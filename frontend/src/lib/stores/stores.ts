import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import { auth, authToken, authSessionId } from './auth';
import { get } from 'svelte/store';

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

interface Agent {
    id: number;
    name: string;
    provider: string;
    model: string;
    system_prompt: string;
}

// Constants
const WS_RECONNECT_INTERVAL = 5000;
const WS_MAX_RECONNECT_ATTEMPTS = 5;
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api';
const WS_URL = API_URL.replace('http', 'ws');

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
export const chatHistory = writable<ChatMessage[]>([]);
export const userMessage = writable<string>('');
export const isAudioRecording = writable<boolean>(false);
export const isVideoRecording = writable<boolean>(false);
export const flashingButtons = writable<boolean>(false);
export const isLoading = writable<boolean>(false);
export const selectedAgent = writable<Agent | null>(null);
export const transcriptionError = writable<string | null>(null);
export const responseError = writable<string | null>(null);
export const selectedVoice = writable<string>('alloy');
export const speechSpeed = writable<number>(1.0);
export const wsConnection = writable<{isConnected: boolean}>({ isConnected: false });

// Agent-related stores
export const agents = writable<Agent[]>([]);
export const agentProvider = writable<string>('openai');
export const agentName = writable<string>('');
export const agentSystemPrompt = writable<string>('');
export const agentModel = writable<string>('');
export const agentVoice = writable<string>('alloy');
export const availableModels = writable<string[]>([]);
export const errorStore = writable<string | null>(null);

// WebSocket connection management
export async function setupWebSocket() {
    if (!browser) return;

    const token = get(authToken);
    const sessionId = get(authSessionId);

    if (!token || !sessionId) {
        console.error('Missing token or session ID');
        return;
    }

    const wsUrl = `${WS_URL}/ws/${token}?session=${sessionId}`;
    console.log('Connecting to WebSocket:', wsUrl);
    
    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
        console.log('WebSocket connected');
        wsState.update(state => ({
            ...state,
            socket,
            connected: true,
            reconnectAttempts: 0,
            error: null
        }));
        wsConnection.set({ isConnected: true });

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
            console.log('WebSocket message received:', data);
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

    socket.onclose = (event) => {
        console.log('WebSocket closed:', event);
        wsConnection.set({ isConnected: false });
        wsState.update(state => {
            const newState = {
                ...state,
                socket: null,
                connected: false
            };

            if (state.reconnectAttempts < WS_MAX_RECONNECT_ATTEMPTS) {
                setTimeout(() => {
                    setupWebSocket();
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

// Helper function to send messages
export function sendWebSocketMessage(message: string) {
    wsState.update(state => {
        if (state.socket?.readyState === WebSocket.OPEN) {
            const messageData = {
                type: 'chat',
                content: message,
                session_id: get(authSessionId)
            };
            console.log('Sending WebSocket message:', messageData);
            state.socket.send(JSON.stringify(messageData));
        }
        return state;
    });
}

// Export disconnect function
export function disconnectWebSocket() {
    wsState.update(state => {
        if (state.socket?.readyState === WebSocket.OPEN) {
            state.socket.close();
        }
        return {
            ...initialWebSocketState
        };
    });
    wsConnection.set({ isConnected: false });
}

import { writable, get } from 'svelte/store';
import { auth } from './auth';

// Chat stores
export const chatHistory = writable<Array<{ text: string; isUser: boolean; audioUrl?: string }>>([]);
export const userMessage = writable('');
export const isAudioRecording = writable(false);
export const isVideoRecording = writable(false);
export const flashingButtons = writable(new Set<string>());
export const isLoading = writable(false);
export const transcriptionError = writable('');
export const responseError = writable('');
export const selectedVoice = writable('en-US-Standard-A');
export const speechSpeed = writable(1.0);
export const isSilentMode = writable(false);

// WebSocket store
export const wsConnection = writable<{
    socket: WebSocket | null;
    isConnected: boolean;
}>({
    socket: null,
    isConnected: false
});

// Agent stores
export const agents = writable<any[]>([]);
export const selectedAgent = writable<any>(null);
export const agentName = writable('');
export const agentSystemPrompt = writable('');
export const agentProvider = writable('');
export const agentModel = writable('');
export const agentVoice = writable('');
export const errorStore = writable('');

// WebSocket functions
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;
const reconnectDelay = 1000;

export function setupWebSocket() {
    const authState = get(auth);
    if (!authState.token) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//localhost:8001/api/ws/${authState.token}`;
    
    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
        wsConnection.update(state => ({ ...state, socket, isConnected: true }));
        reconnectAttempts = 0;
        console.log('WebSocket connected');
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'message') {
            chatHistory.update(history => [
                ...history,
                {
                    text: data.content,
                    isUser: false,
                    audioUrl: data.audioUrl
                }
            ]);

            // Handle TTS for response
            if (data.audioUrl && !get(isSilentMode)) {
                const audio = new Audio(data.audioUrl);
                audio.playbackRate = get(speechSpeed);
                audio.play();
            }
        }
    };

    socket.onclose = () => {
        wsConnection.update(state => ({ ...state, socket: null, isConnected: false }));
        console.log('WebSocket disconnected');
        
        if (reconnectAttempts < maxReconnectAttempts) {
            setTimeout(() => {
                reconnectAttempts++;
                setupWebSocket();
            }, reconnectDelay * Math.pow(2, reconnectAttempts));
        }
    };

    socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        socket.close();
    };
}

export function disconnectWebSocket() {
    wsConnection.update(state => {
        if (state.socket) {
            state.socket.close();
        }
        return { socket: null, isConnected: false };
    });
}

export function sendWebSocketMessage(message: string) {
    const connection = get(wsConnection);
    const activeAgent = get(selectedAgent);
    
    if (connection.socket && connection.isConnected) {
        chatHistory.update(history => [
            ...history,
            { text: message, isUser: true }
        ]);

        const messageData = {
            type: 'text',
            content: message,
            agent_name: activeAgent?.name || '',
            ttsSettings: {
                voice: get(selectedVoice),
                speed: get(speechSpeed),
                isSilentMode: get(isSilentMode)
            }
        };

        connection.socket.send(JSON.stringify(messageData));
    } else {
        console.error('WebSocket not connected');
        responseError.set('Connection error. Please try again.');
    }
}

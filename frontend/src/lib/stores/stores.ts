import { writable, get } from 'svelte/store';
import { auth, authSessionId } from './auth';

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
export const agentTemperature = writable(0.7);
export const agentMaxTokens = writable(1000);
export const agentTopP = writable(1.0);
export const agentFrequencyPenalty = writable(0.0);
export const agentPresencePenalty = writable(0.0);
export const agentRole = writable('');
export const agentConnections = writable('');
export const agentTools = writable('');
export const errorStore = writable('');

// WebSocket functions
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;
const reconnectDelay = 1000;

export function setupWebSocket() {
    const authState = get(auth);
    if (!authState.token) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/chat/ws/${authState.token}`;
    
    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
        wsConnection.update(state => ({ ...state, socket, isConnected: true }));
        reconnectAttempts = 0;
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
    if (connection.socket && connection.isConnected) {
        connection.socket.send(JSON.stringify({
            type: 'text',
            content: message,
            ttsSettings: {
                voice: get(selectedVoice),
                speed: get(speechSpeed),
                isSilentMode: get(isSilentMode)
            }
        }));
    }
}

// Audio functions
export async function sendAudioData(blob: Blob) {
    const formData = new FormData();
    formData.append('audio', blob, 'recording.wav');

    try {
        const authState = get(auth);
        formData.append('ttsSettings', JSON.stringify({
            voice: get(selectedVoice),
            speed: get(speechSpeed),
            isSilentMode: get(isSilentMode)
        }));

        const response = await fetch('/api/chat/audio', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authState.token}`
            },
            body: formData
        });

        if (!response.ok) throw new Error('Failed to send audio');

        return await response.json();
    } catch (error) {
        console.error('Error sending audio:', error);
        throw error;
    }
}

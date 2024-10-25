import { writable } from 'svelte/store';
import { auth } from './auth';
import { get } from 'svelte/store';

export interface ChatMessage {
    id: string;
    message: string;
    isUser: boolean;
    timestamp: string;
    audioUrl?: string | null;
}

interface ChatState {
    messages: ChatMessage[];
    isRecording: boolean;
    audioBlob: Blob | null;
    mediaRecorder: MediaRecorder | null;
    stream: MediaStream | null;
    socket: WebSocket | null;
    isConnected: boolean;
}

interface AuthState {
    isLoggedIn: boolean;
    token: string | null;
    user: any | null;
}

function createChatStore() {
    const { subscribe, set, update } = writable<ChatState>({
        messages: [],
        isRecording: false,
        audioBlob: null,
        mediaRecorder: null,
        stream: null,
        socket: null,
        isConnected: false
    });

    let reconnectAttempts = 0;
    const maxReconnectAttempts = 5;
    const reconnectDelay = 1000; // Start with 1 second

    function setupWebSocket() {
        const authState = get(auth) as unknown as AuthState;
        if (!authState?.token) return;

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/api/chat/ws/${authState.token}`;
        
        const socket = new WebSocket(wsUrl);

        socket.onopen = () => {
            update(state => ({ ...state, socket, isConnected: true }));
            reconnectAttempts = 0;
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'message') {
                const store = get({ subscribe }) as ChatState;
                update(state => ({
                    ...state,
                    messages: [...state.messages, {
                        id: crypto.randomUUID(),
                        message: data.content,
                        isUser: false,
                        timestamp: new Date().toLocaleTimeString(),
                        audioUrl: data.audioUrl
                    }]
                }));
            }
        };

        socket.onclose = () => {
            update(state => ({ ...state, socket: null, isConnected: false }));
            
            // Attempt to reconnect with exponential backoff
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

    return {
        subscribe,
        connect: setupWebSocket,
        disconnect: () => {
            update(state => {
                if (state.socket) {
                    state.socket.close();
                }
                return { ...state, socket: null, isConnected: false };
            });
        },
        addMessage: (message: string, isUser: boolean, audioUrl?: string) => {
            update(state => ({
                ...state,
                messages: [...state.messages, {
                    id: crypto.randomUUID(),
                    message,
                    isUser,
                    timestamp: new Date().toLocaleTimeString(),
                    audioUrl
                }]
            }));
        },
        sendMessage: async (message: string) => {
            update(state => {
                if (state.socket && state.isConnected) {
                    state.socket.send(JSON.stringify({
                        type: 'text',
                        content: message
                    }));
                }
                return state;
            });
        },
        startRecording: async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                const mediaRecorder = new MediaRecorder(stream);
                const chunks: BlobPart[] = [];

                mediaRecorder.ondataavailable = (e) => {
                    chunks.push(e.data);
                };

                mediaRecorder.onstop = () => {
                    const blob = new Blob(chunks, { type: 'audio/wav' });
                    update(state => ({ ...state, audioBlob: blob }));
                };

                mediaRecorder.start();

                update(state => ({
                    ...state,
                    isRecording: true,
                    mediaRecorder,
                    stream
                }));
            } catch (error) {
                console.error('Error starting recording:', error);
                throw error;
            }
        },
        stopRecording: () => {
            update(state => {
                if (state.mediaRecorder) {
                    state.mediaRecorder.stop();
                }
                if (state.stream) {
                    state.stream.getTracks().forEach(track => track.stop());
                }
                return {
                    ...state,
                    isRecording: false,
                    mediaRecorder: null,
                    stream: null
                };
            });
        },
        sendAudio: async (blob: Blob) => {
            const formData = new FormData();
            formData.append('audio', blob, 'recording.wav');

            try {
                const authState = get(auth) as unknown as AuthState;
                const response = await fetch('/api/chat/audio', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${authState?.token}`
                    },
                    body: formData
                });

                if (!response.ok) throw new Error('Failed to send audio');

                const data = await response.json();
                return data;
            } catch (error) {
                console.error('Error sending audio:', error);
                throw error;
            }
        },
        clearAudioBlob: () => {
            update(state => ({ ...state, audioBlob: null }));
        },
        clearMessages: () => {
            update(state => ({ ...state, messages: [] }));
        }
    };
}

export const chatStore = createChatStore();

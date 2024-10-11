import { render, fireEvent, screen } from '@testing-library/svelte';
import Chat from '../src/routes/chat/+page.svelte';
import { goto } from '$app/navigation';
import { currentConversation, chatMessages, token } from '../src/stores';

// Mock the $app/navigation module
jest.mock('$app/navigation', () => ({
  goto: jest.fn(),
}));

// Mock the stores
jest.mock('../src/stores', () => ({
  currentConversation: {
    subscribe: jest.fn(),
    set: jest.fn(),
  },
  chatMessages: {
    subscribe: jest.fn(),
    set: jest.fn(),
    update: jest.fn(),
  },
  token: {
    subscribe: jest.fn(() => () => {}),
  },
}));

describe('WebSocket Integration', () => {
  let mockWebSocket: jest.Mock;
  let mockAddEventListener: jest.Mock;
  let mockSend: jest.Mock;

  beforeEach(() => {
    mockAddEventListener = jest.fn();
    mockSend = jest.fn();
    mockWebSocket = jest.fn().mockImplementation(function(this: any) {
      this.addEventListener = mockAddEventListener;
      this.send = mockSend;
    });
    (global as any).WebSocket = mockWebSocket;

    // Mock token value
    (token.subscribe as jest.Mock).mockImplementation((callback: (value: string) => void) => {
      callback('mock-token');
      return () => {};
    });
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('establishes WebSocket connection on component mount', () => {
    render(Chat);
    expect(mockWebSocket).toHaveBeenCalledWith('ws://localhost:8000/ws/mock-token');
  });

  it('sends message through WebSocket', async () => {
    (currentConversation.subscribe as jest.Mock).mockImplementation((callback: (value: number) => void) => {
      callback(1);
      return () => {};
    });

    render(Chat);

    const input = screen.getByPlaceholderText('Type your message...');
    await fireEvent.input(input, { target: { value: 'Hello, WebSocket!' } });
    await fireEvent.click(screen.getByRole('button', { name: 'Send' }));

    expect(mockSend).toHaveBeenCalledWith('1:Hello, WebSocket!');
  });

  it('receives and processes messages from WebSocket', () => {
    render(Chat);

    // Simulate receiving a message from the WebSocket
    const messageEventListener = mockAddEventListener.mock.calls.find(
      (call: any[]) => call[0] === 'message'
    )[1];

    messageEventListener({ data: '1:Received message:false' });

    expect(chatMessages.update).toHaveBeenCalled();
  });
});

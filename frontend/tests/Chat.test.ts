import { render, fireEvent, screen } from '@testing-library/svelte';
import Chat from '../src/routes/chat/+page.svelte';
import { goto } from '$app/navigation';
import { currentConversation, chatMessages } from '../src/stores';

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
}));

describe('Chat Component', () => {
  let fetchMock: jest.SpyInstance;

  beforeEach(() => {
    fetchMock = jest.spyOn(window, 'fetch').mockImplementation(jest.fn());
    // Reset mocked stores
    (currentConversation.set as jest.Mock).mockClear();
    (chatMessages.set as jest.Mock).mockClear();
    (chatMessages.update as jest.Mock).mockClear();
  });

  afterEach(() => {
    fetchMock.mockRestore();
  });

  it('renders chat interface', () => {
    render(Chat);
    expect(screen.getByPlaceholderText('Type your message...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Send' })).toBeInTheDocument();
  });

  it('starts a new conversation on mount if no current conversation', async () => {
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 1 }),
    } as Response);

    render(Chat);

    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/api/conversations',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          'Authorization': expect.stringContaining('Bearer '),
        }),
      })
    );

    expect(currentConversation.set).toHaveBeenCalledWith(1);
  });

  it('sends a message and updates chat messages', async () => {
    const mockMessages = [
      { id: 1, content: 'Hello', is_user: true },
      { id: 2, content: 'Hi there!', is_user: false },
    ];

    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => mockMessages,
    } as Response);

    render(Chat);

    const input = screen.getByPlaceholderText('Type your message...');
    await fireEvent.input(input, { target: { value: 'Hello' } });
    await fireEvent.click(screen.getByRole('button', { name: 'Send' }));

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/api/conversations/'),
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          'Authorization': expect.stringContaining('Bearer '),
          'Content-Type': 'application/json',
        }),
        body: JSON.stringify({ content: 'Hello' }),
      })
    );

    expect(chatMessages.update).toHaveBeenCalled();
  });
});

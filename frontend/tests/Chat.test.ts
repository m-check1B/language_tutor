import { render, fireEvent, screen } from '@testing-library/svelte';
import '@testing-library/jest-dom';
import Chat from '../src/routes/[lang]/chat/+page.svelte';
import { goto } from '$app/navigation';
import { currentConversation, chatMessages } from '../src/stores';

// Extend Jest matchers
declare global {
  namespace jest {
    interface Matchers<R> {
      toBeInTheDocument(): R;
    }
  }
}

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
  let mockMediaRecorder: Partial<MediaRecorder>;
  let mockAudio: Partial<HTMLAudioElement>;

  beforeEach(() => {
    fetchMock = jest.spyOn(window, 'fetch').mockImplementation(jest.fn());
    // Reset mocked stores
    jest.mocked(currentConversation.set).mockClear();
    jest.mocked(chatMessages.set).mockClear();
    jest.mocked(chatMessages.update).mockClear();

    // Mock MediaRecorder
    mockMediaRecorder = {
      start: jest.fn(),
      stop: jest.fn(),
      ondataavailable: jest.fn(),
      onstop: jest.fn(),
    };
    global.MediaRecorder = jest.fn(() => mockMediaRecorder) as unknown as typeof MediaRecorder;
    jest.mocked(global.MediaRecorder).isTypeSupported = jest.fn().mockReturnValue(true);

    // Mock navigator.mediaDevices
    Object.defineProperty(global.navigator, 'mediaDevices', {
      value: {
        getUserMedia: jest.fn().mockResolvedValue('mock-stream'),
      },
      writable: true,
    });

    // Mock URL.createObjectURL
    global.URL.createObjectURL = jest.fn().mockReturnValue('mock-audio-url');

    // Mock Audio
    mockAudio = {
      play: jest.fn().mockResolvedValue(undefined),
    };
    global.Audio = jest.fn(() => mockAudio) as unknown as typeof Audio;
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

  // New tests for the "torture" button functionality
  it('renders the torture button', () => {
    render(Chat);
    expect(screen.getByRole('button', { name: '🔁 Hold to Torture' })).toBeInTheDocument();
  });

  it('starts recording when torture button is pressed', async () => {
    render(Chat);
    const tortureButton = screen.getByRole('button', { name: '🔁 Hold to Torture' });
    await fireEvent.mouseDown(tortureButton);

    expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalledWith({ audio: true });
    expect(global.MediaRecorder).toHaveBeenCalledWith('mock-stream');
    expect(mockMediaRecorder.start).toHaveBeenCalled();
    expect(tortureButton.textContent).toBe('🔴 Torturing...');
  });

  it('stops recording and plays audio when torture button is released', async () => {
    render(Chat);
    const tortureButton = screen.getByRole('button', { name: '🔁 Hold to Torture' });
    await fireEvent.mouseDown(tortureButton);
    await fireEvent.mouseUp(tortureButton);

    expect(mockMediaRecorder.stop).toHaveBeenCalled();
    expect(tortureButton.textContent).toBe('🔁 Hold to Torture');
    expect(global.URL.createObjectURL).toHaveBeenCalled();
    expect(global.Audio).toHaveBeenCalledWith('mock-audio-url');
    expect(mockAudio.play).toHaveBeenCalled();
  });
});

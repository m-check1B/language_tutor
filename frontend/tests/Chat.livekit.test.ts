import { render, fireEvent, screen } from '@testing-library/svelte';
import { jest } from '@jest/globals';
import Chat from '../src/routes/chat/+page.svelte';
import { goto } from '$app/navigation';
import { currentConversation, chatMessages, token } from '../src/stores';
import { Room, RoomEvent, LocalParticipant, RemoteParticipant } from 'livekit-client';

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

// Mock the livekit-client module
jest.mock('livekit-client', () => ({
  Room: jest.fn().mockImplementation(() => ({
    connect: jest.fn().mockResolvedValue(undefined),
    on: jest.fn(),
    localParticipant: {
      setMicrophoneEnabled: jest.fn(),
    },
  })),
  RoomEvent: {
    ParticipantConnected: 'participantConnected',
    TrackSubscribed: 'trackSubscribed',
  },
}));

describe('Chat Component with LiveKit', () => {
  let mockFetch: jest.SpyInstance;

  beforeEach(() => {
    mockFetch = jest.spyOn(global, 'fetch').mockImplementation(
      jest.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ access_token: 'mock_token' }),
        })
      ) as jest.Mock
    );

    (token.subscribe as jest.Mock).mockImplementation((callback: (value: string) => void) => {
      callback('mock_token');
      return () => {};
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('initializes LiveKit room on mount', async () => {
    render(Chat);
    
    // Wait for the component to mount and initialize LiveKit
    await new Promise(resolve => setTimeout(resolve, 0));

    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/livekit/join-room',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          'Authorization': 'Bearer mock_token',
        }),
      })
    );

    expect(Room).toHaveBeenCalled();
    const mockRoom = (Room as jest.Mock).mock.results[0].value;
    expect(mockRoom.connect).toHaveBeenCalledWith('wss://your-livekit-server-url', 'mock_token');
  });

  it('toggles audio when button is clicked', async () => {
    render(Chat);

    // Wait for the component to mount and initialize LiveKit
    await new Promise(resolve => setTimeout(resolve, 0));

    const audioButton = screen.getByText('Enable Audio');
    await fireEvent.click(audioButton);

    const mockRoom = (Room as jest.Mock).mock.results[0].value;
    expect(mockRoom.localParticipant.setMicrophoneEnabled).toHaveBeenCalledWith(true);

    expect(audioButton.textContent).toBe('Disable Audio');

    await fireEvent.click(audioButton);
    expect(mockRoom.localParticipant.setMicrophoneEnabled).toHaveBeenCalledWith(false);
    expect(audioButton.textContent).toBe('Enable Audio');
  });

  // Add more tests for LiveKit functionality as needed
});

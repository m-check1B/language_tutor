import '@testing-library/jest-dom';
import { jest, expect, describe, it, beforeEach, afterEach } from '@jest/globals';

declare global {
  const jest: typeof jest & {
    spyOn: <T extends {}, M extends keyof T>(object: T, method: M) => jest.SpyInstance<T[M], any[]>;
  };
  const expect: typeof expect;
  const describe: typeof describe;
  const it: typeof it;
  const beforeEach: typeof beforeEach;
  const afterEach: typeof afterEach;
  const global: typeof globalThis;

  namespace jest {
    interface SpyInstance<T = any, Y extends any[] = any[]> {
      mockImplementation(fn: (...args: Y) => T): this;
      mockResolvedValue(value: T): this;
      mockResolvedValueOnce(value: T): this;
      mockRestore(): void;
    }
    type Mock<T = any> = jest.MockInstance<T, any[]> & {
      mockClear(): void;
    };
  }
}

declare module '@testing-library/svelte' {
  export const render: (component: any, options?: any) => {
    container: HTMLElement;
    component: any;
    debug: (element?: HTMLElement) => void;
    rerender: (props?: any) => void;
    unmount: () => void;
  };
  export const fireEvent: {
    click: (element: HTMLElement) => Promise<void>;
    input: (element: HTMLElement, options: { target: { value: string } }) => Promise<void>;
  };
  export const screen: {
    getByLabelText: (text: string) => HTMLElement;
    getByRole: (role: string, options?: { name: string }) => HTMLElement;
    getByPlaceholderText: (text: string) => HTMLElement;
    getByText: (text: string) => HTMLElement;
    findByText: (text: string) => Promise<HTMLElement>;
  };
}

declare module '$app/navigation' {
  export function goto(path: string): Promise<void>;
}

declare module '$app/environment' {
  export const browser: boolean;
}

declare module 'livekit-client' {
  export class Room {
    connect(url: string, token: string): Promise<void>;
    on(event: string, listener: (...args: any[]) => void): void;
    localParticipant: LocalParticipant;
  }

  export class LocalParticipant {
    setMicrophoneEnabled(enabled: boolean): Promise<void>;
  }

  export class RemoteParticipant {}

  export enum RoomEvent {
    ParticipantConnected = 'participantConnected',
    TrackSubscribed = 'trackSubscribed',
  }
}

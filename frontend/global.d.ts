/// <reference types="svelte" />
/// <reference types="vite/client" />

declare module '@testing-library/svelte' {
  import { SvelteComponent } from 'svelte';
  
  export function render(component: typeof SvelteComponent, options?: any): any;
  export const fireEvent: any;
  export const screen: any;
}

declare module '$app/navigation' {
  export function goto(path: string): Promise<void>;
}

declare module '$app/environment' {
  export const browser: boolean;
}

declare namespace jest {
  interface Matchers<R> {
    toBeInTheDocument(): R;
  }
  
  type Mock<T extends (...args: any[]) => any> = {
    (...args: Parameters<T>): ReturnType<T>;
    mock: {
      calls: Parameters<T>[];
      results: { type: 'return' | 'throw'; value: ReturnType<T> }[];
      instances: T[];
      contexts: any[];
      lastCall: Parameters<T>;
    };
  } & T;
}

declare global {
  interface Window {
    fetch: jest.Mock;
  }
}

export {};

declare global {
  interface Window {
    timezone?: {
      system?: string;
      user?: string;
    };
  }

  function __(str: string, values?: any[]): string;
}

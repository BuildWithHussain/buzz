export {};

declare global {
  interface Window {
    timezone?: {
      system?: string;
      user?: string;
    };
  }
}

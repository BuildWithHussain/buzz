export {};

declare global {
  interface Window {
    timezone?: {
      system?: string;
      user?: string;
    };
    site_name?: string;
  }

  function __(str: string, values?: any[]): string;
}

declare module "@vue/runtime-core" {
  interface ComponentCustomProperties {
    __(str: string, values?: any[]): string;
  }
}

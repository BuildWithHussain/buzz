export {};

declare global {
  interface Window {
    timezone?: {
      system?: string;
      user?: string;
    };
  }

  function __(str: string, values?: any[]): string;

  declare module "*.wav" {
    const value: string;
    export default value;
  }

  declare module "*.mp3" {
    const value: string;
    export default value;
  }

  declare module "*.svg" {
    const value: string;
    export default value;
  }
}

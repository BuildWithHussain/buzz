export {};

declare module '@vue/runtime-core' {
  export interface GlobalComponents {
    RouterLink: (typeof import('vue-router'))['RouterLink']
    RouterView: (typeof import('vue-router'))['RouterView']
    Button: (typeof import('frappe-ui'))['Button']
    Input: (typeof import('frappe-ui'))['Input']
    TextInput: (typeof import('frappe-ui'))['TextInput']
    FormControl: (typeof import('frappe-ui'))['FormControl']
    ErrorMessage: (typeof import('frappe-ui'))['ErrorMessage']
    Dialog: (typeof import('frappe-ui'))['Dialog']
    Alert: (typeof import('frappe-ui'))['Alert']
    Badge: (typeof import('frappe-ui'))['Badge']
  }
  export interface ComponentCustomProperties {
    $socket: import('socket.io-client').Socket;
    __: (message: string, replace?: any[], context?: string) => string;
  }
}

declare global {
  interface Window {
    frappe: any;
    __: (message: string, replace?: any[], context?: string) => string;
    site_name: string;
    time_zone: string;
    timezone?: {
      system: string;
      user: string;
    };
    translatedMessages: Record<string, string>;
  }
  const __: (message: string, replace?: any[], context?: string) => string;
}


declare module "*.wav" {
  const src: string;
  export default src;
}

declare module "*.mp3" {
  const src: string;
  export default src;
}

declare module "*.png" {
  const src: string;
  export default src;
}

declare module "*.jpg" {
  const src: string;
  export default src;
}

declare module "*.svg" {
  const src: string;
  export default src;
}

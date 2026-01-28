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
}

declare module "*.vue" {
  import type { DefineComponent } from "vue";
  const component: DefineComponent<{}, {}, any>;
  export default component;
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

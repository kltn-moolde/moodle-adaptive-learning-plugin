/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_MOODLE_URL: string;
  readonly VITE_MOODLE_TOKEN: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

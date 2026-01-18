import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load các biến môi trường dựa theo mode (development, production)
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [react()],
    server: {
      port: 5173, // có thể đổi nếu muốn
    },
    define: {
      // Truyền biến môi trường vào code phía client
      'import.meta.env.VITE_MOODLE_URL': JSON.stringify(env.VITE_MOODLE_URL),
      'import.meta.env.VITE_MOODLE_TOKEN': JSON.stringify(env.VITE_MOODLE_TOKEN),
    },
  };
});
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev server binds to localhost by default (mirrors [310] SEC-1 posture).
export default defineConfig({
  plugins: [react()],
  server: { host: "127.0.0.1", port: 5173 },
});

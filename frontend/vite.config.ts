import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const apiTarget =
  process.env.DOCKER === "true" ? "http://api:8000" : "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      "/jobs": apiTarget,
      "/health": apiTarget,
    },
  },
});

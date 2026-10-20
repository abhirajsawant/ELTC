import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Configure Vite to serve React during development and build production assets.
export default defineConfig({ plugins: [react()], server: { port: 5173 } });

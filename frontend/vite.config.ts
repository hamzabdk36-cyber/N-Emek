/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    // Backend ayri portta; gelistirmede vekil uzerinden gidiyoruz ki
    // arayuz kodunda mutlak URL tutmayalim.
    proxy: {
      "/api": { target: "http://127.0.0.1:8000", changeOrigin: true },
    },
  },
  test: {
    // jsdom: bilesenler DOM'a baglaniyor. Tarayici acmaya gerek yok,
    // sinanan sey yerlesim hesabi ve isaretleme - piksel boyama degil.
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    include: ["src/**/*.test.{ts,tsx}"],
    css: false,
    restoreMocks: true,
  },
});

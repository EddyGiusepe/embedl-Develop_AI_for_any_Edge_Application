/**
 * Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro
 *
 * main.tsx
 * ========
 * Frontend bootstrap file executed first by Vite.
 *
 * Mounts the React app into #root and wires the global providers:
 * - ThemeProvider: light/dark/system theme handling
 * - QueryClientProvider: fetch cache and job polling state
 * - Toaster: temporary UI notifications
 *
 * RUN
 * ---
 * npm run dev   (development server at http://localhost:5173)
 */

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "next-themes";

import App from "./App";
import { Toaster } from "@/components/ui/sonner";
import "./index.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const root = document.getElementById("root");
if (!root) {
  throw new Error("Element #root not found in index.html");
}

createRoot(root).render(
  <StrictMode>
    {/*
      ThemeProvider from next-themes:
      - attribute="class": applies/removes the `.dark` class on <html>, combining
        with `@custom-variant dark (&:is(.dark *))` in src/index.css.
      - defaultTheme="system": on first visit, respects the system preference
        (prefers-color-scheme). On subsequent visits, uses the value saved in
        localStorage.
      - enableSystem: allows the "system" value in setTheme (in addition to light/dark).
      - disableTransitionOnChange: avoids "flash" of CSS transitions when the theme changes.
      - storageKey: key used in localStorage (avoids collision with other apps).
    */}
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
      storageKey="embedl-theme"
    >
      <QueryClientProvider client={queryClient}>
        <App />
        <Toaster position="bottom-right" richColors />
      </QueryClientProvider>
    </ThemeProvider>
  </StrictMode>
);

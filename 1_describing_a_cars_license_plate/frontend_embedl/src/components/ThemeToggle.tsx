/**
 * Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro
 *
 * ThemeToggle.tsx
 * ================
 * Button used to toggle between light and dark themes.
 *
 */
import { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";

import { Button } from "@/components/ui/button";

/**
 * Button used to toggle between light and dark themes.
 *
 * Uses next-themes (configured in src/main.tsx). When clicked, toggles
 * between "light" and "dark" — even if the internal state is "system",
 * `resolvedTheme` tells us which theme is actually applied, and we use
 * that to decide the next value.
 */
export function ThemeToggle() {
  const { resolvedTheme, setTheme } = useTheme();

  // Avoid "hydration mismatch": on the first render, the server (or the initial HTML)
  // doesn't know which theme will be applied. Rendering the icon before the mount
  // causes flicker (light turning to moon). We wait for the mount to then render
  // the correct icon.
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    // Placeholder of the same size as the button, avoids "jump" in the layout.
    return <Button variant="ghost" size="icon" aria-hidden="true" disabled />;
  }

  // resolvedTheme is always "light" or "dark" (resolve "system" to one of them).
  const isDark = resolvedTheme === "dark";

  function toggle() {
    setTheme(isDark ? "light" : "dark");
  }

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={toggle}
      aria-label={isDark ? "Change to light theme" : "Change to dark theme"}
      title={isDark ? "Light theme" : "Dark theme"}
    >
      {isDark ? <Moon className="size-5" /> : <Sun className="size-5" />}
    </Button>
  );
}

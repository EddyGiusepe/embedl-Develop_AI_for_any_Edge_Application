/**
 * Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro
 *
 * Header.tsx
 * ==========
 * Application-specific header that displays the logo, title, model subtitle,
 * and theme toggle.
 *
 */
import { Car } from "lucide-react";

import { ThemeToggle } from "@/components/ThemeToggle";

export function Header() {
  return (
    <header className="border-b bg-background/70 backdrop-blur sticky top-0 z-10">
      <div className="mx-auto flex max-w-4xl items-center gap-3 px-4 py-4">
        <div className="rounded-lg bg-primary/10 p-2">
          <Car className="size-6 text-primary" />
        </div>
        <div>
          <h1 className="text-lg font-semibold leading-tight">
          Vehicle license plate analyzer in Images and Videos
          </h1>
          <p className="text-xs text-muted-foreground">
            Powered by embedl/Cosmos-Reason2-2B-W4A16 - Edge AI
          </p>
        </div>

        {/* ml-auto pushes the toggle to the right side of the header. */}
        <div className="ml-auto">
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}

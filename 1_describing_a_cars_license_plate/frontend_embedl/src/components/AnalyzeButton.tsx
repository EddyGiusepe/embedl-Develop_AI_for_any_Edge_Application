/**
 * Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro
 *
 * AnalyzeButton.tsx
 * ==================
 * Button used to start the image/video license plate analysis flow.
 *
 */
import { Loader2, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";

interface AnalyzeButtonProps {
  onClick: () => void;
  isUploading: boolean;
  isProcessing: boolean;
  disabled?: boolean;
}

export function AnalyzeButton({
  onClick,
  isUploading,
  isProcessing,
  disabled = false,
}: AnalyzeButtonProps) {
  const busy = isUploading || isProcessing;
  const label = isUploading
    ? "Sending..."
    : isProcessing
      ? "Analyzing..."
      : "Analyze License Plate";

  return (
    <Button
      onClick={onClick}
      disabled={disabled || busy}
      size="lg"
      className="w-full"
    >
      {busy ? (
        <Loader2 className="size-4 animate-spin" />
      ) : (
        <Sparkles className="size-4" />
      )}
      {label}
    </Button>
  );
}

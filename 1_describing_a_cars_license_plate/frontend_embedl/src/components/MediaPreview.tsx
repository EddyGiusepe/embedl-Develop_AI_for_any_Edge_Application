/**
 * Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro
 *
 * MediaPreview.tsx
 * =================
 * Shows a preview of the selected image or video file in the UI.
 *
 */
import { useEffect, useState } from "react";
import { X, FileImage, FileVideo } from "lucide-react";

import { Button } from "@/components/ui/button";
import type { MediaType } from "@/lib/types";

interface MediaPreviewProps {
  file: File;
  mediaType: MediaType;
  onClear: () => void;
  disabled?: boolean;
}

export function MediaPreview({
  file,
  mediaType,
  onClear,
  disabled = false,
}: MediaPreviewProps) {
  const [objectUrl, setObjectUrl] = useState<string>("");

  useEffect(() => {
    const url = URL.createObjectURL(file);
    setObjectUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  const sizeMB = (file.size / 1024 / 1024).toFixed(2);
  const Icon = mediaType === "image" ? FileImage : FileVideo;

  return (
    <div className="space-y-3 rounded-xl border bg-card p-4 shadow-sm">
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <Icon className="size-4 shrink-0 text-muted-foreground" />
          <div className="min-w-0">
            <p className="truncate text-sm font-medium">{file.name}</p>
            <p className="text-xs text-muted-foreground">
              {sizeMB} MB - {file.type || mediaType}
            </p>
          </div>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={onClear}
          disabled={disabled}
          aria-label="Remover arquivo"
        >
          <X className="size-4" />
        </Button>
      </div>

      <div className="overflow-hidden rounded-lg border bg-muted/30">
        {mediaType === "image" ? (
          <img
            src={objectUrl}
            alt="Preview da placa"
            className="mx-auto block max-h-[420px] w-auto object-contain"
          />
        ) : (
          <video
            src={objectUrl}
            controls
            className="mx-auto block max-h-[420px] w-full"
          />
        )}
      </div>
    </div>
  );
}

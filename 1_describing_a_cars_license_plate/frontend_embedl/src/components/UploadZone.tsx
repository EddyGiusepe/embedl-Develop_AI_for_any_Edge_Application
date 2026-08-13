/**
 * Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro
 *
 * UploadZone.tsx
 * ===============
 * Drag-and-drop upload area for selecting an image or video file.
 * Validates file type and size before passing it to the analysis flow.
 *
 */
import { useCallback, useRef, useState } from "react";
import { ImagePlus, VideoIcon } from "lucide-react";

import { cn } from "@/lib/utils";
import type { MediaType } from "@/lib/types";

interface UploadZoneProps {
  mediaType: MediaType;
  onFileSelected: (file: File) => void;
  disabled?: boolean;
}

const IMAGE_EXTS = [".jpg", ".jpeg", ".png", ".webp", ".bmp"];
const VIDEO_EXTS = [".mp4", ".avi", ".mov", ".webm", ".mkv"];
const MAX_MB = 100;

function isAcceptedFile(file: File, mediaType: MediaType): string | null {
  const exts = mediaType === "image" ? IMAGE_EXTS : VIDEO_EXTS;
  const lower = file.name.toLowerCase();
  const match = exts.some((ext) => lower.endsWith(ext));
  if (!match) {
    return `Unsupported file extension. Use: ${exts.join(", ")}`;
  }
  const sizeMB = file.size / 1024 / 1024;
  if (sizeMB > MAX_MB) {
    return `File too large (${sizeMB.toFixed(1)} MB). Maximum ${MAX_MB} MB.`;
  }
  return null;
}

export function UploadZone({
  mediaType,
  onFileSelected,
  disabled = false,
}: UploadZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFile = useCallback(
    (file: File | null | undefined) => {
      if (!file) return;
      const err = isAcceptedFile(file, mediaType);
      if (err) {
        setError(err);
        return;
      }
      setError(null);
      onFileSelected(file);
    },
    [mediaType, onFileSelected]
  );

  const onChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFile(e.target.files?.[0]);
    e.target.value = "";
  };

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const onDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFile(e.dataTransfer.files?.[0]);
  };

  const accept =
    mediaType === "image" ? IMAGE_EXTS.join(",") : VIDEO_EXTS.join(",");
  const Icon = mediaType === "image" ? ImagePlus : VideoIcon;
  const label =
    mediaType === "image" ? "image containing a license plate" : "video containing a license plate";
  const allowed =
    mediaType === "image" ? IMAGE_EXTS.join(", ") : VIDEO_EXTS.join(", ");

  return (
    <div className="space-y-2">
      <button
        type="button"
        disabled={disabled}
        onClick={() => inputRef.current?.click()}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        className={cn(
          "group flex w-full flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed border-input bg-card/50 px-6 py-12 text-center transition-colors",
          "hover:border-primary/60 hover:bg-accent/40",
          "disabled:cursor-not-allowed disabled:opacity-50",
          isDragging && "border-primary bg-accent/60"
        )}
      >
        <div className="rounded-full bg-primary/10 p-4 transition group-hover:bg-primary/20">
          <Icon className="size-8 text-primary" />
        </div>
        <div>
          <p className="text-base font-medium">
            Drag and drop {label} here or{" "}
            <span className="text-primary underline underline-offset-2">
              click to select
            </span>
          </p>
          <p className="mt-1 text-xs text-muted-foreground">
            Formats: {allowed} - Maximum {MAX_MB} MB
          </p>
        </div>
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          className="hidden"
          onChange={onChange}
          disabled={disabled}
        />
      </button>
      {error && (
        <p className="text-sm text-destructive" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}

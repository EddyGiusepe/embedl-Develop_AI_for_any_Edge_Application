/**
 * Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro
 *
 * PlateReport.tsx
 * ===============
 * Renders the VLM license plate analysis report as structured UI blocks.
 *
 * Uses parsePlateReport() to extract one or more plates from the API
 * description. Falls back to the raw model output when parsing fails.
 */
import {
  AlertTriangle,
  CarFront,
  CheckCircle2,
  CircleAlert,
  Flag,
  Hash,
  MapPin,
  Palette,
  ScanLine,
  Video,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import {
  parsePlateReport,
  type Confidence,
  type PlateInfo,
} from "@/lib/parsePlateReport";

interface PlateReportProps {
  description: string;
}

/** Confidence badge styles by level. */
const CONFIDENCE_STYLES: Record<
  Confidence,
  { className: string; Icon: LucideIcon; label: string }
> = {
  High: {
    className:
      "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 border-emerald-500/30",
    Icon: CheckCircle2,
    label: "High",
  },
  Medium: {
    className:
      "bg-amber-500/15 text-amber-700 dark:text-amber-300 border-amber-500/30",
    Icon: CircleAlert,
    label: "Medium",
  },
  Low: {
    className:
      "bg-rose-500/15 text-rose-700 dark:text-rose-300 border-rose-500/30",
    Icon: AlertTriangle,
    label: "Low",
  },
};

/** Normalizes confidence to one of the 3 known levels. */
function normalizeConfidence(value?: string): Confidence | undefined {
  if (!value) return undefined;
  const v = value.trim().toLowerCase();
  if (v.startsWith("high") || v.startsWith("alt")) return "High";
  if (v.startsWith("med")) return "Medium";
  if (v.startsWith("low") || v.startsWith("baix")) return "Low";
  return undefined;
}

function ConfidenceBadge({ value }: { value?: string }) {
  const level = normalizeConfidence(value);
  if (!level) {
    return value ? (
      <Badge variant="outline">{value}</Badge>
    ) : null;
  }
  const { className, Icon, label } = CONFIDENCE_STYLES[level];
  return (
    <Badge variant="outline" className={`gap-1 ${className}`}>
      <Icon className="size-3" />
      {label}
    </Badge>
  );
}

interface FieldProps {
  icon: LucideIcon;
  label: string;
  value?: string;
}

function Field({ icon: Icon, label, value }: FieldProps) {
  const isMissing =
    !value || /^(not\s+(visible|identified|provided)|unreadable)/i.test(value);
  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center gap-1.5 text-xs font-medium uppercase tracking-wide text-muted-foreground">
        <Icon className="size-3.5" />
        {label}
      </div>
      <div
        className={`text-sm ${
          isMissing ? "italic text-muted-foreground" : "text-foreground"
        }`}
      >
        {value || "Not provided"}
      </div>
    </div>
  );
}

function NoPlateBlock({ plate }: { plate: PlateInfo }) {
  return (
    <div className="space-y-4 rounded-lg border bg-muted/30 p-4">
      <div className="flex flex-wrap items-start justify-between gap-3 border-b pb-3">
        <div className="flex items-center gap-2">
          <AlertTriangle className="size-5 text-amber-500" />
          <div className="font-semibold text-foreground">
            {plate.analysisStatus ?? "No license plate detected"}
          </div>
        </div>
        <ConfidenceBadge value={plate.confidence} />
      </div>

      <Field
        icon={CircleAlert}
        label="Reason"
        value={
          plate.reason ??
          "No vehicle or real vehicle license plate is visible in the media."
        }
      />
    </div>
  );
}

function PlateBlock({ plate, total }: { plate: PlateInfo; total: number }) {
  if (plate.analysisStatus) {
    return <NoPlateBlock plate={plate} />;
  }

  return (
    <div className="space-y-4 rounded-lg border bg-muted/30 p-4">
      {/* Block header: prominent plate number + confidence. */}
      <div className="flex flex-wrap items-start justify-between gap-3 border-b pb-3">
        <div className="space-y-1">
          {total > 1 && plate.index && (
            <div className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
              Plate #{plate.index}
            </div>
          )}
          <div className="font-mono text-2xl font-bold tracking-wider text-foreground">
            {plate.plateText ?? "Unreadable"}
          </div>
        </div>
        <ConfidenceBadge value={plate.confidence} />
      </div>

      {/* Metadata grid (2 columns on larger screens, 1 on mobile). */}
      <div className="grid gap-4 sm:grid-cols-2">
        <Field icon={Flag} label="Country" value={plate.country} />
        <Field icon={MapPin} label="State/City" value={plate.region} />
        <Field icon={ScanLine} label="Format" value={plate.format} />
        <Field icon={CarFront} label="Vehicle" value={plate.vehicle} />
      </div>

      {/* Longer descriptive fields span the full width. */}
      {plate.visualFeatures && (
        <Field
          icon={Palette}
          label="Visual characteristics"
          value={plate.visualFeatures}
        />
      )}

      {plate.videoContext && (
        <Field
          icon={Video}
          label="Video context"
          value={plate.videoContext}
        />
      )}
    </div>
  );
}

export function PlateReport({ description }: PlateReportProps) {
  const parsed = parsePlateReport(description);

  // Fallback: the parser could not extract anything. Show the raw model output
  // so no information returned by the model is lost.
  if (parsed.isFallback) {
    return (
      <div className="space-y-2 rounded-lg border bg-muted/30 p-4">
        <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground">
          <Hash className="size-3.5" />
          Model response (unrecognized format)
        </div>
        <pre className="whitespace-pre-wrap break-words font-sans text-sm leading-relaxed text-foreground">
          {parsed.raw}
        </pre>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {parsed.plates.map((plate, idx) => (
        <PlateBlock
          key={plate.index ?? idx}
          plate={plate}
          total={parsed.plates.length}
        />
      ))}
    </div>
  );
}

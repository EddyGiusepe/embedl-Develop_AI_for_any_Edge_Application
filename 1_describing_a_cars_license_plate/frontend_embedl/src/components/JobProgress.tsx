/**
 * Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro
 *
 * JobProgress.tsx
 * ===============
 * Shows the current analysis job status, progress bar, and job identifier.
 *
 */
import { Loader2 } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import type { JobStatusValue } from "@/lib/types";

interface JobProgressProps {
  status: JobStatusValue;
  jobId: string;
}

const STATUS_LABEL: Record<JobStatusValue, string> = {
  queued: "In Queue",
  processing: "Processing",
  completed: "Completed",
  failed: "Failed",
};

const STATUS_VALUE: Record<JobStatusValue, number> = {
  queued: 20,
  processing: 65,
  completed: 100,
  failed: 100,
};

function variantOf(status: JobStatusValue) {
  if (status === "completed") return "default" as const;
  if (status === "failed") return "destructive" as const;
  return "secondary" as const;
}

export function JobProgress({ status, jobId }: JobProgressProps) {
  const isActive = status === "queued" || status === "processing";

  return (
    <div className="space-y-3 rounded-xl border bg-card p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {isActive && (
            <Loader2 className="size-4 animate-spin text-primary" />
          )}
          <span className="text-sm font-medium">
            Status: {STATUS_LABEL[status]}
          </span>
        </div>
        <Badge variant={variantOf(status)}>{status}</Badge>
      </div>
      <Progress value={STATUS_VALUE[status]} />
      <p className="text-xs text-muted-foreground">
        Job ID: <code className="font-mono">{jobId}</code>
      </p>
    </div>
  );
}

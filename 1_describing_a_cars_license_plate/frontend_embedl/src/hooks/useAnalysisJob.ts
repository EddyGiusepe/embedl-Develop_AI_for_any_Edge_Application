/**
 * Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro
 *
 * useAnalysisJob.ts
 * =================
 * Manages the license plate analysis job lifecycle:
 * - uploads the selected file
 * - polls the job status until completion or failure
 * - exposes UI state flags and triggers user feedback toasts
 */
import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { getJobStatus, uploadFile } from "@/lib/api";
import type { JobCreatedResponse, JobStatusResponse } from "@/lib/types";

const POLL_INTERVAL_MS = 2000; // 2 seconds

export function useAnalysisJob() {
  const [jobId, setJobId] = useState<string | null>(null);

  const uploadMutation = useMutation({
    mutationFn: (file: File) => uploadFile(file),
    onSuccess: (data: JobCreatedResponse) => {
      setJobId(data.job_id);
      toast.info("Upload successful", {
        description: `Analysis started for ${data.filename}`,
      });
    },
    onError: (error: Error) => {
      toast.error("Upload failed", {
        description: error.message,
      });
    },
  });

  const statusQuery = useQuery({
    queryKey: ["job", jobId],
    queryFn: () => getJobStatus(jobId as string),
    enabled: jobId !== null,
    refetchInterval: (query) => {
      const data = query.state.data as JobStatusResponse | undefined;
      if (!data) return POLL_INTERVAL_MS;
      if (data.status === "completed" || data.status === "failed") {
        return false;
      }
      return POLL_INTERVAL_MS;
    },
    refetchIntervalInBackground: true,
  });

  useEffect(() => {
    const data = statusQuery.data;
    if (!data) return;
    if (data.status === "completed") {
      toast.success("Analysis completed!", {
        description: `Processing time: ${data.result?.processing_time_seconds ?? 0}s`,
      });
    } else if (data.status === "failed") {
      toast.error("Analysis failed", {
        description: data.error ?? "Unknown error",
      });
    }
  }, [statusQuery.data]);

  function reset() {
    setJobId(null);
    uploadMutation.reset();
  }

  function analyze(file: File) {
    reset();
    uploadMutation.mutate(file);
  }

  const job = statusQuery.data ?? null;
  const isUploading = uploadMutation.isPending;
  const isProcessing =
    job !== null && (job.status === "queued" || job.status === "processing");
  const isComplete = job?.status === "completed";
  const isFailed = job?.status === "failed";

  return {
    analyze,
    reset,
    job,
    jobId,
    isUploading,
    isProcessing,
    isComplete,
    isFailed,
    uploadError: uploadMutation.error,
  };
}

/**
 * Tipos espelhando os schemas Pydantic do backend FastAPI.
 * Mantenha em sincronia com app/schemas/analysis.py
 */

export type MediaType = "image" | "video";

export type JobStatusValue = "queued" | "processing" | "completed" | "failed";

export interface AnalysisResult {
  description: string;
  media_type: MediaType;
  filename: string;
  processing_time_seconds: number;
}

export interface JobCreatedResponse {
  job_id: string;
  status: JobStatusValue;
  media_type: MediaType;
  filename: string;
  created_at: string;
  poll_url: string;
}

export interface JobStatusResponse {
  job_id: string;
  status: JobStatusValue;
  created_at: string;
  updated_at: string;
  result: AnalysisResult | null;
  error: string | null;
}

export interface HealthResponse {
  status: string;
  app_name: string;
  app_version: string;
  model_name: string;
  model_loaded: boolean;
  device: string;
  cuda_available: boolean;
  active_jobs: number;
}

export interface ApiError {
  detail: string;
}

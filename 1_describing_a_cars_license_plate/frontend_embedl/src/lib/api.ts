/**
 * Cliente HTTP para a API do backend_embedl.
 */
import type {
  ApiError,
  HealthResponse,
  JobCreatedResponse,
  JobStatusResponse,
} from "./types";

const API_URL = import.meta.env.VITE_API_URL ?? "";
const API_V1 = `${API_URL}/api/v1`;

class HttpError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`;
    try {
      const body = (await res.json()) as ApiError;
      if (body.detail) detail = body.detail;
    } catch {
      // Ignora se nao for JSON
    }
    throw new HttpError(res.status, detail);
  }
  if (res.status === 204) {
    return undefined as T;
  }
  return (await res.json()) as T;
}

export async function getHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_URL}/health`);
  return handleResponse<HealthResponse>(res);
}

export async function uploadFile(file: File): Promise<JobCreatedResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_V1}/jobs`, {
    method: "POST",
    body: formData,
  });
  return handleResponse<JobCreatedResponse>(res);
}

export async function getJobStatus(
  jobId: string
): Promise<JobStatusResponse> {
  const res = await fetch(`${API_V1}/jobs/${jobId}`);
  return handleResponse<JobStatusResponse>(res);
}

export async function deleteJob(jobId: string): Promise<void> {
  const res = await fetch(`${API_V1}/jobs/${jobId}`, {
    method: "DELETE",
  });
  return handleResponse<void>(res);
}

export { HttpError };

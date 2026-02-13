/**
 * Cron Jobs API Client
 * Handles communication with the cron jobs management backend
 */

import { getAuthHeaders } from '../auth-headers';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
const API_V1_URL = `${API_BASE_URL}/api/v1`;

// ── Types ────────────────────────────────────────────────────────────

export interface CronJob {
  id: string;
  job_id: string;
  competitor: string;
  aspects: string[];
  frequency_hours: number;
  notification_preference?: string;
  status: 'running' | 'paused' | 'failed';
  created_at?: string;
  next_run?: string;
  last_execution?: string;
  error_count: number;
  last_error?: string;
}

export interface MonitoringResult {
  id: string;
  config_id: string;
  competitor: string;
  aspects: string[];
  execution_time: string;
  is_significant: boolean;
  significance_score: number;
  summary: string;
  notification_sent: boolean;
}

export interface CronStats {
  total: number;
  active: number;
  paused: number;
  failed: number;
  with_errors: number;
}

export interface CronJobUpdate {
  frequency_hours?: number;
  aspects?: string[];
  notification_preference?: string;
}

export interface BulkDeleteResult {
  status: string;
  deleted: number;
  requested: number;
  errors: string[];
}

// ── API Functions ────────────────────────────────────────────────────

/**
 * List all cron jobs for the current user
 */
export async function listCronJobs(): Promise<CronJob[]> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_V1_URL}/crons/`, {
    method: 'GET',
    headers,
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to list cron jobs: ${error}`);
  }

  return response.json();
}

/**
 * Pause a cron job
 */
export async function pauseCronJob(jobId: string): Promise<{ status: string; job_id: string }> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_V1_URL}/crons/${jobId}/pause`, {
    method: 'POST',
    headers,
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to pause job: ${error}`);
  }

  return response.json();
}

/**
 * Resume a paused cron job
 */
export async function resumeCronJob(jobId: string): Promise<{ status: string; job_id: string }> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_V1_URL}/crons/${jobId}/resume`, {
    method: 'POST',
    headers,
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to resume job: ${error}`);
  }

  return response.json();
}

/**
 * Delete a cron job permanently
 */
export async function deleteCronJob(jobId: string): Promise<{ status: string; job_id: string }> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_V1_URL}/crons/${jobId}`, {
    method: 'DELETE',
    headers,
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to delete job: ${error}`);
  }

  return response.json();
}

/**
 * Update a cron job configuration
 */
export async function updateCronJob(jobId: string, update: CronJobUpdate): Promise<{ status: string; job_id: string }> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_V1_URL}/crons/${jobId}`, {
    method: 'PUT',
    headers,
    body: JSON.stringify(update),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to update job: ${error}`);
  }

  return response.json();
}

/**
 * Bulk delete cron jobs
 */
export async function bulkDeleteCronJobs(jobIds: string[]): Promise<BulkDeleteResult> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_V1_URL}/crons/bulk-delete`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ job_ids: jobIds }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to bulk delete jobs: ${error}`);
  }

  return response.json();
}

/**
 * Get execution results for a monitoring job
 */
export async function getCronJobResults(configId: string, limit: number = 50): Promise<MonitoringResult[]> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_V1_URL}/crons/${configId}/results?limit=${limit}`, {
    method: 'GET',
    headers,
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to get job results: ${error}`);
  }

  return response.json();
}

/**
 * Get summary statistics for cron jobs
 */
export async function getCronStats(): Promise<CronStats> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_V1_URL}/crons/stats/summary`, {
    method: 'GET',
    headers,
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to get cron stats: ${error}`);
  }

  return response.json();
}

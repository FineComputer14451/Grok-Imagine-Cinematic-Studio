/**
 * Client for the GICS Snapshot API (FastAPI).
 * Same-origin paths so Vite proxies to :8787 in dev / preview.
 */

export type ApiSource = "live" | "mock" | "offline";

export interface SnapshotResponse {
  source: "live" | "mock";
  studio_version: string;
  severity: "ok" | "warn" | "critical";
  attention: string[];
  snapshot: Record<string, unknown>;
}

export interface CliActionResponse {
  source: "live" | "mock";
  action: string;
  exit_code: number;
  output: string;
  ok: boolean;
}

export interface DnaProfileDto {
  id?: string | null;
  name: string;
  slug?: string | null;
  status?: string;
  locked?: boolean;
  drift_score?: number | null;
  traits?: string[];
  looks?: string | null;
  project?: string | null;
}

export interface SequenceDto {
  id?: string | null;
  name: string;
  slug?: string | null;
  clips?: number;
  target_duration?: number | null;
  health?: string | null;
  chain_qa_status?: string | null;
}

export interface QuotaEstimateResponse {
  source: "live" | "mock";
  dashboard: Record<string, unknown>;
  estimate?: Record<string, unknown> | null;
  risk?: Record<string, unknown> | null;
  alignment?: Record<string, unknown> | null;
}

const API_BASE = ""; // same origin — Vite proxies /api and /health

async function apiFetch<T>(
  path: string,
  init?: RequestInit,
): Promise<{ ok: true; data: T } | { ok: false; error: string }> {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: {
        Accept: "application/json",
        ...(init?.body ? { "Content-Type": "application/json" } : {}),
        ...(init?.headers ?? {}),
      },
    });
    if (!res.ok) {
      const text = await res.text().catch(() => "");
      return { ok: false, error: text || `HTTP ${res.status}` };
    }
    return { ok: true, data: (await res.json()) as T };
  } catch (err) {
    return {
      ok: false,
      error: err instanceof Error ? err.message : "Network error",
    };
  }
}

export async function fetchHealth(): Promise<{
  status: string;
  tools_available: boolean;
  studio_version: string;
} | null> {
  const r = await apiFetch<{
    status: string;
    tools_available: boolean;
    studio_version: string;
  }>("/health");
  return r.ok ? r.data : null;
}

export async function fetchSnapshot(): Promise<SnapshotResponse | null> {
  const r = await apiFetch<SnapshotResponse>("/api/v1/dashboard/snapshot");
  return r.ok ? r.data : null;
}

export async function runCliAction(
  action: string,
): Promise<CliActionResponse | null> {
  // map UI keys → API path segments
  const map: Record<string, string> = {
    doctor: "doctor",
    validate: "validate",
    "quota-sync": "quota-sync",
    models: "models-verify",
    "models-verify": "models-verify",
  };
  const slug = map[action] ?? action;
  const r = await apiFetch<CliActionResponse>(`/api/v1/cli/${slug}`, {
    method: "POST",
    body: JSON.stringify({ timeout_sec: 120 }),
  });
  return r.ok ? r.data : null;
}

export async function fetchDna(): Promise<DnaProfileDto[] | null> {
  const r = await apiFetch<{ characters: DnaProfileDto[] }>("/api/v1/dna");
  return r.ok ? r.data.characters : null;
}

export async function lockDna(
  name: string,
): Promise<{ character: DnaProfileDto; message: string } | null> {
  const r = await apiFetch<{ character: DnaProfileDto; message: string }>(
    "/api/v1/dna/lock",
    {
      method: "POST",
      body: JSON.stringify({ name }),
    },
  );
  return r.ok ? r.data : null;
}

export async function fetchSequences(): Promise<SequenceDto[] | null> {
  const r = await apiFetch<{ sequences: SequenceDto[] }>("/api/v1/sequences");
  return r.ok ? r.data.sequences : null;
}

export async function estimateQuota(body: {
  duration_sec: number;
  complexity?: string;
  fast_mode?: boolean;
}): Promise<QuotaEstimateResponse | null> {
  const r = await apiFetch<QuotaEstimateResponse>("/api/v1/quota/estimate", {
    method: "POST",
    body: JSON.stringify(body),
  });
  return r.ok ? r.data : null;
}

export async function verifyModels(): Promise<Record<string, unknown> | null> {
  const r = await apiFetch<Record<string, unknown>>("/api/v1/models/verify");
  return r.ok ? r.data : null;
}

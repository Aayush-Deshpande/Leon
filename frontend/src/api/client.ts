/**
 * Backend API client. Endpoints and shapes are owned by [220]; implemented in P8.
 * Base URL is configurable via Vite env (VITE_API_BASE_URL); defaults to local backend.
 */
export const API_BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

import type { QueryResponse } from "../types";

export async function getHealth(): Promise<{ status: string; version: string }> {
  const res = await fetch(`${API_BASE_URL}/health`);
  if (!res.ok) throw new Error(`health check failed: ${res.status}`);
  return (await res.json()) as { status: string; version: string };
}

export async function query(question: string): Promise<QueryResponse> {
  const res = await fetch(`${API_BASE_URL}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: question }),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`query failed: ${res.status} ${detail}`);
  }
  return (await res.json()) as QueryResponse;
}

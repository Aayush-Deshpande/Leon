// API types mirroring the [220] POST /query contract.

export interface Citation {
  id: string;
  chunk_id: string;
  source_document: string;
  locator: string;
  passage: string;
}

export interface Routing {
  outcome: "returned" | "reformulated" | "tool_verified" | "low_confidence";
  reformulations: number;
}

export interface QueryResponse {
  answer: string;
  citations: Citation[];
  confidence: "high" | "low";
  routing: Routing;
  reason: string | null;
}

import { useState } from "react";
import { query } from "../api/client";
import type { QueryResponse } from "../types";
import { CitationList } from "./CitationList";
import { ConfidenceIndicator } from "./ConfidenceIndicator";

/** Single-turn chat (FR-1, FR-21, FR-23, FR-15). Sends a query and renders the grounded, cited answer. */
export function ChatView(): JSX.Element {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent): Promise<void> {
    e.preventDefault();
    if (!question.trim()) return;
    setLoading(true);
    setError(null);
    try {
      setResponse(await query(question.trim()));
    } catch (err) {
      setError(err instanceof Error ? err.message : "unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <form onSubmit={onSubmit}>
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a legal question…"
          rows={3}
          maxLength={2000}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Checking…" : "Ask"}
        </button>
      </form>

      {error && <p role="alert">Error: {error}</p>}

      {response && (
        <article>
          <ConfidenceIndicator confidence={response.confidence} />
          <p>{response.answer}</p>
          {response.confidence === "low" && response.reason && (
            <p>
              <em>Reason: {response.reason}</em>
            </p>
          )}
          <CitationList citations={response.citations} />
        </article>
      )}
    </div>
  );
}

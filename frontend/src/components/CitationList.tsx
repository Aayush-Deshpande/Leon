import type { Citation } from "../types";

/** Citation display (FR-6, FR-23): each citation reveals its underlying source passage. */
export function CitationList({ citations }: { citations: Citation[] }): JSX.Element | null {
  if (citations.length === 0) return null;
  return (
    <section aria-label="Citations">
      <h3>Citations</h3>
      <ul>
        {citations.map((c) => (
          <li key={c.id}>
            <details>
              <summary>
                {c.locator} — {c.source_document}
              </summary>
              <blockquote>{c.passage}</blockquote>
            </details>
          </li>
        ))}
      </ul>
    </section>
  );
}

/** Confidence indicator (FR-21). Surfaces the [210]-derived high/low confidence. */
export function ConfidenceIndicator({ confidence }: { confidence: "high" | "low" }): JSX.Element {
  const label = confidence === "high" ? "High confidence" : "Low confidence";
  const color = confidence === "high" ? "#137333" : "#b3261e";
  return (
    <span aria-label={label} style={{ color, fontWeight: 600 }}>
      ● {label}
    </span>
  );
}

import { ChatView } from "./components/ChatView";

/** Application shell. Renders the single-turn legal Q&A chat (P8). */
export function App(): JSX.Element {
  return (
    <main style={{ maxWidth: 760, margin: "2rem auto", fontFamily: "system-ui, sans-serif" }}>
      <h1>Leon</h1>
      <p>Self-evaluating legal RAG. Answers are grounded in cited sources or flagged low-confidence.</p>
      <ChatView />
    </main>
  );
}

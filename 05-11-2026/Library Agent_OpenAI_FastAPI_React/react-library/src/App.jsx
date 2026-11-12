import { useState } from "react";
import "./App.css";

export default function App() {
  const [sessionId] = useState(() => crypto.randomUUID());
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);

  async function sendMessage(event) {
    event.preventDefault();
    const message = text.trim();
    if (!message || loading) return;

    setMessages((current) => [...current, { role: "user", content: message }]);
    setText("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, message }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? "Chat request failed.");

      setMessages((current) => [
        ...current,
        { role: "assistant", content: data.reply },
      ]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        { role: "assistant", content: `Error: ${error.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="chat">
      <header className="chat-header">Library Assistant</header>

      <section className="messages" aria-live="polite">
        {messages.length === 0 && (
          <p className="welcome">How can I help you today?</p>
        )}
        {messages.map((message, index) => (
          <div className={`message ${message.role}`} key={index}>
            {message.content}
          </div>
        ))}
        {loading && <div className="message assistant">Thinking…</div>}
      </section>

      <form className="composer" onSubmit={sendMessage}>
        <textarea
          value={text}
          onChange={(event) => setText(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              event.currentTarget.form.requestSubmit();
            }
          }}
          placeholder="Tell me here"
          aria-label="Message"
        />
        <button disabled={loading || !text.trim()} type="submit">
          Send
        </button>
      </form>
    </main>
  );
}
import { useEffect, useMemo, useRef, useState } from "react";
import { AlertTriangle, ArrowUp, Bot, LoaderCircle, Sparkles } from "lucide-react";
import Header from "./components/Header";
import ExamplePrompts from "./components/ExamplePrompts";
import Message from "./components/Message";
import ToolPanel from "./components/ToolPanel";
import { api } from "./services/api";

export default function App() {
  const [health, setHealth] = useState("unknown");
  const [mcp, setMcp] = useState(false);
  const [tools, setTools] = useState([]);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef(null);

  const connected = health === "configured" && mcp;

  const welcome = useMemo(() => messages.length === 0, [messages.length]);

  useEffect(() => {
    Promise.all([api.health(), api.mcpStatus(), api.mcpTools()])
      .then(([h, s, t]) => {
        setHealth(h.gemini);
        setMcp(s.connected);
        setTools(t.tools || []);
      })
      .catch((err) => setError(err.message));
  }, []);

  async function send(message = input) {
    const text = message.trim();
    if (!text || loading) return;

    setError("");
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setLoading(true);

    try {
      const data = await api.chat(text);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.response,
          pipeline: {
            ...data.pipeline,
            request: text,
            response: data.response,
          },
        },
      ]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      send();
    }
  }

  return (
    <div className="app-shell">
      <Header health={health} mcp={mcp} />

      <main className="layout">
        <section className="chat-card">
          {welcome ? (
            <div className="welcome">
              <div className="welcome-icon"><Sparkles size={24} /></div>
              <span className="eyebrow">AI + MCP</span>
              <h2>Ask me to calculate anything.</h2>
              <p>Gemini understands your request. MCP performs the actual arithmetic.</p>
              <ExamplePrompts onSelect={send} />
            </div>
          ) : (
            <div className="messages">
              {messages.map((message, index) => (
                <Message key={index} message={message} />
              ))}
              {loading && (
                <div className="thinking">
                  <LoaderCircle size={17} className="spin" />
                  <span>Agent is thinking…</span>
                </div>
              )}
            </div>
          )}

          {error && (
            <div className="error-card">
              <AlertTriangle size={18} />
              <div>
                <strong>Request failed</strong>
                <p>{error}</p>
              </div>
            </div>
          )}

          <div className="composer">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value.slice(0, 500))}
              onKeyDown={handleKeyDown}
              placeholder="Ask me anything…"
              aria-label="Calculator request"
              disabled={loading}
              rows={1}
            />
            <button
              className="send"
              onClick={() => send()}
              disabled={!input.trim() || loading || !connected}
              aria-label="Send message"
            >
              {loading ? <LoaderCircle className="spin" size={18} /> : <ArrowUp size={18} />}
            </button>
          </div>
          <div className="composer-meta">
            <span>Enter to send · Shift + Enter for a new line</span>
            <span>{input.length}/500</span>
          </div>
        </section>

        <ToolPanel tools={tools} />
      </main>

      <footer>
        <Bot size={14} /> Agentic Calculator · Gemini reasoning · Real MCP tool execution
      </footer>
    </div>
  );
}

import { Calculator, Circle } from "lucide-react";

export default function Header({ health, mcp }) {
  return (
    <header className="topbar">
      <div className="brand">
        <div className="brand-icon"><Calculator size={21} /></div>
        <div>
          <h1>Agentic Calculator</h1>
          <p>Natural language calculations powered by Gemini + MCP</p>
        </div>
      </div>
      <div className="status-row">
        <span className={`status ${health === "configured" ? "ok" : "warn"}`}>
          <Circle size={9} fill="currentColor" /> Gemini {health === "configured" ? "Connected" : "Not configured"}
        </span>
        <span className={`status ${mcp ? "ok" : "warn"}`}>
          <Circle size={9} fill="currentColor" /> MCP {mcp ? "Connected" : "Disconnected"}
        </span>
      </div>
    </header>
  );
}

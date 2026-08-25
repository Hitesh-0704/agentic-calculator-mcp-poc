import { ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";

export default function Pipeline({ pipeline }) {
  const [open, setOpen] = useState(false);

  if (pipeline.intent === "unsupported") return null;

  const items = [
    ["USER REQUEST", pipeline.request],
    ["AI UNDERSTANDING", pipeline.intent],
    ["OPERATION", pipeline.operation],
    ["OPERANDS", pipeline.operands?.join(", ")],
    ["MCP TOOL", pipeline.mcp_tool],
    ["MCP EXECUTION", `${pipeline.mcp_tool ?? "—"}(${pipeline.operands?.join(", ") ?? ""})`],
    ["RESULT", pipeline.result],
    ["AGENT RESPONSE", pipeline.response],
  ];

  return (
    <div className="pipeline">
      <button className="pipeline-toggle" onClick={() => setOpen(!open)}>
        <span>Request Processing</span>
        {open ? <ChevronUp size={17} /> : <ChevronDown size={17} />}
      </button>
      {open && (
        <div className="pipeline-body">
          {items.map(([label, value], index) => (
            <div className="pipeline-step" key={label}>
              <div>
                <span className="step-label">{label}</span>
                <strong>{String(value ?? "—")}</strong>
              </div>
              {index < items.length - 1 && <span className="connector">↓</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

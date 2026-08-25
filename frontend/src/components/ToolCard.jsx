import { Calculator, Divide, Minus, Plus, X } from "lucide-react";

const icons = { add: Plus, subtract: Minus, multiply: X, divide: Divide };

export default function ToolCard({ tool }) {
  const Icon = icons[tool.name] || Calculator;
  return (
    <div className="tool-card">
      <div className="tool-icon"><Icon size={18} /></div>
      <div>
        <strong>{tool.name}</strong>
        <p>{tool.description}</p>
      </div>
    </div>
  );
}

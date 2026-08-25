import ToolCard from "./ToolCard";

export default function ToolPanel({ tools }) {
  return (
    <aside className="tools-panel">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">MCP SERVER</span>
          <h2>Available MCP Tools</h2>
        </div>
        <span className="count">{tools.length}</span>
      </div>
      <p className="panel-copy">These tools are discovered dynamically from the MCP server.</p>
      <div className="tool-list">
        {tools.map((tool) => <ToolCard key={tool.name} tool={tool} />)}
      </div>
    </aside>
  );
}

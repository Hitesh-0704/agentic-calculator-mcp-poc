import { Bot, User } from "lucide-react";
import Pipeline from "./Pipeline";

export default function Message({ message }) {
  const isUser = message.role === "user";

  return (
    <article className={`message-row ${isUser ? "user" : "assistant"}`}>
      <div className="avatar">{isUser ? <User size={16} /> : <Bot size={17} />}</div>
      <div className="message-content">
        <span className="message-label">{isUser ? "You" : "Agent"}</span>
        <div className="bubble">{message.content}</div>
        {!isUser && message.pipeline && <Pipeline pipeline={message.pipeline} />}
      </div>
    </article>
  );
}

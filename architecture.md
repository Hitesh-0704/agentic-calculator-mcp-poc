# Architecture

## Component diagram

```mermaid
flowchart LR
    U[User] --> UI[React / Vite]
    UI --> API[FastAPI]
    API --> A[Gemini Agent]
    A --> C[MCP Client]
    C -->|STDIO JSON-RPC| S[MCP Calculator Server]
    S --> T[Calculator Tools]
    T --> S
    S --> C
    C --> A
    A --> API
    API --> UI
```

## Request lifecycle

```mermaid
sequenceDiagram
    participant U as User
    participant UI as React UI
    participant API as FastAPI
    participant G as Gemini
    participant C as MCP Client
    participant S as MCP Server
    participant T as Calculator Tool

    U->>UI: Natural-language request
    UI->>API: POST /api/chat
    API->>G: Prompt + discovered MCP tool declarations
    G-->>API: Tool call: multiply(a=25,b=8)
    API->>C: call_tool("multiply", args)
    C->>S: MCP call_tool
    S->>T: Execute multiply
    T-->>S: Structured result
    S-->>C: MCP result
    C-->>API: Result
    API->>G: Tool result
    G-->>API: Final response
    API-->>UI: Response + real pipeline data
```

## Security boundaries

- Browser never receives `GEMINI_API_KEY`.
- Browser cannot choose an arbitrary MCP executable.
- Backend only invokes MCP tools that were discovered and are in the calculator allow-list.
- MCP server performs arithmetic independently of Gemini.
- User input is never executed as Python or shell code.

## Failure flow

```text
Gemini unavailable
      |
      v
Fallback intent parser
      |
      v
MCP tool invocation
      |
      +--> success -> final response
      |
      +--> failure -> controlled MCP error
```

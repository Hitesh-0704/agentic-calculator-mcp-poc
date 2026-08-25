> Compatibility: this project is pinned to MCP Python SDK 2.1.0 and uses the v2 `MCPServer`/`Client` APIs.

# Agentic Calculator

AI-powered natural-language calculator using **Google Gemini + MCP + FastAPI + React/Vite**.

## Verified stack

| Component | Choice |
|---|---|
| Python | 3.11+ |
| Gemini SDK | `google-genai` |
| Gemini model | `gemini-2.5-flash` (Google Gemini API Free Tier) |
| MCP SDK | Official `mcp` Python SDK v2 line |
| MCP transport | STDIO |
| Backend | FastAPI + Uvicorn |
| Frontend | React + Vite |
| Validation | Pydantic v2 |
| Tests | Pytest + HTTPX |

The implementation intentionally keeps the calculator arithmetic inside the MCP server. Gemini only understands the natural-language request and selects a dynamically discovered MCP tool.

## Architecture

```text
React/Vite
   |
   | POST /api/chat
   v
FastAPI
   |
   v
Gemini Agent
   |
   | function/tool selection
   v
MCP Client
   |
   | real MCP STDIO
   v
MCP Server
   |
   +--> add
   +--> subtract
   +--> multiply
   +--> divide
   |
   v
result
   |
   v
MCP Client -> Gemini -> FastAPI -> React
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- npm
- A Gemini API key from Google AI Studio

## Setup

### 1. Backend

Windows PowerShell:

```powershell
cd agentic-calculator\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and add:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
```

### 2. Start backend

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The FastAPI process automatically starts the MCP calculator server as a child process over STDIO.

You do **not** need a second terminal for the MCP server.

### 3. Frontend

Open another terminal:

```powershell
cd agentic-calculator\frontend
npm install
npm run dev
```

Open the URL Vite prints, normally:

```text
http://localhost:5173
```

## Useful endpoints

```text
GET  /api/health
GET  /api/mcp/status
GET  /api/mcp/tools
POST /api/chat
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## Test

From `backend`:

```powershell
pytest -q
```

The tests cover calculator logic, fallback intent parsing, API validation, and MCP discovery/invocation using the official SDK's in-memory client.

## Demo

Try:

```text
Multiply 25 by 8
Add 3 and 4
What is 17 plus 28?
Subtract 25 from 100
Divide 144 by 12
Divide 10 by 0
What's the weather today?
```

For the strongest demonstration, open the **Request Processing** panel after a successful calculation. It shows:

1. User request
2. AI understanding
3. Operation
4. Operands
5. MCP tool
6. MCP execution
7. Result
8. Agent response

## Fallback

If Gemini is unavailable, the backend has a clearly labelled **Fallback intent parser** for the four supported operations. The fallback only determines the operation and operands. It still calls the MCP tool for the actual arithmetic.

It never performs the calculation itself.

## Security

- API key is environment-only.
- `.env` is ignored by Git.
- Input is length-limited and validated.
- Only discovered calculator tools can be invoked.
- MCP subprocess command is fixed by application code rather than user input.
- Backend errors are sanitized before reaching the browser.
- API keys and environment variables are never logged.

## Interview explanation

### What is an AI Agent?

The Gemini-powered layer that interprets the user's request, decides whether a calculator tool is needed, selects the tool, and turns the tool result into a natural-language answer.

### What is MCP?

Model Context Protocol is a standardized protocol for connecting AI applications to external tools and context.

### Why MCP here?

The calculator is deliberately separated from the AI layer. The agent can discover the calculator capabilities through MCP rather than knowing the calculator implementation.

### What is the MCP Server?

A separate process exposing `add`, `subtract`, `multiply`, and `divide` as MCP tools.

### What is the MCP Client?

The backend-side MCP client that connects to the server, discovers tools, and invokes a selected tool.

### Where does the calculation happen?

Inside the MCP server's calculator functions.

### Why doesn't Gemini calculate directly?

Because the assignment demonstrates tool use. Gemini selects the operation; the authoritative arithmetic is performed by the external MCP tool.

### What happens if MCP goes down?

The API returns a clean MCP-unavailable error. Gemini is not allowed to bypass the MCP calculation requirement.

## 5-minute demo script

1. Open the UI and point out `Gemini Connected` and `MCP Connected`.
2. Show the dynamically discovered MCP tools.
3. Ask: `Multiply 25 by 8`.
4. Expand `Request Processing`.
5. Explain: "Gemini understood the request, selected the multiply tool, the MCP client invoked the real MCP server, and the MCP server performed the calculation."
6. Try `Add 17 and 28`.
7. Try `Divide 10 by 0` to show controlled error handling.
8. Show `/api/mcp/tools` in the browser and explain that the frontend list comes from actual MCP discovery.

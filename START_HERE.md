# Agentic Calculator — Start Here

This project targets **MCP Python SDK 2.1.0** and uses the official v2 `MCPServer` + `Client` APIs with real STDIO transport.

Architecture:

React → FastAPI → Gemini → MCP Client → MCP Server → Calculator Tool → Gemini → React

## Windows setup

### Terminal 1 — backend

```powershell
cd agentic-calculator\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and put your Gemini API key in `GEMINI_API_KEY`.

Then start the backend:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The backend automatically starts `mcp-server/server.py` as an MCP child process over STDIO. You do **not** start the MCP server separately.

Expected startup logs include:

```text
MCP client starting
Connecting to calculator MCP server
MCP connection established
Discovered 4 MCP tools
Discovered MCP tool: add
Discovered MCP tool: subtract
Discovered MCP tool: multiply
Discovered MCP tool: divide
Application startup complete
```

### Terminal 2 — frontend

```powershell
cd agentic-calculator\frontend
npm install
npm run dev
```

Open the URL printed by Vite, normally:

```text
http://localhost:5173
```

## Backend checks

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
Invoke-RestMethod http://127.0.0.1:8000/api/mcp/tools
```

## Test prompts

```text
Multiply 25 by 8
Add 17 and 28
Subtract 25 from 100
Divide 144 by 12
Divide 10 by 0
```

## Direct MCP server smoke test

If you ever need to verify the child server by itself, run from `backend`:

```powershell
.\.venv\Scripts\python.exe ..\mcp-server\server.py
```

A healthy STDIO MCP server normally prints nothing and waits for a host. Press `Ctrl+C` to stop it. Do not run it separately while also starting FastAPI; FastAPI launches it automatically.

## API docs

```text
http://127.0.0.1:8000/docs
```

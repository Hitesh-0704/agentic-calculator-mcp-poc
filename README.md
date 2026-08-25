# 🧮 Agentic Calculator MCP

<p align="center">
  <strong>AI-powered natural-language calculator using Google Gemini, Model Context Protocol (MCP), FastAPI, and React/Vite.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-Frontend-61DAFB?logo=react&logoColor=111827" alt="React">
  <img src="https://img.shields.io/badge/Vite-Frontend-646CFF?logo=vite&logoColor=white" alt="Vite">
  <img src="https://img.shields.io/badge/MCP-SDK%202.1.0-6B4FBB" alt="MCP SDK">
  <img src="https://img.shields.io/badge/Gemini-2.5%20Flash-4285F4?logo=google&logoColor=white" alt="Gemini">
</p>

<p align="center">
  <b>Gemini understands the request → MCP selects and executes the tool → FastAPI returns the result → React presents it.</b>
</p>

---

## 📌 Overview

**Agentic Calculator MCP** is a full-stack AI-powered calculator designed to demonstrate how a modern AI agent can interact with external tools through the **Model Context Protocol (MCP)**.

Instead of allowing the language model to perform the arithmetic directly, the application separates **AI reasoning** from **deterministic execution**.

The system uses:

- **Google Gemini** for natural-language understanding and tool selection
- **MCP Client** for discovering and invoking tools
- **MCP Server** for deterministic calculator operations
- **FastAPI** for backend orchestration and APIs
- **React + Vite** for the user interface

### 🎯 Core Principle

> **Let the model understand the problem. Let the tool solve the problem.**

Gemini decides **what needs to be done**.

The MCP calculator performs **the actual arithmetic**.

---

# 🏗️ Architecture

```text
                         USER
                           │
                           │ Natural-language request
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     REACT + VITE                            │
│                  Frontend Calculator UI                     │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ POST /api/chat
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                       FASTAPI                               │
│              Backend / Agent Orchestration                  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    GEMINI AGENT                             │
│                                                             │
│  Understand request → Determine operation → Select tool    │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ Tool selection
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      MCP CLIENT                             │
│                                                             │
│        Discover tools → Invoke selected MCP tool            │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ MCP over STDIO
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      MCP SERVER                             │
│                                                             │
│    ┌────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐         │
│    │  add   │ │ subtract │ │ multiply │ │ divide │         │
│    └────────┘ └──────────┘ └──────────┘ └────────┘         │
│                                                             │
│                 AUTHORITATIVE ARITHMETIC                    │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ Result
                             ▼
                       MCP Client
                             │
                             ▼
                          Gemini
                             │
                             ▼
                         FastAPI
                             │
                             ▼
                          React
                             │
                             ▼
                            USER
```

---

# 🔄 How the Agent Works

Suppose the user enters:

```text
Multiply 25 by 8
```

The request flows through the system:

```text
User
 │
 ▼
"Multiply 25 by 8"
 │
 ▼
Gemini
 │
 │ Understands intent
 │
 │ Operation = multiply
 │ Operands = 25, 8
 ▼
MCP Client
 │
 │ Selects multiply tool
 ▼
MCP Server
 │
 │ multiply(25, 8)
 ▼
200
 │
 ▼
Gemini
 │
 │ Generates natural-language response
 ▼
FastAPI
 │
 ▼
React UI
```

### Important Design Decision

Gemini does **not** perform:

```text
25 × 8
```

The MCP calculator performs it.

This keeps deterministic computation outside the probabilistic language model.

---

# 🚀 Features

## 🤖 AI-Powered Natural Language

Users can communicate with the calculator using normal language.

Examples:

```text
Multiply 25 by 8
```

```text
What is 17 plus 28?
```

```text
Subtract 25 from 100
```

```text
Divide 144 by 12
```

The user does not need to provide a structured JSON operation.

---

## 🔌 Model Context Protocol

The project uses the official MCP Python SDK v2 line.

The MCP server exposes calculator capabilities as tools.

Available tools:

```text
add
subtract
multiply
divide
```

The backend MCP client connects to the MCP server through:

```text
STDIO
```

---

## 🔎 Dynamic MCP Tool Discovery

The backend discovers available calculator tools through MCP.

Instead of relying only on a manually maintained list, the application can query the MCP server and discover its capabilities.

The API exposes this through:

```text
GET /api/mcp/tools
```

---

## 🧮 Deterministic Calculator Execution

The arithmetic is performed by the MCP server.

```text
Gemini
   ↓
Tool Selection
   ↓
MCP Client
   ↓
MCP Server
   ↓
Calculator Function
   ↓
Result
```

This creates a clear separation:

```text
AI Layer
   ↓
Reasoning + Intent + Tool Selection

MCP Layer
   ↓
Tool Execution + Arithmetic
```

---

## 🔄 Fallback Intent Parser

The backend contains a clearly labelled fallback intent parser for the four supported calculator operations.

If Gemini is unavailable, the fallback parser can determine:

```text
Operation
Operands
```

However, the fallback parser does **not** perform the arithmetic.

The calculation still goes through the MCP calculator tool.

```text
User
 ↓
Fallback Parser
 ↓
Operation + Operands
 ↓
MCP Tool
 ↓
Calculator
 ↓
Result
```

---

## 🛡️ Controlled Error Handling

The application handles conditions such as:

- Division by zero
- Invalid input
- Unsupported requests
- MCP unavailable
- Backend errors
- Validation failures

Example:

```text
Divide 10 by 0
```

The system should return a controlled error instead of producing an invalid result.

---

# 🧰 Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python 3.11+ |
| AI Model | Google Gemini |
| Gemini SDK | `google-genai` |
| Gemini Model | `gemini-2.5-flash` |
| MCP | Model Context Protocol |
| MCP SDK | Official Python SDK 2.1.0 |
| MCP Transport | STDIO |
| Backend | FastAPI |
| ASGI Server | Uvicorn |
| Validation | Pydantic v2 |
| Frontend | React |
| Frontend Tooling | Vite |
| Testing | Pytest |
| API Testing | HTTPX |

---

# 📁 Project Structure

```text
agentic-calculator-mcp-poc/
│
├── backend/
│   │
│   ├── app/
│   │   ├── agent/
│   │   ├── api/
│   │   ├── core/
│   │   ├── fallback/
│   │   ├── mcp/
│   │   ├── models/
│   │   ├── services/
│   │   └── main.py
│   │
│   ├── tests/
│   │
│   ├── .env.example
│   └── requirements.txt
│
├── frontend/
│   │
│   ├── src/
│   ├── index.html
│   ├── package.json
│   └── package-lock.json
│
├── mcp-server/
│   ├── server.py
│   ├── requirements.txt
│   └── tools/
│
├── architecture.md
├── START_HERE.md
├── .gitignore
├── LICENSE
└── README.md
```

---

# ⚙️ Prerequisites

Before running the project, install:

- Python **3.11 or newer**
- Node.js **18 or newer**
- npm
- A Google Gemini API key

---

# 🚀 Quick Start

## 1. Clone the Repository

```powershell
git clone https://github.com/Hitesh-0704/agentic-calculator-mcp-poc.git
```

Enter the project:

```powershell
cd agentic-calculator-mcp-poc
```

---

# 🐍 Backend Setup

## 2. Open the Backend Directory

```powershell
cd backend
```

---

## 3. Create a Python Virtual Environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell execution policy prevents activation, Command Prompt can be used:

```cmd
.venv\Scripts\activate.bat
```

---

## 4. Install Backend Dependencies

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install project dependencies:

```powershell
pip install -r requirements.txt
```

The MCP SDK is pinned to:

```text
mcp[cli]==2.1.0
```

This keeps the project compatible with the intended MCP v2 API implementation.

---

# 🔑 Gemini API Configuration

## 5. Create the Environment File

From the `backend` directory:

```powershell
Copy-Item .env.example .env
```

Open:

```text
backend/.env
```

Add your Gemini configuration:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
```

### 🔐 Security Warning

Never commit your real `.env` file to GitHub.

Your API key should remain local.

The repository should contain:

```text
.env.example
```

but not:

```text
.env
```

---

# ▶️ Start the Backend

## 6. Run FastAPI

From the `backend` directory:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The backend will start on:

```text
http://127.0.0.1:8000
```

### MCP Server

You do **not** need to manually start another MCP server terminal.

The FastAPI backend automatically starts the MCP calculator server as a child process and communicates with it through STDIO.

---

# ⚛️ Frontend Setup

## 7. Open a Second Terminal

Keep the backend terminal running.

Open another PowerShell terminal and return to the project root:

```powershell
cd agentic-calculator-mcp-poc
```

Go to the frontend:

```powershell
cd frontend
```

---

## 8. Install Frontend Dependencies

```powershell
npm install
```

---

## 9. Start the Frontend

```powershell
npm run dev
```

Vite normally starts the frontend at:

```text
http://localhost:5173
```

Open the URL shown by Vite in your browser.

---

# 🩺 Backend Health Checks

Once the backend is running, use these endpoints.

## Swagger / OpenAPI

```text
http://127.0.0.1:8000/docs
```

This provides the interactive API documentation.

---

## Health Check

```text
http://127.0.0.1:8000/api/health
```

This endpoint is used to verify backend health.

---

## MCP Status

```text
http://127.0.0.1:8000/api/mcp/status
```

This can be used to inspect MCP connection status.

---

## MCP Tools

```text
http://127.0.0.1:8000/api/mcp/tools
```

This exposes the dynamically discovered MCP calculator tools.

---

## Root URL

The following URL:

```text
http://127.0.0.1:8000/
```

may return:

```json
{
  "detail": "Not Found"
}
```

This is expected if no root `/` route is defined.

Use:

```text
http://127.0.0.1:8000/api/health
```

or:

```text
http://127.0.0.1:8000/docs
```

to verify the backend.

---

# 🔌 MCP Execution

The MCP server exposes calculator tools.

```text
add
subtract
multiply
divide
```

The backend MCP client discovers these tools and invokes the selected operation.

For example:

```text
multiply(25, 8)
```

The MCP calculator performs:

```text
25 × 8 = 200
```

The result is then returned to the agent pipeline.

---

# 🔍 MCP Tool Discovery

The system can expose discovered tools through:

```text
GET /api/mcp/tools
```

Expected calculator capabilities include:

```text
add
subtract
multiply
divide
```

This demonstrates that the application is using the MCP server as a real tool provider.

---

# 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Backend health check |
| `GET` | `/api/mcp/status` | MCP connection/status |
| `GET` | `/api/mcp/tools` | Dynamically discovered MCP tools |
| `POST` | `/api/chat` | Natural-language calculator request |
| `GET` | `/docs` | Swagger/OpenAPI documentation |

---

# 🧪 Testing

The backend contains automated tests.

Go to:

```powershell
cd backend
```

Activate the virtual environment if necessary:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run:

```powershell
pytest -q
```

The tests cover areas including:

- Calculator logic
- Fallback intent parsing
- API validation
- MCP discovery
- MCP invocation
- In-memory MCP client testing
- HTTP/API behaviour

---

# 🎬 Demo

The application supports natural-language calculator requests.

Try:

```text
Multiply 25 by 8
```

```text
Add 3 and 4
```

```text
What is 17 plus 28?
```

```text
Subtract 25 from 100
```

```text
Divide 144 by 12
```

```text
Divide 10 by 0
```

---

# 🏆 Recommended 5-Minute Presentation

## Step 1 — Show the UI

Point out:

```text
Gemini Connected
MCP Connected
```

and the discovered calculator tools.

---

## Step 2 — Send a Request

Enter:

```text
Multiply 25 by 8
```

---

## Step 3 — Show Request Processing

Open the request-processing section.

Show the pipeline:

```text
User Request
     ↓
AI Understanding
     ↓
Operation
     ↓
Operands
     ↓
MCP Tool
     ↓
MCP Execution
     ↓
Result
     ↓
Agent Response
```

---

## Step 4 — Explain the Architecture

Use this explanation:

> Gemini understands the natural-language request and determines which calculator operation is required. The MCP client then invokes the real calculator tool exposed by the MCP server. The MCP server performs the arithmetic and returns the result. Gemini can then formulate the final natural-language response.

---

## Step 5 — Demonstrate Another Request

Try:

```text
Add 17 and 28
```

---

## Step 6 — Demonstrate Error Handling

Try:

```text
Divide 10 by 0
```

Explain that division-by-zero is handled by the calculator/tool layer rather than allowing the AI to invent a result.

---

## Step 7 — Demonstrate MCP Discovery

Open:

```text
http://127.0.0.1:8000/docs
```

Use:

```text
GET /api/mcp/tools
```

Explain:

> The calculator tools are discovered from the MCP server rather than simply being hard-coded into the frontend.

---

# 🧠 Interview / Viva Questions

## What is an AI Agent?

The Gemini-powered layer that interprets the user's request, determines what capability is needed, selects the appropriate tool, and generates a natural-language response from the tool result.

---

## What is MCP?

**Model Context Protocol (MCP)** is a standardized protocol for connecting AI applications with external tools and context.

It provides a structured way for an AI application to discover and interact with external capabilities.

---

## Why did you use MCP?

The purpose of this project is to demonstrate separation between:

```text
AI Reasoning
      ↓
Tool Discovery
      ↓
Tool Selection
      ↓
Tool Execution
```

MCP provides the standardized tool communication layer.

---

## What is the MCP Server?

The MCP server is a separate process that exposes calculator functionality as MCP tools.

The tools are:

```text
add
subtract
multiply
divide
```

---

## What is the MCP Client?

The MCP client runs on the backend side.

It is responsible for:

1. Connecting to the MCP server
2. Discovering available tools
3. Selecting/invoking the required tool
4. Receiving the tool result

---

## Where does the calculation happen?

The actual arithmetic happens inside the MCP calculator functions.

The Gemini model does not act as the authoritative calculator.

---

## Why doesn't Gemini calculate directly?

Because the project is demonstrating tool-based agent architecture.

Gemini is responsible for:

```text
Understanding
Reasoning
Tool Selection
```

The MCP server is responsible for:

```text
Deterministic Arithmetic
```

This creates a cleaner separation of responsibilities.

---

## What happens if MCP goes down?

The application reports an MCP-unavailable error.

The agent is not supposed to silently bypass the MCP calculator and perform the calculation itself.

---

## What happens if Gemini is unavailable?

The application has a clearly labelled fallback intent parser for the supported calculator operations.

The fallback determines:

```text
Operation
Operands
```

but the actual arithmetic still goes through MCP.

---

# 🔄 Fallback Flow

```text
                 User Request
                      │
                      ▼
              Gemini Available?
                 /          \
               YES           NO
                │             │
                ▼             ▼
             Gemini      Fallback Parser
                │             │
                └──────┬──────┘
                       │
                       ▼
               Operation + Operands
                       │
                       ▼
                  MCP Client
                       │
                       ▼
                  MCP Server
                       │
                       ▼
                  Calculator
                       │
                       ▼
                    Result
```

---

# 🔐 Security

The project follows several security practices.

### API Key Protection

The Gemini API key is stored in environment configuration:

```text
backend/.env
```

and should never be committed to source control.

---

### Input Validation

User input is validated before processing.

---

### Input Length Limits

Input length is constrained to reduce unnecessary or unexpected payloads.

---

### Controlled MCP Tools

Only the intended calculator tools can be invoked.

---

### Controlled MCP Process

The MCP subprocess command is defined by application configuration rather than arbitrary user input.

---

### Sanitized Errors

Backend errors are handled and sanitized before being returned to the browser.

---

### No API Key Logging

API keys and environment secrets should never be intentionally logged.

---

# 🌟 Design Principles

## 1. Separate Reasoning From Execution

```text
Gemini → Understands and Decides
MCP    → Executes
```

---

## 2. Deterministic Tools for Deterministic Tasks

Arithmetic should be handled by deterministic application code instead of relying on probabilistic model output.

---

## 3. Dynamic Capability Discovery

MCP allows the backend to discover available tools from the MCP server.

---

## 4. Explicit Failure

If MCP is unavailable, the application should report the failure rather than silently bypassing the intended execution path.

---

## 5. Secrets Stay Local

Credentials belong in environment variables and should never be committed to GitHub.

---

# 📊 Request Processing

The frontend can expose the internal processing pipeline:

```text
┌───────────────────────┐
│    User Request       │
└───────────┬───────────┘
            ▼
┌───────────────────────┐
│   AI Understanding    │
└───────────┬───────────┘
            ▼
┌───────────────────────┐
│      Operation        │
└───────────┬───────────┘
            ▼
┌───────────────────────┐
│       Operands        │
└───────────┬───────────┘
            ▼
┌───────────────────────┐
│      MCP Tool         │
└───────────┬───────────┘
            ▼
┌───────────────────────┐
│    MCP Execution      │
└───────────┬───────────┘
            ▼
┌───────────────────────┐
│        Result         │
└───────────┬───────────┘
            ▼
┌───────────────────────┐
│   Agent Response      │
└───────────────────────┘
```

---

# 💡 Why This Project Matters

The calculator itself is intentionally simple.

The important part is the architecture.

The same pattern can be extended to much more complex AI systems.

For example:

```text
                 AI Agent
                    │
                    ▼
                   MCP
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       Database    APIs     Files
          │         │         │
          ▼         ▼         ▼
       Tools     Tools     Tools
```

Instead of building an AI system that directly performs every task, the model can reason about the task and use specialized external tools.

---

# 🔮 Possible Future Extensions

The architecture can be extended with additional MCP tools such as:

```text
Weather Tool
Currency Conversion
Database Queries
Web Search
File Search
Unit Conversion
Date / Time Utilities
Enterprise APIs
```

The calculator therefore serves as a small demonstration of a broader tool-using agent architecture.

---

# 🛠️ Development Commands

## Backend

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

## Tests

```powershell
cd backend
pytest -q
```

---

# 📚 Project Documentation

Additional documentation available in the repository:

- [`START_HERE.md`](START_HERE.md) — Getting started instructions
- [`architecture.md`](architecture.md) — Architecture details
- [`backend/requirements.txt`](backend/requirements.txt) — Backend dependencies
- [`frontend/package.json`](frontend/package.json) — Frontend dependencies
- [`LICENSE`](LICENSE) — Project license

---

# 📦 Dependency Philosophy

The repository intentionally does **not** include local environments or installed dependency folders.

Do not commit:

```text
.venv/
venv/
__pycache__/
node_modules/
.env
```

Dependencies should be installed on the target machine using:

```powershell
pip install -r requirements.txt
```

and:

```powershell
npm install
```

This keeps the GitHub repository lightweight and portable.

---

# 🚫 Files That Should Not Be Committed

Never upload:

```text
.env
.venv/
venv/
node_modules/
__pycache__/
*.pyc
```

The `.gitignore` file should exclude these development-only files.

---

# 🖥️ Running on Another Laptop

To run the project on another development machine:

```text
1. Clone repository
        ↓
2. Install Python
        ↓
3. Install Node.js
        ↓
4. Create Python virtual environment
        ↓
5. Install backend requirements
        ↓
6. Create backend/.env
        ↓
7. Add Gemini API key
        ↓
8. Start FastAPI
        ↓
9. npm install
        ↓
10. npm run dev
        ↓
11. Open frontend
```

No `.venv` or `node_modules` folder needs to be transferred through GitHub.

---

# 📌 Compatibility

The project is designed around:

```text
Python 3.11+
MCP Python SDK 2.1.0
Google GenAI SDK
FastAPI
React
Vite
```

The MCP implementation uses the intended MCP v2 API surface.

---

# 👨‍💻 Project Summary

**Agentic Calculator MCP** demonstrates a practical AI agent architecture where:

```text
Natural Language
       ↓
     Gemini
       ↓
 Tool Selection
       ↓
   MCP Client
       ↓
   MCP Server
       ↓
Deterministic Calculator
       ↓
     Result
       ↓
 Natural Language
```

The project combines:

**Generative AI + Tool Calling + MCP + FastAPI + React + Deterministic Execution**

---

# ⭐ Core Takeaway

> **The model understands the problem.  
> MCP connects the model to the capability.  
> The external tool performs the deterministic work.**

---

## 📄 License

This project is distributed under the **MIT License**.

See [`LICENSE`](LICENSE) for the complete license text.

---

<p align="center">
  <strong>🧮 Agentic Calculator MCP</strong>
  <br>
  AI Reasoning × MCP Tooling × Deterministic Execution
</p>

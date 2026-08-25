                                     🧮 Agentic Calculator MCP

<p align="center">
  <strong>Natural-language calculations powered by Google Gemini, Model Context Protocol (MCP), FastAPI, and React.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-Frontend-61DAFB?logo=react&logoColor=111827" alt="React">
  <img src="https://img.shields.io/badge/Vite-Frontend%20Tooling-646CFF?logo=vite&logoColor=white" alt="Vite">
  <img src="https://img.shields.io/badge/MCP-SDK%202.1.0-6B4FBB" alt="MCP SDK 2.1.0">
  <img src="https://img.shields.io/badge/Gemini-2.5%20Flash-4285F4?logo=google&logoColor=white" alt="Gemini 2.5 Flash">
</p>

<p align="center">
  <a href="#-overview">Overview</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-key-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-api">API</a> •
  <a href="#-testing">Testing</a> •
  <a href="#-demo">Demo</a>
</p>

✨ Overview

Agentic Calculator MCP is a full-stack AI calculator that turns natural-language requests into controlled tool calls.

Instead of allowing the language model to perform arithmetic directly, the project separates reasoning from execution:

Gemini understands the user's request and selects the appropriate operation.

MCP Client discovers and invokes calculator capabilities through the Model Context Protocol.

MCP Server performs the authoritative arithmetic.

FastAPI orchestrates the agent workflow and exposes the backend API.

React/Vite provides the interactive user interface and visualizes the request-processing flow.

The core idea

The AI decides what tool to use. The MCP tool performs the calculation.

This makes the project a compact but realistic demonstration of AI agents + tool calling + MCP + API orchestration + modern frontend development.

🎯 What the Project Demonstrates

This project is intentionally designed around a real agentic workflow rather than a calculator hidden behind an AI-looking interface.

User asks

"Multiply 25 by 8"

Agent workflow

Natural Language
      │
      ▼
   Gemini
      │
      │ Understands intent
      │ Selects calculator tool
      ▼
  MCP Client
      │
      │ Discovers / invokes tool
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
      ▼
Natural-language response

The arithmetic itself remains outside the model.

🏗️ Architecture

┌───────────────────────────────────────────────────────────────┐
│                         React / Vite                         │
│                  Natural-language calculator UI              │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                │ POST /api/chat
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                          FastAPI                              │
│                 API + Agent Orchestration                    │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                       Gemini Agent                            │
│       Understand request → select operation/tool             │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                │ Tool selection
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                         MCP Client                            │
│             Discover tools → invoke selected tool            │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                │ MCP over STDIO
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                         MCP Server                            │
│                                                               │
│     add   │   subtract   │   multiply   │   divide           │
│                                                               │
│              Authoritative arithmetic                         │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
                              Result
                                │
                                ▼
                    MCP Client → Gemini
                                │
                                ▼
                           FastAPI → UI

Important architectural decision

The calculator implementation is deliberately isolated inside the MCP server.

Gemini is not the source of truth for arithmetic.

That separation demonstrates a key agentic design principle:

LLM for interpretation and decision-making; deterministic tools for execution.

🚀 Key Features

🤖 Gemini-powered agent

Understands natural-language calculator requests and selects the appropriate operation.

🔌 Real MCP integration

Uses the official MCP Python SDK with the v2 API surface and STDIO transport.

🔎 Dynamic tool discovery

The backend discovers calculator tools from the MCP server instead of hard-coding the available tool list into the UI.

🧮 Deterministic arithmetic

add, subtract, multiply, and divide execute inside the MCP server.

🛡️ Controlled tool execution

Only discovered calculator tools are eligible for invocation.

🔄 Fallback intent parser

If Gemini is unavailable, the backend can fall back to a clearly labelled intent parser for the four supported operations.

The fallback determines:

operation

operands

It does not perform the arithmetic itself.

The actual calculation still goes through MCP.

⚠️ Controlled error handling

Examples include:

division by zero

invalid requests

unavailable MCP service

backend failures

📊 Request Processing visualization

The UI exposes the agent workflow, including:

User request

AI understanding

Operation

Operands

MCP tool

MCP execution

Result

Final agent response

🧰 Tech Stack

Layer

Technology

AI

Google Gemini

Gemini SDK

google-genai

Gemini Model

gemini-2.5-flash

Agent Backend

FastAPI + Uvicorn

Tool Protocol

Model Context Protocol

MCP SDK

Official Python SDK 2.1.0

MCP Transport

STDIO

Validation

Pydantic v2

Frontend

React

Frontend Tooling

Vite

HTTP Client

HTTPX

Testing

Pytest + pytest-asyncio

Language

Python 3.11+ / JavaScript

Compatibility

This project is pinned to:

MCP Python SDK 2.1.0

and uses the v2 MCPServer / Client APIs.

📁 Project Structure

agentic-calculator-mcp-poc/
│
├── backend/
│   ├── app/
│   │   ├── agent/
│   │   │   ├── gemini_client.py
│   │   │   └── prompts.py
│   │   │
│   │   ├── api/
│   │   │   └── routes.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── exceptions.py
│   │   │   └── logging.py
│   │   │
│   │   ├── fallback/
│   │   │   └── parser.py
│   │   │
│   │   ├── mcp/
│   │   │   ├── client.py
│   │   │   └── manager.py
│   │   │
│   │   ├── models/
│   │   │   └── schemas.py
│   │   │
│   │   ├── services/
│   │   │   └── calculator_service.py
│   │   │
│   │   └── main.py
│   │
│   ├── tests/
│   │   ├── test_api.py
│   │   ├── test_calculator.py
│   │   ├── test_fallback.py
│   │   └── test_formatting_and_service.py
│   │
│   ├── .env.example
│   └── requirements.txt
│
├── frontend/
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

⚡ Quick Start

Prerequisites

Install:

Python 3.11+

Node.js 18+

npm

A Gemini API key

1. Clone the repository

git clone https://github.com/Hitesh-0704/agentic-calculator-mcp-poc.git
cd agentic-calculator-mcp-poc

2. Create the Python environment

cd backend
python -m venv .venv

Windows PowerShell

.\.venv\Scripts\Activate.ps1

If activation is blocked by PowerShell policy, use Command Prompt:

.venv\Scripts\activate.bat

3. Install backend dependencies

python -m pip install --upgrade pip
pip install -r requirements.txt

The MCP SDK is intentionally pinned to:

mcp[cli]==2.1.0

4. Configure Gemini

Create your local environment file:

Copy-Item .env.example .env

Then edit:

backend/.env

Add your API key:

GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash

Additional backend configuration can be supplied through the variables documented in .env.example.

Never commit .env. It contains secrets and is intentionally ignored by Git.

5. Start the backend

From backend:

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

The FastAPI process automatically starts the MCP calculator server as a child process over STDIO.

You do NOT need a separate terminal for the MCP server.

6. Start the frontend

Open a second terminal:

cd agentic-calculator-mcp-poc/frontend
npm install
npm run dev

Open the URL printed by Vite, normally:

http://localhost:5173

🩺 Verify the Backend

Once the backend is running, open:

http://127.0.0.1:8000/docs

FastAPI Swagger UI provides the available API operations.

Health

GET /api/health

MCP status

GET /api/mcp/status

MCP tools

GET /api/mcp/tools

Agent chat

POST /api/chat

http://127.0.0.1:8000/ may return {"detail":"Not Found"} because the application intentionally exposes its API under /api/*. Use /api/health or /docs to verify the service.

🔌 MCP Workflow

The MCP layer is not decorative. It is part of the actual execution path.

1. Backend starts

FastAPI initializes the MCP manager.

2. MCP server starts

The calculator MCP server runs as a child process using STDIO.

3. Client connects

The backend-side MCP client establishes the connection.

4. Tools are discovered

The client asks the MCP server what tools are available.

5. Gemini selects a tool

For example:

"Multiply 25 by 8"
          ↓
      multiply

6. MCP invokes the tool

multiply(25, 8)

7. MCP server performs arithmetic

200

8. Result returns through the agent pipeline

MCP Server
    ↓
MCP Client
    ↓
Gemini
    ↓
FastAPI
    ↓
React

🧪 Testing

From the backend directory:

pytest -q

The test suite covers areas including:

calculator logic

fallback intent parsing

API validation

formatting/service behavior

MCP discovery/invocation through the official SDK's in-memory client

🎬 Demo Scenarios

Try these requests in the UI:

Multiply 25 by 8

Add 3 and 4

What is 17 plus 28?

Subtract 25 from 100

Divide 144 by 12

Divide 10 by 0

What's the weather today?

The last two are useful for demonstrating controlled error handling and unsupported intent handling.

🏆 Recommended 5-Minute Demo

1. Show the application

Point out:

Gemini connection status

MCP connection status

dynamically discovered tools

2. Ask

Multiply 25 by 8

3. Open Request Processing

Walk through:

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

4. Explain the architecture

"Gemini understands the natural-language request and selects the calculator operation. The MCP client invokes the real calculator tool exposed by the MCP server. The MCP server performs the arithmetic, so the language model is not the arithmetic authority."

5. Demonstrate an error

Try:

Divide 10 by 0

Use this to demonstrate controlled error handling.

6. Show dynamic MCP discovery

Open:

http://127.0.0.1:8000/docs

Then demonstrate:

GET /api/mcp/tools

Explain that the available calculator tools come from actual MCP discovery.

🧠 Why MCP?

A traditional implementation could simply put calculator functions directly inside the FastAPI application.

This project intentionally does not do that.

MCP creates a clean boundary:

AI / Agent Layer
       │
       │ standardized tool protocol
       ▼
    MCP Layer
       │
       ▼
 External Tool Capability

That makes the calculator capability independently discoverable and invokable.

The same pattern can be extended to other tool categories such as:

databases

file systems

enterprise APIs

search

business systems

developer tools

The calculator is intentionally small so the underlying agent + tool architecture is easy to understand.

🧩 Fallback Design

When Gemini is unavailable, the backend can use a clearly labelled fallback intent parser for the four supported calculator operations.

The fallback parser:

User text
   ↓
Detect operation
   ↓
Extract operands
   ↓
Call MCP tool
   ↓
Return result

It does not calculate the answer itself.

This preserves the architectural rule:

Arithmetic belongs to the MCP calculator tool.

🔐 Security & Reliability

The project includes several safeguards:

API keys are environment-only.

.env is ignored by Git.

Input is length-limited and validated.

Only discovered calculator tools can be invoked.

MCP subprocess configuration is controlled by application code rather than user input.

Backend errors are sanitized before reaching the browser.

API keys and environment variables are not intentionally logged.

Division-by-zero is handled as a controlled calculator error.

MCP failures are surfaced as clean application errors rather than silently bypassing the tool layer.

💬 Interview / Viva Explanation

What is an AI Agent?

The Gemini-powered layer interprets the user's request, determines whether a calculator capability is needed, selects the appropriate tool, and converts the tool result into a natural-language response.

What is MCP?

Model Context Protocol is a standardized protocol for connecting AI applications with external tools and context.

Why use MCP for a calculator?

The goal is not to make the calculator itself complicated. The calculator demonstrates a clean separation between:

AI reasoning

tool discovery

tool invocation

deterministic execution

What is the MCP Server?

A separate process exposing:

add
subtract
multiply
divide

as MCP tools.

What is the MCP Client?

The backend-side MCP client that:

connects to the server

discovers available tools

invokes the selected tool

receives the result

Where does the calculation happen?

Inside the MCP server's calculator functions.

Why doesn't Gemini calculate directly?

Because the architecture intentionally treats Gemini as the reasoning/tool-selection layer, while the MCP server is the execution layer.

What happens if MCP goes down?

The API returns a controlled MCP-unavailable error. Gemini is not allowed to bypass the MCP calculation requirement.

📌 API Reference

Method

Endpoint

Purpose

GET

/api/health

Backend health

GET

/api/mcp/status

MCP connection/status

GET

/api/mcp/tools

Dynamically discovered tools

POST

/api/chat

Natural-language agent interaction

GET

/docs

Swagger/OpenAPI documentation

🛠️ Development Notes

Backend

cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

Frontend

cd frontend
npm install
npm run dev

Tests

cd backend
pytest -q

🌟 Design Principles

This project follows a few deliberate principles:

1. Separate reasoning from execution

Gemini → decides
MCP    → executes

2. Prefer deterministic tools for deterministic work

Arithmetic should not depend on probabilistic model output.

3. Discover capabilities dynamically

The frontend can reflect the tools exposed by the MCP server rather than maintaining a separate hard-coded tool registry.

4. Fail explicitly

If Gemini or MCP is unavailable, the system should report the condition rather than silently pretending the operation succeeded.

5. Keep secrets out of source control

Credentials belong in environment configuration, never in Git.

📚 Further Documentation

START_HERE.md — project setup and getting started

architecture.md — architecture details

backend/requirements.txt — Python dependencies

frontend/package.json — frontend dependencies

👨‍💻 Project

Agentic Calculator MCP

Built as a practical demonstration of:

Generative AI
     +
Tool Calling
     +
Model Context Protocol
     +
FastAPI
     +
React
     +
Deterministic Execution

Core principle

Let the model understand the problem. Let the tool solve the problem.

📄 License

This project is distributed under the repository's MIT License.

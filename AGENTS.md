# AGENTS.md — Instructions for AI Coding Agents

> **IMPORTANT**: This repository represents **Open Agent AWS**, a production-oriented autonomous AI execution platform. For the complete system architecture, product vision, component specifications, and end-to-end walkthroughs, always refer to [PROJECT_OVERVIEW.md](file:///workspaces/open_Agent_Aws-/PROJECT_OVERVIEW.md).

---

## 1. Role of the AI Agent

You are working as an **AI implementation assistant**, not the system architect.

When working in this repository:
1. **Understand Before Modifying**: Inspect existing files, interfaces, and architecture before making changes.
2. **Reuse Existing Abstractions**: Build upon established patterns (Strategy, Repository, Adapter, Dependency Injection). Do not create duplicate or parallel systems.
3. **Respect Architectural Boundaries**: Never collapse distinct components (e.g. LLM, Agent, Runtime, Tool, Computer, Database Model) into a monolithic file or class.
4. **Preserve Naming & Directory Conventions**: Follow established project conventions in `backend/`, `web/`, and `mobile/`.
5. **No False Claims**: Never mark a feature as completed in `PROGRESS.md` or in responses if it only exists as a scaffold, interface, mock, placeholder, or unused class.

---

## 2. Non-Negotiable Architectural Invariants

Every AI agent working on this codebase must strictly preserve the following architectural boundaries:

```text
LLM != Agent
Agent != Runtime
Agent != Tool
Agent != Computer
Connector != Tool
Integration != Tool
Memory != Database
Database Model != Runtime Object
API != Agent
LLM Provider Fallback != Agent Fallback
```

- **LLM != Agent**: The LLM provides reasoning and text/tool generation. The Agent represents a configured domain worker with identity, capabilities, and settings.
- **Agent != Runtime**: `Agent` is a configuration domain model. `AgentRuntime` executes runs, manages step limits, timeouts, observations, and state transitions.
- **Agent != Tool**: Tools are individual executable capabilities exposed to agents. Agents do not contain tool execution logic.
- **Agent != Computer**: Computers provide operating environment interaction (`screenshot`, `click`, `type`).
- **Connector != Tool**: A Connector talks to an external API (Slack, GitHub, Gmail). A Tool wraps specific connector operations for agent invocation.
- **Integration != Tool**: An Integration represents a user's service connection and auth state.
- **Memory != Database**: PostgreSQL stores structured execution history; Qdrant stores semantic vector embeddings; S3 stores raw artifact bytes.
- **Database Model != Runtime Object**: SQLAlchemy models are strictly persistence entities. Runtime domain objects represent application behavior.
- **API != Agent**: FastAPI is the central control plane and coordinator, not an agent.
- **LLM Fallback != Agent Fallback**: 
  - *LLM Fallback*: Switches model/provider (e.g. Groq $\rightarrow$ Gemini).
  - *Agent Fallback*: Reassigns the task to an alternate agent with matching capabilities and permissions.

---

## 3. Engineering Progression Rule

The project grows strictly from working primitives toward higher abstractions. **Never implement future layers prematurely.**

Follow this preferred progression order:

```text
1. Database Foundation (Neon PostgreSQL, SQLAlchemy, Alembic)
   ↓
2. Agent State (AgentState runtime dataflow)
   ↓
3. LangGraph Orchestration (Baseline START → LLM → END)
   ↓
4. LLM Node & Provider Abstraction (Strict Fallback: Groq → Gemini → Mistral)
   ↓
5. Agent Runtime (Execution boundary, step limits, timeouts)
   ↓
6. Tool Loop & Tool Executor (LLM ↔ Observation loop)
   ↓
7. Tool Registry & Built-in Tools
   ↓
8. Persistence (Repository layer, runs, messages, tool calls)
   ↓
9. Dynamic Agent Creation & Agent Registry
   ↓
10. Document Intelligence (PDF, image, and document ingestion via Gemini)
   ↓
11. External Integrations (Google Docs, Drive, Slack, Gmail, GitHub)
   ↓
12. Interactive Integration Authentication Checks
   ↓
13. Conversational Chat Agent (Coordinator & Worker Management)
   ↓
14. Multi-Day Autonomous Scheduling & User Notifications
   ↓
15. AWS EC2 Cloud Computer (Cloud-Only, No Local Computer)
   ↓
16. Computer Perception/Reasoning/Action Loop
   ↓
17. Artifact System & S3 Storage
   ↓
18. Semantic Memory & Qdrant RAG
   ↓
19. Distributed Execution & Background Workers
   ↓
20. Web (Next.js) & Mobile (React Native / Expo) Clients
   ↓
21. Production Reliability, Sentry & Observability
```

---

## 4. Code Quality & Module Standards

- **~250-Line Practical Warning Threshold**: When any file approaches or exceeds ~250 lines, identify distinct responsibilities and extract cohesive components.
- **Strict Typing**:
  - Python: Explicit type annotations, Pydantic models for validation, no untyped dictionaries for domain entities.
  - TypeScript (Frontend/Mobile): Strict mode, explicit types, generics, discriminated unions. **Never use `any`**.
- **Dependency Injection**: Pass dependencies (LLM providers, tool registries, computers) into runtimes and graphs. Do not instantiate providers secretly inside business logic.
- **Cohesion & Simplicity**:
  - Small, focused classes with single responsibilities.
  - Stateless utility functions where applicable.
  - Minimal duplication.
  - No hidden global mutable state.
  - No provider-specific logic leaking into domain models.

---

## 5. Persistence vs. Runtime Separation

Persistence and runtime concerns must remain decoupled:
- **SQLAlchemy Models**: Live in repository/database layers, representing table schemas and foreign key relationships.
- **Domain/Runtime Objects**: Represent runtime entities (`Agent`, `Task`, `Run`, `Tool`).
- **Repositories**: Bridge persistence and runtime:
  ```text
  Database Model  ──(Repository)──>  Domain Object
  ```
- **Rule**: Never pass SQLAlchemy models directly into LangGraph state, LLM prompts, or runtime tool executors.

---

## 6. Authentication, Ownership & User Scoping

- **Clerk Owns Authentication**: The Python backend does not maintain a local `User` authentication table.
- **User Scoping**: The backend receives the authenticated external `user_id` from Clerk.
- **Ownership Invariant**: Every user-owned AI resource (agents, tasks, runs, messages, tool calls, computer sessions, artifacts, integration connections) must include `user_id`.
- **Enforcement**: Repositories and services must always enforce ownership checks:
  ```python
  get_agent(user_id: str, agent_id: str)
  list_agents(user_id: str)
  get_task(user_id: str, task_id: str)
  ```
  An agent or task belonging to User A must **never** be accessible to User B.

---

## 7. Storage Separation

Do not mix storage systems. Each has an explicit role:
- **Neon PostgreSQL**: Structured state, execution history, metadata, ownership, task/run states.
- **Qdrant**: Vector embeddings, similarity search, semantic memory, RAG context retrieval.
- **AWS S3**: Raw file bytes, report downloads, generated documents, screenshots, artifact files.

---

## 8. Tools, Integrations & Connectors

- **Tools**:
  - Inherit from the common `Tool` base class.
  - Have stable names, clear descriptions, validated input schemas, and explicit error handling.
  - Perform one cohesive capability (e.g. `web_search`, `read_file`, `create_github_issue`).
- **Integrations & Connectors**:
  - Hierarchy: `Integration` (connection/auth) $\rightarrow$ `Connector` (API client) $\rightarrow$ `Tool` (agent capability) $\rightarrow$ `Agent`.
  - Credentials and OAuth tokens are security-sensitive. Raw access tokens must **never** be passed into prompt contexts or generic metadata.
  - Enforce permission checks before an agent can invoke external integration tools.
  - **Interactive Integration Checks**: If an agent requires an external integration (e.g. Google Docs) that is not authenticated or connected for the user, the agent runtime or Conversational Chat Agent must interactively prompt the user in chat to connect before proceeding.

---

## 9. Computer-Use Abstraction (Cloud-Only AWS EC2)

- Abstract computer control behind a unified `Computer` interface.
- Computer execution is strictly cloud-only (`AWSComputer` on EC2). The platform does **not** automate or control the user's local machine or personal computer.
- The agent interacts via standard perception-reasoning-action operations (`screenshot`, `click`, `type`, `press_key`, `scroll`).

---

## 10. Security & High-Impact Action Tiers

- **Secret Safety**: Never expose API keys, OAuth tokens, refresh tokens, private keys, or internal credentials to the model.
- **Action Tiers**: Distinguish **READ** actions from **WRITE / HIGH-IMPACT** actions:
  - *Read Actions*: Fetching web pages, reading files, searching messages, querying issues.
  - *High-Impact Actions*: Sending emails, sending Slack messages, deleting files, pushing code to GitHub, running shell commands.
- High-impact operations must enforce strict permissions and support user confirmation checks where configured.

---

## 11. Error Handling & Observability

- **Explicit Exceptions**: All custom exceptions inherit from `OpenAgentError`:
  ```text
  OpenAgentError
    ├── ConfigurationError
    ├── AgentError
    ├── ToolError
    └── ComputerError
  ```
- **No Silent Catches**: Never use broad `except Exception: pass`. Handle errors at the layer with appropriate context.
- **Observability**: Maintain structured telemetry across execution steps, LLM calls, latency, tool calls, and errors. Sentry is used across backend, web, and mobile clients.

---

## 12. Documentation Standards & Truthfulness

- **PROGRESS.md**:
  - Record the **actual** state of development.
  - Sections: Completed Work, Current Work, Next Work, Architectural Decisions, Known Blockers.
  - Rule: Never mark a feature complete if it is only scaffolded or mocked.
- **ERR.md**:
  - Record significant errors, root causes, fixes, affected subsystems, and regression prevention.
- **PROJECT_OVERVIEW.md**:
  - Update when major architectural decisions evolve.

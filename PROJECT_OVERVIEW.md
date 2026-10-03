# Open Agent AWS — Project Context

## 1. Project Identity

Open Agent AWS is a production-oriented autonomous AI execution platform.

It is designed to allow users to create and interact with AI agents that can reason about tasks, use tools, operate computers, interact with external applications, process files, access semantic memory, collaborate with other agents, and execute long-running real-world workflows.

The project is not intended to be a simple chatbot, an LLM wrapper, or a collection of API integrations.

The core idea is:

> Build an AI execution platform where the LLM is the reasoning component, while the surrounding system provides identity, state, tools, memory, computers, integrations, orchestration, security, persistence, and execution.

The platform is intended to eventually let a user say something such as:

> "Check my Slack messages, find anything important, look at the related GitHub issues, update the relevant issue, check the staging website, and send me a summary."

The system should be capable of decomposing that request, selecting the appropriate capabilities, executing the workflow, maintaining state, handling failures, and returning the result.

---

# 2. What We Are Building

Open Agent AWS is a centralized AI control plane with distributed execution capabilities.

At the highest level:

User
  ↓
Web / Mobile / API Client
  ↓
FastAPI Control Plane
  ↓
Agent System
  ↓
Agent Runtime
  ↓
LangGraph
  ↓
LLM + Tools + Integrations + Computer + Memory
  ↓
Execution
  ↓
Results / Artifacts / Persistent State
  ↓
User

The system is centralized in orchestration and state management, but execution can happen across different environments.

For example:

- sandboxed AWS EC2 cloud computers
- browser environments
- background workers
- external APIs
- connected applications
- multiple AI agents

This makes the system a centralized control plane with distributed execution.

---

# 3. The Fundamental Idea

The project is built around the following distinction:

LLM != Agent

Agent != Runtime

Agent != Tool

Agent != Computer

Connector != Tool

Integration != Tool

Memory != Database

Database Model != Runtime Object

API != Agent

Each component has a specific responsibility.

The LLM provides reasoning and generation.

The Agent represents an AI worker and its configuration.

The Runtime executes the agent.

LangGraph orchestrates execution.

Tools provide capabilities.

Connectors communicate with external services.

Computers provide an environment in which actions can be performed.

PostgreSQL stores structured persistent state.

Qdrant stores vector/semantic memory.

S3 stores actual artifact bytes.

FastAPI acts as the central control plane.

The clients provide interfaces through which users interact with the platform.

---

# 4. Product Vision

The long-term goal is to create a platform where an AI agent can operate across the software and computing environments a user already uses.

The agent should eventually be able to:

- understand natural-language tasks
- plan multi-step work
- call tools
- use APIs
- interact with websites
- operate a computer
- run on a cloud computer
- read files
- understand images
- process documents
- retrieve relevant memory
- perform RAG
- communicate with other agents
- interact with Slack
- interact with Gmail
- interact with GitHub
- interact with Google Drive
- interact with Google Calendar
- interact with Notion
- interact with other connected applications
- create and modify external resources
- respond to events
- generate files
- maintain task history
- recover from failures
- use different LLM providers
- continue long-running tasks
- report progress in real time

The goal is not to make the agent "smart" in isolation.

The goal is to make the entire system capable of accomplishing useful work.

---

# 5. Clients

The same AI backend should support multiple clients.

The main clients are:

- Next.js web application
- React Native / Expo mobile application
- future API clients
- future CLI
- future AI/agent clients

All clients communicate with the same central backend.

The clients should not contain the actual autonomous execution logic.

The backend owns orchestration and execution.

---

# 6. Web Application

The web application provides the primary control panel.

It is responsible for things such as:

- authentication
- dashboard
- agent creation
- agent configuration
- agent management
- chat
- task creation
- task history
- execution monitoring
- screenshots
- file uploads
- artifact access
- integration management
- agent permissions
- settings

The web application communicates with FastAPI.

The web application does not directly control LangGraph or the agent runtime.

---

# 7. Mobile Application

The mobile application uses the same backend as the web application.

Technology:

- React Native
- Expo
- TypeScript
- Expo Router
- Zustand
- React Query

The mobile application is intended to support:

- authentication
- agent management
- chat
- task creation
- file uploads
- image uploads
- execution monitoring
- live status
- screenshots
- generated artifacts
- push notifications
- background task awareness
- reconnection after the application is closed
- offline caching
- deep linking

The mobile application is not a second backend.

It is another client of the same control plane.

---

# 8. FastAPI Control Plane

FastAPI is the central backend/control plane.

It is responsible for coordinating the platform.

Responsibilities include:

- API requests
- authentication integration
- authorization
- user ownership
- agent management
- task management
- execution management
- streaming
- persistence
- integration management
- computer session management
- artifact management
- background execution
- event handling
- observability
- error handling

The backend does not own the authentication User model.

The frontend/authentication system owns the user identity.

The Python backend receives an external `user_id` and uses it to scope AI-owned resources.

---

# 9. User Ownership

The Python backend must not create a duplicate User model.

Authentication belongs to the application authentication layer.

The AI backend uses:

    user_id

to associate resources with the correct user.

User-owned resources include:

- agents
- tasks
- runs
- messages
- tool calls
- computer sessions
- artifacts
- integration connections
- integration permissions
- future user-owned resources

Repositories and services must always respect ownership.

For example:

    get_agent(user_id, agent_id)

    list_agents(user_id)

    get_task(user_id, task_id)

An agent belonging to User A must never be returned to User B.

---

# 10. Agent

An Agent is a first-class domain object.

An Agent represents an AI worker.

An Agent can have:

- identity
- name
- role
- description
- LLM/provider configuration
- model configuration
- available tools
- integration capabilities
- computer capabilities
- memory configuration
- permissions
- execution configuration

The Agent does not itself represent one execution.

An Agent can execute many tasks and can have many runs.

For example:

Research Agent

can execute:

- Research Task A
- Research Task B
- Research Task C

Each task can produce one or more execution runs.

---

# 11. Agent Manager

AgentManager manages collections of agents.

Its responsibilities include:

- registering agents
- finding agents
- removing agents
- listing agents
- coordinating agent lifecycle

It does not perform the agent's reasoning.

It does not execute the autonomous loop.

It does not directly manipulate LangGraph state.

It is a management layer.

---

# 12. Agent Runtime

AgentRuntime is the execution boundary for an Agent.

The Runtime is responsible for turning an Agent and a Task into an actual execution.

Conceptually:

Agent
  ↓
AgentRuntime
  ↓
AgentState
  ↓
LangGraph
  ↓
Execution

The Runtime manages things such as:

- execution state
- step limits
- LLM invocation
- tool execution
- observations
- failures
- execution events
- persistence
- cancellation
- completion

The Runtime is separate from Agent identity.

This allows one Agent configuration to participate in multiple independent runs.

---

# 13. Agent State

AgentState represents temporary state flowing through an execution.

Current core state includes concepts such as:

- user_id
- agent_id
- task_id
- run_id
- prompt
- messages
- current_step
- status
- error

Example execution:

Task
  ↓
AgentState
  ↓
LLM
  ↓
AIMessage
  ↓
AgentState
  ↓
Tool
  ↓
Observation
  ↓
AgentState
  ↓
LLM
  ↓
...

AgentState is runtime state.

It is not a database model.

The state can evolve as new execution capabilities are added.

Future state may include:

- current plan
- tool calls
- observations
- artifacts
- memory retrieval results
- computer state
- execution metadata

Only add state fields when the execution system actually needs them.

---

# 14. LangGraph

LangGraph is the orchestration engine.

The agent is not simply:

    prompt → LLM → response

Instead, execution is represented as a graph.

The initial graph is intentionally simple:

START
  ↓
LLM
  ↓
END

This proves the core pipeline before adding autonomous behavior.

The next stage becomes:

START
  ↓
LLM
  ↓
Does the model request a tool?
  ├── No → END
  │
  └── Yes
       ↓
    Tool Executor
       ↓
    Observation
       ↓
      LLM
       ↓
    Continue / End

Eventually the graph can include:

- planning
- context retrieval
- tool execution
- computer interaction
- memory updates
- artifact creation
- multi-agent delegation
- validation
- retry/recovery

LangGraph controls state transitions.

The LLM does not directly control the entire application.

---

# 15. LLM Layer

The LLM is treated as a replaceable provider.

The architecture uses an LLM provider abstraction with a strict fallback chain:

- **Groq**: Ultra-fast execution and real-time tool calling.
- **Gemini**: Large-context reasoning, multimodal input (PDFs, images), and primary fallback.
- **Mistral**: Robust secondary fallback and alternative reasoning.

The Agent Runtime does not depend directly on any single provider.

Instead:

LLMProvider
  ├── GroqProvider
  ├── GeminiProvider
  └── MistralProvider

This is a Strategy-style architecture.

The graph receives an LLM/provider dependency instead of secretly constructing one.

This makes the execution system provider-independent and resilient to outages.

---

# 16. Provider Manager (Fallback Chain: Groq → Gemini → Mistral)

A Provider Manager sits above individual providers to guarantee execution reliability.

Conceptually:

LLMProvider
  │
  ├── Groq (Primary / Fast Tool Calls)
  │     ↓ (on rate limit or failure)
  ├── Gemini (Large Context / Multimodal / Primary Fallback)
  │     ↓ (on failure)
  └── Mistral (Secondary Fallback)
       ↓
Provider Manager
       ↓
Automatic Routing & Seamless Fallback

The Provider Manager handles:

- automatic provider fallback (`Groq → Gemini → Mistral`)
- multimodal routing (routing image/PDF heavy prompts to Gemini)
- rate-limit handling (429 exponential backoff and failover)
- latency and cost optimization
- provider health checks

If Groq encounters a rate limit or service outage, the execution automatically falls back to Gemini, and then to Mistral. The user's execution run never crashes due to a single vendor failure.


---

# 17. Tool System

Tools represent capabilities that an agent can invoke.

Examples include:

- web search
- browser interaction
- HTTP requests
- file reading
- file writing
- shell execution
- Python execution
- screenshots
- computer actions
- artifact generation
- external application operations

A Tool should have a clear interface and execution contract.

The Agent should not contain tool-specific implementation logic.

---

# 18. Tool Registry

ToolRegistry manages available tools.

Conceptually:

ToolRegistry
  ├── browser_search
  ├── browser_open
  ├── screenshot
  ├── click
  ├── type
  ├── press_key
  ├── read_file
  ├── write_file
  └── ...

The registry is responsible for:

- registration
- discovery
- lookup
- capability exposure

It does not decide what the Agent should do.

The LLM decides whether a tool is useful.

The Tool Executor executes it.

---

# 19. Computer-Use System (Cloud Execution Only)

Computer use in Open Agent AWS is strictly executed in isolated cloud environments.

The platform **does not operate on the user's local machine or personal computer**.

Instead, computer execution is abstracted and runs on managed cloud infrastructure:

Conceptually:

Computer
  └── AWSComputer (EC2 Cloud Environment)

Operations can include:

- screenshot
- click
- type
- press
- scroll
- move
- wait

The architecture is:

Agent
  ↓
AgentRuntime
  ↓
ComputerSession
  ↓
AWSComputer (EC2)

---

# 20. Cloud-Only Isolation (No Local Computer Control)

Open Agent AWS strictly excludes local computer automation:

- The agent has **no access to the user's local machine, laptop, or desktop OS**.
- All interactive browser and application sessions run inside sandboxed cloud environments (AWS EC2 instances).
- This ensures complete user security, data isolation, and guarantees that long-running tasks continue running in the cloud even when the user shuts down their local laptop.


---

# 21. AWS Computer

AWSComputer provides a cloud execution environment.

The computer can run on AWS EC2.

Architecture:

Agent
  ↓
AgentRuntime
  ↓
ComputerSession
  ↓
AWSComputer
  ↓
EC2
  ↓
Browser / Applications / OS

The EC2 instance is infrastructure.

It is not an Agent.

Multiple agents can potentially use the same infrastructure if execution environments are properly isolated through:

- workspaces
- browser contexts
- processes
- permissions
- filesystem boundaries
- session identifiers

---

# 22. Computer-Use Loop

A computer-use workflow follows a perception/reasoning/action loop.

Example:

User:

    "Open the website and find the report."

Agent understands the task.

LLM:

    decide action

Computer:

    click / type / scroll

Computer:

    return screenshot

Vision-capable LLM:

    analyze screenshot

LLM:

    decide next action

Computer:

    perform action

The loop continues until the task is completed, blocked, or fails.

Conceptually:

Screenshot
  ↓
Reasoning
  ↓
Action
  ↓
New Screenshot
  ↓
Reasoning
  ↓
Action
  ↓
...

---

# 23. External Application Integrations

The platform is also designed to connect with applications users already use.

Examples:

- Slack
- Gmail
- GitHub
- Google Drive
- Google Calendar
- Notion
- Discord
- Microsoft Teams
- Jira
- Linear
- Trello
- Asana
- Dropbox
- OneDrive
- other future services

This is a major part of the project's newer direction.

The goal is not merely:

    "AI can control a computer."

The goal is:

    "AI can perform work across the user's existing software ecosystem."

---

# 24. Integrations vs Tools

An Integration represents a connected external service.

A Tool represents a specific capability exposed to an Agent.

For example:

Slack Integration
  ├── search_messages
  ├── read_message
  ├── read_thread
  ├── send_message
  └── create_channel

Gmail Integration
  ├── search_emails
  ├── read_email
  ├── create_draft
  ├── send_email
  └── reply_email

GitHub Integration
  ├── search_repositories
  ├── read_issue
  ├── create_issue
  ├── create_pull_request
  └── comment_on_issue

The Connector communicates with the external service.

The Tool exposes an operation to the Agent.

Architecture:

Agent
  ↓
Tool Registry
  ↓
Integration Tool
  ↓
Connector
  ↓
External API

---

# 25. Integration Manager

IntegrationManager manages external service connections.

It is responsible for concepts such as:

- available integrations
- user connections
- connection status
- provider identity
- capabilities
- integration permissions
- connection lifecycle

The manager does not contain the business logic of every external API.

Each provider has its own connector implementation.

---

# 26. User Integration Connections

A user can connect external applications such as Google Docs, Google Drive, Gmail, Slack, and GitHub.

Example:

User:

    Google Docs  → not connected
    Google Drive → not connected
    Slack        → connected
    Gmail        → connected
    GitHub       → connected

The platform persists connection metadata and OAuth state per user.

### Interactive Connection State Check & Prompt

When a user instructs the Chat Agent to perform a task requiring an external service (for example: *"Research AI market trends for 5 days and write the final report in my Google Docs"*):

1. **Pre-execution Verification**:
   The Chat Agent inspects the user's connection status for Google Docs.
2. **If Not Connected**:
   The agent pauses execution and proactively prompts the user in chat:
   > *"Google Docs is not connected yet. Please connect your Google account so I can create and write the report for you [Connect Google Docs Button / OAuth Link]."*
3. **Once Connected**:
   The agent detects the valid connection, confirms the planned execution to the user, and initiates the background task.
4. **Agent-Level Permission Scoping**:
   Even when an integration is connected, access is granted strictly per-agent (an agent only receives the specific tools it needs).


---

# 27. OAuth and Credentials

External applications commonly use OAuth.

Typical flow:

User
  ↓
Connect Application
  ↓
OAuth Provider
  ↓
Authorization
  ↓
Callback
  ↓
Backend
  ↓
Secure Credential Storage
  ↓
Integration Connection

Credentials are security-sensitive.

The Agent must never receive raw OAuth credentials as normal prompt/context data.

The integration layer handles authentication.

The Agent receives capabilities such as:

    "Slack: search messages"

not:

    "Here is the user's Slack token."

---

# 28. Integration Permissions

Connecting an application does not automatically give every Agent unlimited access.

Permission hierarchy:

User
  ↓
Integration
  ↓
Agent
  ↓
Tool
  ↓
Operation

Example:

User connects Gmail.

Agent A:

    read email

Agent B:

    read email
    create drafts

Agent C:

    read email
    send email

Permissions must be explicit.

Read and write capabilities should be distinguishable.

High-impact operations may require user confirmation depending on the configured security policy.

---

# 29. API Automation vs Computer Automation

The platform supports two ways of interacting with external applications.

### API-based

When an API provides the required capability:

Agent
  ↓
Integration
  ↓
API
  ↓
Result

### Computer-based

When the API does not provide the required capability:

Agent
  ↓
Computer
  ↓
Browser
  ↓
Website
  ↓
Action

The Agent can therefore choose the appropriate execution mechanism.

---

# 30. Hybrid Workflows

A single task can combine integrations and computer use.

Example:

    "Check Slack for the customer's request,
     update the GitHub issue,
     then open the staging website and verify
     the fix."

Execution:

Slack API
  ↓
Read request
  ↓
GitHub API
  ↓
Update issue
  ↓
AWS Computer
  ↓
Browser
  ↓
Test staging website
  ↓
Screenshot
  ↓
Agent
  ↓
Final report

This is one of the central goals of the platform.

---

# 31. Multi-Agent Architecture & Dynamic Agent Creation

The platform supports multiple specialized Agents that can be created dynamically.

### Dynamic Multi-Agent Creation:
- **Created by User**: The user can create multiple agents via chat or the dashboard for different tasks, assigning each agent specific roles, instructions, and restricted toolsets.
- **Created by Chat Agent**: The Chat Agent itself can dynamically spin up specialized worker agents when complex workflows require dedicated capabilities.

Example Worker Agents:

Chat Agent (Front-Facing Coordinator)
  ├── Market Research Agent (Tools: Web Search, Read File)
  ├── Document Intelligence Agent (Tools: PDF Parser, Image Analyzer)
  ├── Report Generator Agent (Tools: Google Docs Connector, Drive Access)
  └── Communications Agent (Tools: Slack Connector, Gmail Sender)

Each Agent has strictly scoped:

- roles and custom instructions
- assigned tools (no single agent has unrestricted access to all tools)
- integration permissions
- fallback model configuration (`Groq → Gemini → Mistral`)
- memory and artifact access

---

# 32. Conversational Chat Agent

The primary interface for the user is a friendly, front-facing **Chat Agent** (serving as the conversational coordinator rather than an overly abstract academic supervisor).

The user speaks directly with the Chat Agent. Its responsibilities include:

1. **Conversational Interface**: Interacting with the user, clarifying goals, and understanding requirements.
2. **Dynamic Agent Creation**: Creating new specialized worker agents when needed.
3. **Task Delegation & Coordination**: Assigning tasks to working agents and passing necessary context.
4. **Integration Pre-Checks**: Inspecting whether required external tools (like Google Docs) are connected, and prompting the user if authorization is needed.
5. **Progress Reporting & Notifications**: Updating the user on background work and sending notifications when multi-day tasks complete.

Operations include:

- `create_worker_agent`
- `delegate_task`
- `send_instruction`
- `inspect_agent_status`
- `request_result`
- `prompt_user_for_integration`

---

# 33. Agent Collaboration & Real-World Workflows

Example: 5-Day Autonomous Research & Google Docs Reporting

User
  ↓ (Prompt: "Research this market every day for 5 days and write the report in Google Docs")
Chat Agent
  ↓ (Pre-check: Google Docs connected? Prompt user if not)
Market Research Agent (Runs daily web/document research)
  ↓ (Findings gathered across 5 days)
Document Intelligence Agent (Synthesizes PDFs, findings, and charts)
  ↓ (Draft report)
Report Generator Agent (Appends final report into user's Google Doc)
  ↓ (Report URL generated)
Chat Agent
  ↓ (Dispatches completion notification)
User: "Your 5-day market report is ready in your Google Doc: [Link]"

---

# 34. @agent Routing

Users can explicitly target specific working agents using `@agent` tags:

Examples:

    @research-agent investigate this topic
    @document-agent summarize this uploaded PDF
    @report-agent create the weekly executive Google Doc

The chat layer detects the tag and routes the task directly to that specific agent.

If the user does not specify an `@agent` tag, the main Chat Agent handles the conversation, determines whether to answer directly, creates a new worker, or delegates to an existing agent.


---

# 35. Event-Driven Agents

The long-term platform also supports external events.

Examples:

- new Gmail email
- new Slack message
- GitHub pull request opened
- GitHub issue created
- calendar event approaching
- external webhook
- file uploaded

Potential flow:

External Application
  ↓
Webhook
  ↓
FastAPI
  ↓
Event Router
  ↓
Agent / Workflow
  ↓
Task
  ↓
Run

This allows Agents to become proactive rather than only responding to manually submitted prompts.

---

# 36. Cross-Application Automation

A major goal is to allow one task to span multiple applications.

Example:

    "Check my important emails,
     look for related Slack discussions,
     find the related GitHub issue,
     update the issue,
     notify the team in Slack,
     and schedule a follow-up meeting."

Potential execution:

Gmail
  ↓
Find relevant email
  ↓
Slack
  ↓
Find context
  ↓
GitHub
  ↓
Find/update issue
  ↓
Slack
  ↓
Notify team
  ↓
Calendar
  ↓
Create event
  ↓
Final result

The system is therefore an orchestration layer across applications rather than a collection of isolated integrations.

---

# 37. Database

The AI backend uses PostgreSQL through Neon.

Technology:

- Neon PostgreSQL
- SQLAlchemy 2.x
- asyncpg
- Alembic

PostgreSQL stores structured application state.

Important entities include:

- Agents
- Tasks
- Agent Runs
- Messages
- Tool Calls
- Computer Sessions
- Artifacts
- Integration Connections
- future persistence entities only when required

The database is not intended to store everything.

It stores durable structured state.

---

# 38. Database Ownership Model

Every user-owned AI resource should contain:

    user_id

The database does not contain a local User table owned by this backend.

The ownership chain is conceptually:

User
  ↓
Agent
  ↓
Task
  ↓
Run
  ↓
Messages / Tool Calls / Artifacts

And:

User
  ↓
Integration Connection
  ↓
Agent Permissions
  ↓
Integration Tools

Ownership must be enforced by the repository/service layer.

---

# 39. Core Database Entities

### Agent

Stores the persistent representation of an Agent.

### Task

Represents a user-requested unit of work.

### Agent Run

Represents one execution attempt of a task.

### Message

Stores durable execution conversation/history.

### Tool Call

Stores tool execution history and results.

### Computer Session

Represents the execution environment used for computer interaction.

### Artifact

Stores metadata for generated/uploaded files.

### Integration Connection

Represents a user's connection to an external service.

The actual design may evolve as implementation grows.

Do not create tables merely because a future concept exists.

---

# 40. PostgreSQL vs Qdrant vs S3

The platform deliberately separates storage responsibilities.

PostgreSQL:

    structured state
    metadata
    ownership
    execution history

Qdrant:

    vector embeddings
    semantic memory
    retrieval

S3:

    actual file/artifact bytes

The distinction is:

PostgreSQL:
    "What happened?"

Qdrant:
    "What information is semantically relevant?"

S3:
    "Where are the actual bytes?"

---

# 41. Memory

Agents can eventually maintain persistent semantic memory.

Memory is not simply the entire database.

A memory pipeline can be:

Input
  ↓
Chunking
  ↓
Embedding
  ↓
Qdrant
  ↓
Semantic Retrieval
  ↓
Relevant Context
  ↓
Agent
  ↓
LLM

The Agent should retrieve relevant information instead of dumping every historical interaction into the prompt.

---

# 42. RAG

RAG is used for knowledge retrieval.

Example:

Document
  ↓
Parser
  ↓
Chunker
  ↓
Embedding Model
  ↓
Qdrant
  ↓
Similarity Search
  ↓
Relevant Chunks
  ↓
Agent Context
  ↓
LLM

The system should treat uploaded knowledge as reusable context rather than one-time prompt content.

---

# 43. Files as First-Class Inputs (PDF & Image Intelligence)

The system supports files as first-class Agent inputs, with primary focus on **PDFs, images, spreadsheets, and text documents**.

Supported formats:

- **PDF**: Document parsing, text extraction, research papers, financial reports, invoices.
- **Images (PNG, JPG, WEBP)**: Diagrams, screenshots, charts, scanned receipts (routed to multimodal models like Gemini).
- **Documents & Spreadsheets**: DOCX, CSV, XLSX, Markdown, JSON, HTML, TXT.

Files are represented as artifacts.

The system can:

- parse and extract text/tables from PDFs
- feed images directly into multimodal LLMs (e.g. Gemini) for visual analysis
- chunk and embed document content for semantic retrieval
- synthesize multi-document findings into unified reports (e.g. in Google Docs)

Parsing is handled by dedicated tool components (`PDFReaderTool`, `ImageReaderTool`), never hardcoded inside the `Agent` class.

---

# 44. Artifact System

Artifacts represent uploaded or generated files.

Examples:

- PDFs
- reports
- images
- spreadsheets
- screenshots
- generated documents
- logs

PostgreSQL stores artifact metadata.

S3 stores the actual bytes.

Conceptually:

Artifact Metadata
  ↓
PostgreSQL

Artifact Bytes
  ↓
S3

---

# 45. Task Lifecycle & Multi-Day Scheduled Execution

Tasks can be immediate single runs or **multi-day scheduled / recurring workflows**.

Example multi-day workflow:
> *"Research AI market trends every day for 5 days, compile findings, and write the final report into my Google Docs."*

The Task entity tracks the long-running schedule, spawning daily execution runs and keeping track of cumulative progress across days.

A task may move through states such as:

PENDING
  ↓
RUNNING (Daily recurring steps)
  ↓
COMPLETED (Final report created & user notified)

or:

PENDING
  ↓
RUNNING
  ↓
FAILED

Additional states include: `PAUSED`, `CANCELLED`, `BLOCKED`, `WAITING`, `TIMEOUT`.

---

# 46. Execution Runs

A Task represents what the user wants.

A Run represents an execution attempt.

Example:

Task:

    "Research this company for 5 days."

Run 1 (Day 1):
    completed daily research

Run 2 (Day 2):
    completed daily research

The system preserves meaningful execution history instead of overwriting previous state.

---

# 47. Real-Time Updates & Proactive Completion Notifications

Long-running and multi-day Agents require both real-time streaming and proactive notifications upon completion.

### Real-Time Streaming:
- current Agent status & step
- model thinking output
- tool invocations & observations
- artifacts generated

### Proactive Completion Notifications:
When a long-running or multi-day scheduled task reaches `COMPLETED`:
- The Chat Agent automatically dispatches a notification to the user.
- Notification message: *"Your 5-day market report is ready in your Google Doc: [Link to Google Doc]"*.
- Channels: Chat interface, push notification, email, or Slack depending on user configuration.


---

# 48. Reliability

The platform is designed for autonomous execution, so reliability is important.

Mechanisms include:

- timeouts
- retries
- exponential backoff
- provider fallback
- execution step limits
- task cancellation
- failure recovery
- state persistence
- checkpoints
- idempotency where required

An Agent must not be allowed to execute forever simply because the LLM continues producing actions.

---

# 49. Error Handling

The project uses explicit exception categories.

Examples:

OpenAgentError
  ├── ConfigurationError
  ├── AgentError
  ├── ToolError
  └── ComputerError

Errors should be handled at the layer that has enough context to decide what to do.

Examples:

Configuration failure:
    fail immediately

Temporary provider failure:
    retry or fallback

Tool failure:
    return the failure as an observation when appropriate

Computer failure:
    retry / reconnect / fail

Task failure:
    persist failure state and notify the client

Do not use broad silent exception handling.

Do not hide failures from the execution system.

---

# 50. Security Model

The Agent should not automatically have unrestricted access.

Capabilities must be permission-aware.

Security should consider:

- user ownership
- Agent permissions
- tool permissions
- integration permissions
- computer permissions
- filesystem isolation
- command restrictions
- API authentication
- authorization
- secret handling
- OAuth scopes
- rate limits
- execution timeouts
- resource limits
- environment isolation

Especially for computer use and external integrations, permissions must be explicit.

---

# 51. High-Impact Actions

Some operations can have real-world consequences.

Examples:

- sending an email
- sending a Slack message
- deleting a file
- modifying a GitHub repository
- creating a pull request
- changing calendar events
- executing shell commands
- interacting with external systems

The platform should distinguish between:

READ

and:

WRITE / HIGH-IMPACT

Depending on the Agent configuration and operation, high-impact actions may require explicit user confirmation.

The Agent should not silently perform dangerous or irreversible actions merely because an LLM decided to do so.

---

# 52. Observability

The platform should provide enough information to understand what happened during an execution.

Important identifiers include:

- user_id
- agent_id
- task_id
- run_id
- tool_call_id
- computer_session_id
- artifact_id
- integration_connection_id

Important telemetry includes:

- execution steps
- model calls
- latency
- provider
- tool usage
- retries
- failures
- computer actions
- integration operations
- generated artifacts

The system should make debugging possible.

Questions such as:

    "Why did this task fail?"

    "Which tool did the Agent call?"

    "Which LLM provider was used?"

    "Which computer executed the task?"

    "Which Slack connection was used?"

should be answerable from execution data.

---

# 53. Design Patterns

The project uses design patterns intentionally.

### Strategy

Used for LLM providers.

LLMProvider
  ├── GroqProvider
  ├── GeminiProvider
  └── MistralProvider

### Repository

Used for persistence.

AgentRepository
TaskRepository
RunRepository
...

### Adapter

Used for cloud computer implementations.

Computer
  └── AWSComputer (EC2)


### Dependency Injection

Dependencies are passed into components.

For example:

AgentRuntime
    receives Agent / provider / tools / computer

The graph should receive its provider rather than constructing a Groq provider internally.

### State Machine

Used for task and execution lifecycle.

### Factory

Use only when object creation actually becomes complex.

The project should not add patterns just to appear sophisticated.

---

# 54. Current Development Philosophy

The project is being developed incrementally.

The architecture is designed first, then implemented in vertical slices.

Do not build every future feature at once.

A feature should become part of the architecture when it is actually implemented.

Examples:

Do not create a giant database schema for hypothetical future features.

Do not create Slack code before the integration architecture is ready.

Do not build multi-agent coordination before the single-agent execution loop works.

Do not build computer-use orchestration before basic tool calling works.

The core execution path should become reliable before expanding it.

---

# 55. Current Development Progress

The project has already established the initial backend foundation.

Implemented concepts include:

- FastAPI application
- application configuration
- environment settings
- application lifecycle
- logging
- custom exceptions
- LLM provider abstraction
- Groq provider
- Agent class
- AgentManager
- AgentRuntime
- Tool abstraction
- AgentState
- database foundation
- PostgreSQL/Neon architecture
- SQLAlchemy architecture
- Alembic migration architecture

The LLM layer has already been validated with a successful Groq invocation.

The AgentState has been established as the runtime state flowing through future LangGraph execution.

The next core execution layer is the LangGraph graph.

---

# 56. Current Execution Milestone

The immediate execution path is:

Task
  ↓
Agent
  ↓
AgentRuntime
  ↓
AgentState
  ↓
LangGraph
  ↓
LLM
  ↓
AIMessage
  ↓
Completed State

The first LangGraph version is intentionally simple:

START
  ↓
LLM
  ↓
END

This is the foundation for the future autonomous loop.

---

# 57. Immediate Next Execution Stage

After the basic LLM graph works, the system will become:

START
  ↓
LLM
  ↓
Tool requested?
  ├── No → END
  │
  └── Yes
       ↓
    Tool Executor
       ↓
    Observation
       ↓
      LLM
       ↓
    Continue / END

This will be the first genuine agent loop.

After that, capabilities can progressively be added.

---

# 58. Planned Development Progression

The intended progression is:

1. Database foundation
2. AgentState
3. Basic LangGraph execution
4. LLM node & Multi-provider fallback engine (Groq → Gemini → Mistral)
5. Tool-calling loop
6. Tool executor
7. Tool registry & First real tools
8. Persistence of execution (PostgreSQL run history)
9. Dynamic Agent Creation & Agent Registry
10. Document intelligence (PDF & multimodal image processing via Gemini)
11. External integrations (Google Docs, Drive, Slack, Gmail, GitHub)
12. Interactive integration authentication checks
13. Conversational Chat Agent & Worker Coordination
14. Multi-day autonomous scheduling & user notifications
15. AWS EC2 Cloud Computer (Cloud-Only, No Local Computer)
16. Computer-use perception/action loop
17. Artifact system & AWS S3 storage
18. Qdrant semantic memory & RAG
19. Web control panel (Next.js)
20. Mobile application (React Native / Expo)
21. Production reliability, Sentry observability & security hardening

This order may change as implementation reveals better dependencies, but the core principle remains:

Build the execution engine first, then progressively expand its capabilities.

---

# 59. Example: Simple Agent Task

User:

    "Summarize this document."

Flow:

User
  ↓
FastAPI
  ↓
Task
  ↓
Agent
  ↓
AgentRuntime
  ↓
LangGraph
  ↓
LLM
  ↓
Result
  ↓
Artifact / Response
  ↓
User


---

# 60. Example: Tool-Using Agent

User:

    "Search the web for information about X."

Flow:

User
  ↓
Task
  ↓
AgentRuntime
  ↓
LangGraph
  ↓
LLM
  ↓
Tool Call
  ↓
Web Search Tool
  ↓
Observation
  ↓
LLM
  ↓
Final Answer


---

# 61. Example: Computer-Use Agent

User:

    "Open the website and download the report."

Flow:

User
  ↓
Task
  ↓
AgentRuntime
  ↓
LangGraph
  ↓
LLM
  ↓
AWSComputer
  ↓
Browser
  ↓
Screenshot
  ↓
Vision / LLM
  ↓
Next Action
  ↓
Download
  ↓
Artifact
  ↓
S3
  ↓
User


---

# 62. Example: External Application Workflow

User:

    "Find the latest customer request in Slack
     and create a GitHub issue for it."

Flow:

User
  ↓
Chat Agent (Coordinator)
  ↓
Slack Integration
  ↓
Search Messages
  ↓
Read Relevant Thread
  ↓
GitHub Integration
  ↓
Create Issue
  ↓
Persist Tool Calls
  ↓
Return Result


---

# 63. Example: Complex Cross-Application Workflow

User:

    "Check my important emails, find related Slack
     conversations, update the relevant GitHub issue,
     verify the staging website, and send me a report."

Possible execution:

Chat Agent (Coordinator)
  ↓
Gmail Agent / Integration
  ↓
Slack Integration
  ↓
GitHub Integration
  ↓
AWS Computer (EC2)
  ↓
Browser
  ↓
Screenshot / Verification
  ↓
Report Generation
  ↓
Artifact
  ↓
S3
  ↓
Chat Agent
  ↓
User


This is the type of workflow the complete platform is designed to support.

---

# 64. What This Project Ultimately Represents

Open Agent AWS is best understood as an:

> Autonomous AI execution and orchestration platform.

It combines:

- AI agents
- LLMs
- tool calling
- computer use
- cloud computers
- external application integrations
- multi-agent systems
- semantic memory
- RAG
- files
- artifact generation
- persistent execution state
- event-driven automation
- real-time execution
- web
- mobile
- cloud infrastructure

into one system.

It is not a collection of unrelated features.

Every capability exists to increase what an Agent can safely and reliably accomplish.

---

# 65. The Core Architecture in One View

                         USER
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
          NEXT.JS       MOBILE        API/CLI
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                    FASTAPI CONTROL PLANE
                           │
             ┌─────────────┼─────────────────┐
             │             │                 │
             ▼             ▼                 ▼
        AGENT SYSTEM   INTEGRATIONS      TASK SYSTEM
             │             │                 │
             │       ┌─────┼─────┐           │
             │       ▼     ▼     ▼           │
             │     Slack Gmail GitHub        │
             │                               │
             ▼                               ▼
        AGENT RUNTIME                    PostgreSQL
             │
          LangGraph
             │
       ┌─────┼───────────────┐
       ▼     ▼               ▼
      LLM   TOOLS         COMPUTER
       │                     │
       │              ┌──────┴──────┐
       │              ▼             ▼
       │           LOCAL          AWS EC2
       │
       └──────────────┬────────────────┐
                      ▼                ▼
                   MEMORY           ARTIFACTS
                      │                │
                   Qdrant              S3


---

# 66. Final Principle

The most important architectural principle of Open Agent AWS is:

    The LLM is not the product.

The LLM provides reasoning.

The platform provides:

    identity
    state
    orchestration
    tools
    integrations
    computers
    memory
    storage
    permissions
    persistence
    reliability
    observability
    clients
    cloud infrastructure

Together, these turn an LLM into an actual autonomous software system.

The final goal is an AI platform where a user can give an Agent a real-world objective and the platform can safely coordinate whatever capabilities are necessary to accomplish it.

That can mean:

    reasoning
        +
    API calls
        +
    browser interaction
        +
    computer control
        +
    external applications
        +
    files
        +
    memory
        +
    other Agents
        +
    cloud infrastructure

all inside one controlled execution system.

Open Agent AWS is therefore fundamentally an **AI execution platform**, not merely an AI chatbot.

---

# 67. Detailed Architectural Specifications

## 67.1 AI-Assisted Development Principles
This project is developed with the help of AI coding agents, but AI-generated code must follow the architecture and engineering rules defined across this repository.

AI acts as an implementation assistant, not as the system architect.

Before implementing any feature:
1. Understand the existing architecture.
2. Inspect the relevant files.
3. Reuse existing abstractions where appropriate.
4. Avoid creating duplicate systems.
5. Preserve established naming and folder conventions.
6. Update documentation when an architectural decision changes.
7. Never claim a feature is implemented when only scaffolding exists.

Critical systems such as agent execution, LangGraph orchestration, tool calling, computer control, permissions, integrations, persistence, and distributed execution must remain understandable and reviewable by the project owner.

---

## 67.2 Architectural Boundaries
The following concepts must remain separate unless there is a clear architectural reason to combine them:
- API layer
- Agent system
- Agent runtime
- Agent state
- LangGraph orchestration
- LLM providers
- Tools
- Tool registry
- Integrations
- Connectors
- Computer implementations
- Memory
- Database persistence
- Artifact storage
- Authentication
- Observability
- Task execution
- Background workers

These boundaries exist to prevent the project from becoming a monolithic AI script. The goal is a modular AI execution platform rather than a single chatbot application.

---

## 67.3 Authentication and Identity
Authentication is handled through **Clerk**.
- The web application and mobile application use Clerk as the shared identity provider.
- The Python backend does not maintain a separate user authentication system.
- The backend receives and verifies the authenticated user's identity and uses the external Clerk `user_id` as the ownership identifier.
- User-owned resources in the database reference the external user identity (`user_id`) rather than creating a separate local user table.

---

## 67.4 Frontend Architecture
The web control panel uses:
- **Next.js** (App Router)
- **TypeScript** (Strict mode)
- **Tailwind CSS** & **shadcn/ui**
- **Zustand** (Client/application state)
- **TanStack Query** (Server state, caching, loading, mutations, API sync)
- **Clerk** (Authentication)

Responsibilities:
- Use Zustand strictly for client UI state.
- Use TanStack Query for server state and API synchronization.
- Dedicated API client modules for backend communication.
- Feature-specific components for feature behavior; shared components only for genuinely reusable UI.
- Strict typing with no `any`.

---

## 67.5 Mobile Architecture
The mobile client uses:
- **React Native** & **Expo** (Expo Router)
- **TypeScript**
- **NativeWind**
- **Zustand** & **TanStack Query**
- **Clerk**

The mobile application communicates with the same backend control plane as the web application. Both clients share:
- Authentication identity
- API contracts
- Agent, task, and execution concepts
- Integration and permission semantics

---

## 67.6 Agent Architecture & Boundaries
An Agent represents an autonomous worker capability. An Agent should not directly own:
- Database persistence
- HTTP request handling
- Authentication
- Computer infrastructure
- Integration credentials
- Application-wide orchestration

An Agent relies on:
- An LLM provider (via Strategy abstraction)
- Registered tools
- Memory systems
- Integrations (via Connectors and Tools)
- Computer session (via Computer abstraction)
- Temporary runtime state (`AgentState`)

The `Agent` defines behavior and configuration. The `AgentRuntime` executes runs. `LangGraph` orchestrates state transitions.

---

## 67.7 LLM Providers & Provider Fallback
LLMs are providers, not agents. The system uses a provider abstraction with a strict three-tier fallback chain: **Groq → Gemini → Mistral**.
- **Groq**: Primary provider for ultra-fast generation and tool-calling.
- **Gemini**: Large context, native PDF and image/multimodal comprehension, and primary fallback.
- **Mistral**: Secondary fallback guaranteeing uninterrupted execution.

Provider fallback is handled at the provider/routing layer:
```text
Groq (Primary)
     ↓ (failure / 429 rate limit)
Gemini (Multimodal & Primary Fallback)
     ↓ (failure)
Mistral (Secondary Fallback)
     ↓
Continue Execution (Zero Crashes)
```

---

## 67.8 Agent Fallback vs. LLM Fallback
Agent fallback is separate from LLM provider fallback:
- **LLM Provider Fallback**: Swaps the model/provider when a provider fails or experiences rate limits.
- **Agent Fallback**: Reassigns the task to an alternate agent when the primary agent cannot fulfill the task.

Example:
```text
Chat Agent
    │
    ├── Market Research Agent
    │
    └── Fallback Research Agent
```
Agent fallback only occurs if the alternate agent possesses the required capabilities, tools, integrations, permissions, and execution environment.

---

## 67.9 Tools
Tools are executable capabilities exposed to agents. Every tool adheres to the common `Tool` abstraction:
- Stable names and clear descriptions
- Validated inputs (e.g. via Pydantic)
- Controlled execution and explicit errors
- Permission checks where required
- Observable execution telemetry

Tools perform a single specific capability (e.g., `web_search`, `read_file`, `write_file`, `parse_pdf`, `google_docs_create`, `google_docs_append`, `slack_send`).

---

## 67.10 Integrations and Connectors
- **Integration**: Represents a user connection to an external service (Google Docs, Google Drive, Slack, Gmail, GitHub).
- **Connector**: Handles low-level communication and API calls with that service.
- **Tool**: Exposes a specific operation to the Agent.

Hierarchy:
```text
Integration (OAuth / User Auth State)
    ↓
Connector (API Client)
    ↓
Tool (Agent Capability)
    ↓
Agent
```
Raw access tokens are stored securely and never passed to the LLM prompt or generic metadata. If an integration is not connected, the Chat Agent prompts the user interactively before proceeding.

---

## 67.11 Computer Abstraction (Cloud Execution Only)
Computer interaction is abstracted and runs strictly on AWS EC2 cloud infrastructure:
```text
Agent
  ↓
Computer Interface
  ↓
AWSComputer (EC2 Cloud Environment)
```
Open Agent AWS strictly avoids controlling the user's local machine or personal computer. All interactive browser and application sessions run inside sandboxed cloud environments.

---

## 67.12 Distributed Execution
Open Agent AWS uses a centralized control-plane architecture with distributed execution:
```text
Clients (Web / Mobile / API)
   ↓
FastAPI Control Plane
   ↓
Task / Agent Scheduler
   ↓
Execution Worker
   ↓
Agent Runtime
```
The control plane tracks tasks, ownership, status, permissions, and available environments. Workers execute workloads without becoming the source of truth for application state.

---

## 67.13 Database and Runtime Separation
- **SQLAlchemy Models**: Persistence schemas for PostgreSQL (Neon).
- **Domain/Runtime Objects**: Represent active application behavior.

Pattern:
```text
Database Model
      ↓
  Repository
      ↓
Domain/Runtime Object
```
Database models must never be used directly as runtime Agent, Tool, Computer, or LLM abstractions.

---

## 67.14 Storage & Memory Separation
- **PostgreSQL (Neon)**: Structured persistent application and execution state (agents, tasks, runs, tool calls, messages).
- **Qdrant**: Vector embeddings, similarity search, and semantic RAG memory.
- **S3**: Raw binary files, PDFs, images, downloads, and generated artifacts.

---

## 67.15 Conversational Chat Agent & Dynamic Worker Creation
The Chat Agent is the primary conversational interface and coordinator for the user:
```text
                           Chat Agent
                 (Front-Facing Coordinator)
                             │
     ┌───────────────────────┼───────────────────────┐
     ▼                       ▼                       ▼
Market Research Agent   Document Agent       Report Generator Agent
     │                       │                       │
Web Search / Scraper    PDF Parser / Vision   Google Docs / Drive
```
The user or the Chat Agent can dynamically spin up new specialized working agents on the fly, with custom roles and restricted toolsets.

---

## 67.16 Agent Mentions (`@agent`) & Event-Driven Routing
- Explicit user targeting via `@agent` syntax (e.g., `@research-agent`, `@document-agent`) routes tasks directly to specific agents.
- External webhooks (GitHub, Slack, Gmail, Calendars, scheduled jobs) trigger event handlers that create tasks and dispatch them through the standard runtime pipeline.

---

## 67.17 Error Handling Hierarchy
Custom exception hierarchy rooted in `OpenAgentError`:
- `ConfigurationError`: Invalid setups or missing critical configurations.
- `AgentError`: Agent execution or state errors.
- `ToolError`: Tool execution failures.
- `ComputerError`: Environment, connectivity, or cloud computer failures.

---

## 67.18 Observability & Sentry
Full visibility across runs, execution steps, LLM calls, tool invocations, cloud actions, errors, and latency. Logging is paired with **Sentry** across frontend, mobile, and backend.

---

## 67.19 Security & High-Impact Operations
- Never expose API keys, OAuth tokens, or secrets to prompts.
- Distinguish **READ** actions from **WRITE / HIGH-IMPACT** actions (sending emails, modifying Google Docs, executing cloud commands).
- High-impact operations enforce permission checks and require user confirmation where configured.

---

## 67.20 Engineering Progression Order
The project is built strictly layer-by-layer from working primitives:
```text
Database Foundation (Neon PostgreSQL)
        ↓
Agent State & LangGraph Tool Loop
        ↓
Agent Runtime & Run Persistence
        ↓
Model Fallback Engine (Groq → Gemini → Mistral)
        ↓
Dynamic Agent Creation & Tool Scoping
        ↓
Document Intelligence (PDF & Multimodal Image Processing)
        ↓
External Connectors (Google Docs, Drive, Slack, Gmail)
        ↓
Interactive Connection Auth Checks & Prompts
        ↓
Conversational Chat Agent Coordination
        ↓
Multi-Day Scheduled Workflows & Completion Notifications
        ↓
AWS EC2 Cloud Computer (Cloud-Only)
        ↓
S3 Artifacts & Qdrant Semantic Memory
        ↓
Web & Mobile Control Plane (Next.js & Expo)
        ↓
Production Reliability & Sentry
```


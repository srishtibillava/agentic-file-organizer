# Agentic File Organizer

An autonomous, local file management agent built with **LangGraph** and **Ollama (Qwen 2.5)**. It translates natural language requests into real system actions, enforces human-in-the-loop safety for high-risk operations, and self-heals when actions fail.

## 🌟 Key Features

- **Stateful Workflow:** 4-node pipeline (`planner` → `inspector` → `executor` → `self_heal`).
- **Human-in-the-Loop Safety:** Scans for high-risk operations (e.g., file deletion) and prompts for explicit user approval (`yes`/`no`).
- **Real File Operations:** Directly interacts with your local disk using Python's `os` and `shutil`.
- **Self-Healing Loop:** Gracefully recovers from errors or rejected permissions by re-planning alternative steps without crashing.
- **100% Local & Free:** Powered locally by Qwen 2.5 via Ollama with zero API latency or data exposure.

## 🛠️ Architecture

```text
[ User Request ] ──► [ Planner ] ──► [ Inspector ] ──► [ Executor ]
                                          │                 │
                                  (Requires Approval)    (On Error)
                                          │                 │
                                          ▼                 ▼
                                   [ User Prompt ]   [ Self-Heal ]

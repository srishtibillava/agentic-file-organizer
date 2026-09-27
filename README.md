=# Agentic File Organizer

An autonomous, local file management agent built with **LangGraph and Ollama (Qwen 2.5)**. It translates natural language requests into real system actions, enforces **human-in-the-loop safety for high-risk operations**, and self-heals when actions fail.

## 🌟 Key Features

- **Stateful Workflow:** 4-node pipeline (`planner` → `inspector` → `executor` → `self_heal`).
- **Human-in-the-Loop Safety:** Scans for high-risk operations (e.g., file deletion) and prompts for explicit user approval (`yes/no`).
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
```

## 📸 Execution & Proof of Concept

Below is an example execution showing the agent creating an action plan, enforcing human approval, and successfully running file system commands:

```text
🤖 AGENT INITIALIZED: File Management System

[PLANNER NODE]: Generating dynamic action sequence...

Plan Generated:
1. Create directory: 'Projects/Organized'
2. Move file: 'report.pdf' -> 'Projects/Organized/report.pdf'
3. Delete file: 'Projects/temp_draft.txt'

[INSPECTOR NODE]: Evaluating risk levels...
⚠️ High-risk action detected: Delete file 'Projects/temp_draft.txt'

[HUMAN-IN-THE-LOOP]: Do you approve high-risk actions? (yes/no): yes

[EXECUTOR NODE]: Executing planned operations...
- [SUCCESS] Created folder: Projects/Organized
- [SUCCESS] Moved: report.pdf -> Projects/Organized/report.pdf
- [SUCCESS] Deleted: Projects/temp_draft.txt

✅ TASK COMPLETE: All operations executed successfully.
```

## 💻 Running the Streamlit Interface

1. **Start Ollama** (ensure your local model is active):
```bash
   ollama run qwen2.5:7b-instruct
```

2. **Launch the Streamlit App:**
```bash
   streamlit run stream.py
```

3. Open [http://localhost:8501](http://localhost:8501) in your browser.

### 🖥️ Streamlit Interactive Features

- **Visual Safety Alerts:** When high-risk operations (e.g., file deletions) are detected, execution pauses and displays a dynamic ⚠️ **[SAFETY ALERT]** banner in the UI.
- **One-Click State Resume:** Approve or reject pending operations with single-click buttons that seamlessly resume LangGraph execution (`Command(resume=...)`).
- **Real-Time Log Updates:** Watch status messages and graph node transitions update live as actions execute in your sandboxed workspace.
import json
import os
import shutil
from typing import List, TypedDict, Literal
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END

# Define base working directory
BASE_DIR = os.path.join(os.getcwd(), "demo_workspace")

# ==================================================
# 1. Initialize Local LLM Model
# ==================================================
llm = ChatOllama(model="qwen2.5:7b-instruct", temperature=0)


# ==================================================
# 2. Define Shared Graph State
# ==================================================
class OrganizerState(TypedDict):
    user_request: str
    proposed_actions: List[dict]
    needs_approval: bool
    user_approved: bool
    execution_logs: List[str]
    has_errors: bool
    retries: int


# ==================================================
# 3. Define Nodes
# ==================================================

def planner_node(state: OrganizerState):
    """Parses natural language request into a structured JSON execution plan."""
    print("\n--- Stage: planner ---")
    system_prompt = """
    You are an AI File Organizer. Break down the user's request into a JSON array of actions.
    Each action must strictly follow this JSON schema:
    {
      "action": "create_folder" | "move_file" | "delete_file",
      "target": "filename or folder name",
      "destination": "destination folder name or empty string",
      "risk_level": "LOW" | "HIGH"
    }
    Classify 'delete_file' as 'HIGH' risk_level. All other operations are 'LOW'.
    Respond ONLY with valid JSON inside a raw list block. No markdown formatting or extra text.
    """
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=state["user_request"])
    ])
    
    cleaned_content = response.content.strip().replace("```json", "").replace("```", "").strip()
    actions = json.loads(cleaned_content)
    
    print(f"Plan: {json.dumps(actions, indent=2)}")
    return {"proposed_actions": actions}


def inspector_node(state: OrganizerState):
    """Scans proposed actions for HIGH risk steps and triggers Human-in-the-Loop approval."""
    print("\n--- Stage: inspector ---")
    actions = state["proposed_actions"]
    requires_approval = False
    
    for act in actions:
        if act.get("risk_level") == "HIGH":
            requires_approval = True
            print(f"\n⚠️ [SAFETY ALERT] High-risk file operation detected!")
            print(f"   - Danger: {act['action']} on '{act['target']}'")
            
    approved = False
    if requires_approval:
        user_input = input("Approve high-risk actions? (yes/no): ").strip().lower()
        if user_input in ["yes", "y"]:
            approved = True
    else:
        approved = True  # Auto-approve low-risk tasks
        
    return {"needs_approval": requires_approval, "user_approved": approved}


def executor_node(state: OrganizerState):
    """Performs real file system operations on the local disk using os and shutil."""
    print("\n--- Stage: executor ---")
    actions = state["proposed_actions"]
    logs = []
    has_errors = False

    for act in actions:
        action_type = act["action"]
        target = act["target"]
        destination = act["destination"]

        try:
            if action_type == "create_folder":
                os.makedirs(target, exist_ok=True)
                logs.append(f"REAL ACTION: Created folder '{target}'")

            elif action_type == "move_file":
                if os.path.exists(target):
                    shutil.move(target, os.path.join(destination, target))
                    logs.append(f"REAL ACTION: Moved '{target}' to '{destination}'")
                else:
                    logs.append(f"SKIP: File '{target}' does not exist to move")

            elif action_type == "delete_file":
                if not state["user_approved"]:
                    logs.append(f"FAILED: Unauthorized attempt to delete '{target}'")
                    has_errors = True
                elif os.path.exists(target):
                    os.remove(target)
                    logs.append(f"REAL ACTION: Deleted file '{target}'")
                else:
                    logs.append(f"SKIP: File '{target}' does not exist to delete")

        except Exception as e:
            logs.append(f"ERROR on {action_type}: {str(e)}")
            has_errors = True

    print(f"Logs: {logs}")
    return {
        "execution_logs": logs,
        "has_errors": has_errors,
        "retries": state.get("retries", 0) + 1
    }


def self_heal_node(state: OrganizerState):
    """Re-plans execution by stripping unauthorized or failing actions."""
    print("\n--- Stage: self_heal ---")
    print("🔄 Action failed or permission denied. Filtering out rejected operations and re-planning...")
    
    # Filter out unapproved high-risk operations
    safe_actions = [
        act for act in state["proposed_actions"]
        if not (act.get("risk_level") == "HIGH" and not state["user_approved"])
    ]
    
    return {"proposed_actions": safe_actions, "has_errors": False}


# ==================================================
# 4. Conditional Edge Routing Logic
# ==================================================

def route_after_execution(state: OrganizerState) -> str:
    """Routes state back to self_heal if errors occurred, otherwise finishes graph."""
    if state["has_errors"] and state.get("retries", 0) < 2:
        return "self_heal"
    return END 


# ==================================================
# 5. Build and Compile LangGraph Workflow
# ==================================================
builder = StateGraph(OrganizerState)

# Add nodes
builder.add_node("planner", planner_node)
builder.add_node("inspector", inspector_node)
builder.add_node("executor", executor_node)
builder.add_node("self_heal", self_heal_node)

# Set entry point and static edges
builder.set_entry_point("planner")
builder.add_edge("planner", "inspector")
builder.add_edge("inspector", "executor")

# Add conditional routing edge
builder.add_conditional_edges("executor", route_after_execution)
builder.add_edge("self_heal", "executor")

# Compile graph
app = builder.compile()


# ==================================================
# 6. Run Application
# ==================================================
if __name__ == "__main__":
    prompt = "Create a 'Projects' folder, move 'report.pdf' into it, and delete 'temp_draft.txt'"
    print(f"User Request: {prompt}")
    print("=" * 50)
    
    initial_state = {
        "user_request": prompt,
        "proposed_actions": [],
        "needs_approval": False,
        "user_approved": False,
        "execution_logs": [],
        "has_errors": False,
        "retries": 0
    }
    
    app.invoke(initial_state)
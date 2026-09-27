import os
import streamlit as st
from app import run_organizer, resume_organizer, BASE_DIR

st.set_page_config(page_title="Agentic File Organizer", page_icon="📁", layout="centered")

st.title("📁 Agentic File Organizer")
st.caption("Local, privacy-focused file management powered by LangGraph & Qwen2.5")
st.markdown("---")

# 1. Target Directory Input
st.subheader("1. Select Directory")
target_directory = st.text_input(
    "Enter the absolute path of the folder you want to organize:", 
    value=BASE_DIR
)

# Validate Directory
if not os.path.exists(target_directory):
    st.error("⚠️ Path does not exist. Please enter a valid directory.")
    valid_path = False
else:
    st.success(f"Selected Directory: `{os.path.abspath(target_directory)}`")
    valid_path = True

# 2. Instruction Input
st.subheader("2. Instruction")
user_instruction = st.text_area(
    "What would you like the agent to do?", 
    placeholder="e.g., Create a 'Projects' folder, move 'report.pdf' into it, and delete 'temp_draft.txt'"
)

st.markdown("---")

# 3. Trigger Agent Execution
if st.button("Run Organizer", type="primary", disabled=not valid_path or not user_instruction):
    with st.spinner("Analyzing files and building action plan..."):
        state = run_organizer(target_directory=target_directory, instruction=user_instruction)
        st.session_state["graph_state"] = state

# 4. Human-in-the-Loop Safety Gate Interface
current_state = st.session_state.get("graph_state")

if current_state and getattr(current_state, "next", None):
    pending_tasks = current_state.values.get("proposed_actions", [])
    high_risk = [a for a in pending_tasks if a.get("risk_level") == "HIGH"]
    
    st.warning("⚠️ **[SAFETY ALERT] High-risk file operation detected!**")
    for action in high_risk:
        st.write(f"- Danger: `{action.get('action')}` on `{action.get('target')}`")
        
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Approve & Execute", type="primary"):
            updated_state = resume_organizer(approved=True)
            st.session_state["graph_state"] = updated_state
            st.success("🎉 Actions approved and executed!")
            st.rerun()
            
    with col2:
        if st.button("❌ Reject & Abort"):
            updated_state = resume_organizer(approved=False)
            st.session_state["graph_state"] = updated_state
            st.error("🚫 Operation canceled safely. No files were modified.")
            st.rerun()

elif current_state and not getattr(current_state, "next", None):
    st.success("🎉 Organization complete! All operations finished safely.")
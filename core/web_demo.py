#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Echoes Batch Processing Web Demo
=================================

Streamlit web interface for the Echoes batch processing system.
Provides an easy-to-use web interface for demonstrating AI-powered
text processing with budget protection.

Features:
- File upload and text input
- Task selection (summarize, rephrase, extract_actions)
- Budget monitoring and cost estimation
- Dry-run simulation
- Live processing with real API calls
- Results display and history
"""

import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import streamlit as st

# Add src to path for imports
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

try:
    from utils.budget_guard import (
        check_budget,
        choose_model_for_task,
        estimate_tokens,
        load_budget,
    )
except ImportError:
    st.error("❌ Batch processing modules not found. Please run from src/ directory.")
    st.stop()


def main():
    """Main Streamlit application."""

    # Page configuration
    st.set_page_config(
        page_title="Echoes Batch Processing Demo",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Title and description
    st.title("🤖 Echoes Batch Processing Demo")
    st.markdown(
        """
    **Multi-Modal AI Platform with Budget Protection**

    Upload text files or paste content to process with AI. Features include:
    - Smart model selection based on cost and content length
    - Budget protection ($5.00 default limit)
    - Dry-run simulation (no API costs)
    - Real-time processing with cost tracking
    """
    )

    # Sidebar with system status
    render_sidebar()

    # Main content area
    render_main_content()


def render_sidebar():
    """Render the sidebar with system status and controls."""

    st.sidebar.title("⚙️ System Status")

    # Budget status
    ok, remaining, data = check_budget()
    budget_color = "🟢" if ok else "🔴"
    budget_status = "ACTIVE" if ok else "EXHAUSTED"

    st.sidebar.metric(
        label="Budget Status",
        value=f"{budget_color} {budget_status}",
        delta=f"${remaining:.2f} remaining",
    )

    st.sidebar.write(f"**Spent:** ${data['spent']:.2f}")
    st.sidebar.write(f"**API Calls:** {data['calls']}")

    # File counts
    input_dir = src_path / "data" / "input_samples"
    output_dir = src_path / "data" / "outputs"

    input_count = len(list(input_dir.glob("*.txt"))) if input_dir.exists() else 0
    output_count = len(list(output_dir.glob("*.txt"))) if output_dir.exists() else 0

    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Input Files", input_count)
    with col2:
        st.metric("Output Files", output_count)

    # Model pricing info
    st.sidebar.markdown("---")
    st.sidebar.subheader("💰 Model Pricing")
    st.sidebar.write("**GPT-4.1:** $0.15/1k tokens")
    st.sidebar.write("**GPT-3.5-turbo:** $0.50/1k tokens")
    st.sidebar.write("**GPT-4o:** $2.50/1k tokens")

    # API Key status
    has_api_key = bool(os.environ.get("OPENAI_API_KEY"))
    api_status = "✅ Set" if has_api_key else "❌ Missing"
    st.sidebar.write(f"**API Key:** {api_status}")

    if not has_api_key:
        st.sidebar.warning("Set OPENAI_API_KEY in .env for live processing")


def render_main_content():
    """Render the main content area."""

    # Input method selection
    st.header("📝 Input Content")

    input_method = st.radio("Choose input method:", ["Upload Files", "Paste Text"], horizontal=True)

    # Task selection
    st.header("🎯 Processing Task")
    task = st.selectbox(
        "Select processing task:",
        ["summarize", "rephrase", "extract_actions"],
        help="""
        - **summarize**: Create concise summaries of the content
        - **rephrase**: Rewrite content in different words
        - **extract_actions**: Pull out actionable items from text
        """,
    )

    # Processing mode
    st.header("⚡ Processing Mode")
    mode = st.radio(
        "Select processing mode:",
        ["Dry Run (Free)", "Live Processing"],
        help="""
        - **Dry Run**: Simulate processing without API calls (free)
        - **Live Processing**: Make real API calls (costs apply)
        """,
    )

    # Content input based on method
    content_files = []

    if input_method == "Upload Files":
        uploaded_files = st.file_uploader(
            "Upload .txt files:",
            type=["txt"],
            accept_multiple_files=True,
            help="Upload one or more .txt files to process",
        )

        if uploaded_files:
            st.success(f"📁 {len(uploaded_files)} file(s) uploaded")

            # Save uploaded files temporarily
            temp_dir = Path(tempfile.mkdtemp())
            content_files = []

            for uploaded_file in uploaded_files:
                file_path = temp_dir / uploaded_file.name
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                content_files.append(file_path)

    else:  # Paste Text
        text_input = st.text_area(
            "Paste your text here:",
            height=200,
            placeholder="Enter the text you want to process...",
            help="Enter the text content to process",
        )

        if text_input.strip():
            # Save pasted text as temporary file
            temp_dir = Path(tempfile.mkdtemp())
            file_path = temp_dir / "pasted_content.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text_input.strip())
            content_files = [file_path]

    # Process button
    if content_files:
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            process_button = st.button("🚀 Process Content", type="primary")

        with col2:
            clear_button = st.button("🗑️ Clear Results")

        if clear_button:
            st.session_state.results = None
            st.rerun()

        if process_button:
            with st.spinner("Processing content..."):
                results = process_content(content_files, task, mode == "Dry Run (Free)")
                st.session_state.results = results

    # Display results
    if "results" in st.session_state and st.session_state.results:
        render_results(st.session_state.results)


def process_content(file_paths, task, dry_run=False):
    """Process the uploaded/pasted content."""

    results = {
        "timestamp": datetime.now(),
        "task": task,
        "dry_run": dry_run,
        "files_processed": [],
        "total_cost": 0.0,
        "total_tokens": 0,
        "budget_remaining": 0.0,
        "processing_log": [],
    }

    # Create temporary input directory if needed
    temp_input_dir = None
    if not dry_run:
        temp_input_dir = Path(tempfile.mkdtemp())
        for file_path in file_paths:
            import shutil

            shutil.copy2(file_path, temp_input_dir / file_path.name)

    try:
        # Build command
        cmd = [sys.executable, str(src_path / "batch_processor.py")]
        cmd.append(f"--task={task}")
        if dry_run:
            cmd.append("--dry-run")

        # Run batch processor
        env = os.environ.copy()
        env["PYTHONPATH"] = str(src_path)

        result = subprocess.run(cmd, cwd=src_path, capture_output=True, text=True, env=env)

        # Parse results
        results["exit_code"] = result.returncode
        results["stdout"] = result.stdout
        results["stderr"] = result.stderr

        # Extract processing information from stdout
        lines = result.stdout.split("\n")
        for line in lines:
            if line.startswith("[INFO]"):
                # Parse file processing info
                parts = line.split(" | ")
                if len(parts) >= 3:
                    filename = parts[0].replace("[INFO] File: ", "").strip()
                    est_tokens = int(parts[1].replace("est_tokens: ", "").strip())
                    model = parts[2].replace("model: ", "").strip()

                    results["files_processed"].append(
                        {
                            "filename": filename,
                            "estimated_tokens": est_tokens,
                            "selected_model": model,
                        }
                    )

            elif line.startswith("[DONE]"):
                # Parse completion info
                parts = line.split(" | ")
                if len(parts) >= 3:
                    tokens_used = int(parts[0].replace("[DONE] tokens_used: ", "").strip())
                    cost = float(parts[1].replace("cost: $", "").strip())

                    results["total_tokens"] = tokens_used
                    results["total_cost"] = cost

        # Get updated budget info
        ok, remaining, data = check_budget()
        results["budget_remaining"] = remaining

        # Check for output files if not dry run
        if not dry_run and temp_input_dir:
            output_dir = src_path / "data" / "outputs"
            if output_dir.exists():
                output_files = list(output_dir.glob(f"*_{task}.txt"))
                results["output_files"] = [f.name for f in output_files]

    except Exception as e:
        results["error"] = str(e)
        st.error(f"Processing error: {e}")

    finally:
        # Cleanup temp directory
        if temp_input_dir and temp_input_dir.exists():
            import shutil

            shutil.rmtree(temp_input_dir, ignore_errors=True)

    return results


def render_results(results):
    """Render the processing results."""

    st.header("📊 Processing Results")

    # Status overview
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        status_icon = "✅" if results.get("exit_code", 1) == 0 else "❌"
        st.metric(
            "Status",
            f"{status_icon} {'Success' if results.get('exit_code', 1) == 0 else 'Failed'}",
        )

    with col2:
        st.metric("Files Processed", len(results.get("files_processed", [])))

    with col3:
        cost_display = f"${results.get('total_cost', 0):.4f}"
        if results.get("dry_run"):
            cost_display += " (simulated)"
        st.metric("Cost", cost_display)

    with col4:
        st.metric("Budget Remaining", f"${results.get('budget_remaining', 0):.2f}")

    # Processing details
    if results.get("files_processed"):
        st.subheader("📁 File Processing Details")

        for file_info in results["files_processed"]:
            with st.expander(f"📄 {file_info['filename']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Estimated Tokens:** {file_info['estimated_tokens']}")
                with col2:
                    st.write(f"**Selected Model:** {file_info['selected_model']}")
                with col3:
                    # Calculate estimated cost
                    est_tokens = file_info["estimated_tokens"]
                    model = file_info["selected_model"]
                    if model == "gpt-4.1":
                        est_cost = (est_tokens / 1000.0) * 0.15
                    elif model == "gpt-3.5-turbo":
                        est_cost = (est_tokens / 1000.0) * 0.50
                    elif model == "gpt-4o":
                        est_cost = (est_tokens / 1000.0) * 2.50
                    else:
                        est_cost = 0
                    st.write(f"**Est. Cost:** ${est_cost:.4f}")

    # Processing log
    if results.get("stdout"):
        st.subheader("📋 Processing Log")
        with st.expander("View detailed log"):
            st.code(results["stdout"], language="text")

    # Error display
    if results.get("stderr"):
        st.subheader("⚠️ Errors/Warnings")
        st.error(results["stderr"])

    if results.get("error"):
        st.error(f"Processing Error: {results['error']}")

    # Output files
    if not results.get("dry_run") and results.get("output_files"):
        st.subheader("📤 Generated Output Files")
        for filename in results["output_files"]:
            st.write(f"✅ {filename}")

        # Show sample output if available
        output_dir = src_path / "data" / "outputs"
        if output_dir.exists():
            sample_file = output_dir / results["output_files"][0]
            if sample_file.exists():
                with st.expander("👀 Preview Sample Output"):
                    try:
                        with open(sample_file, "r", encoding="utf-8") as f:
                            content = f.read()
                        st.text_area("Sample Output:", content, height=200)
                    except Exception as e:
                        st.error(f"Could not read output file: {e}")

    # Summary
    st.success("🎉 Processing completed! Check the processing log above for detailed results.")

    # Download results summary
    if st.button("📥 Download Results Summary"):
        summary_text = f"""
Echoes Batch Processing Results
===============================

Timestamp: {results["timestamp"]}
Task: {results["task"]}
Mode: {"Dry Run" if results["dry_run"] else "Live Processing"}
Files Processed: {len(results.get("files_processed", []))}
Total Cost: ${results.get("total_cost", 0):.4f}
Budget Remaining: ${results.get("budget_remaining", 0):.2f}

Processing Log:
{results.get("stdout", "No log available")}
        """

        st.download_button(
            label="Download Summary",
            data=summary_text,
            file_name=f"echoes_processing_results_{results['timestamp'].strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
        )


if __name__ == "__main__":
    main()

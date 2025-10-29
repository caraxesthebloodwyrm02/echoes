import json
from openai import OpenAI
from .realtime_preview import GlimpseOrchestrator


class ContextAwareAPICall:
    """An API call handler that is aware of the Glimpse trajectory and codebase."""

    def __init__(self, glimpse_system: GlimpseOrchestrator):
        self.glimpse = glimpse_system
        self.client = OpenAI()  # Assumes OPENAI_API_KEY is in the environment
        self.model = "gpt-4o"
        self.guideline_prompt = " ".join(
            [
                "You are a helpful assistant. Your goal is to answer the user's query based on the provided context.",
                "The context includes a summary of recent activity (trajectory).",
                "If you need to read a file, first find its path using the 'search_for_file' tool. This tool takes a 'search_term' argument, which can be a file name or a class name.",
                'Example: TOOL_CALL: {{"tool":"search_for_file","args":{{"search_term":"GuardrailMiddleware"}}}}',
                "Once you have the path, use the 'read_file' tool to get its contents.",
                'Example: TOOL_CALL: {{"tool":"read_file","args":{{"file_path":"automation/guardrails/middleware.py"}}}}',
                "Only call one tool at a time and ensure your TOOL_CALL output is a single, complete JSON object. Otherwise, answer the user's query concisely.",
            ]
        )

    def run(self, user_query: str, max_loops=5):
        """Runs the context-aware API call, handling multiple tool calls in a loop."""
        # 1. Get context from Glimpse
        trajectory_summary = self.glimpse.get_full_state().get("trajectory", {})
        context_prompt = f"TRAJECTORY_CONTEXT: {json.dumps(trajectory_summary)}"

        # 2. Construct the initial prompt
        current_prompt = f"USER_QUERY: {user_query}\n\n{context_prompt}\n\n{self.guideline_prompt}"

        for i in range(max_loops):
            print(f"--- Sending Request (Loop {i+1}) ---")
            resp = self.client.responses.create(model=self.model, input=current_prompt)
            text = getattr(resp, "output_text", str(resp))
            print(f"MODEL SAYS:\n{text}")

            if "TOOL_CALL:" in text:
                payload = text.split("TOOL_CALL:", 1)[1].strip()

                # Take only the first tool call if multiple are present
                if "TOOL_CALL:" in payload:
                    payload = payload.split("TOOL_CALL:")[0].strip()

                # Robust parsing: clean common formatting artifacts
                payload = payload.strip("`").strip()  # Remove backticks
                payload = payload.strip('"').strip()  # Remove quotes

                # Extract from code blocks if present
                if "```json" in payload:
                    payload = payload.split("```json")[1].split("```")[0].strip()
                elif "```" in payload:
                    payload = payload.split("```")[1].split("```")[0].strip()

                # Extract just the JSON object if there's extra text
                import re

                json_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", payload)
                if json_match:
                    payload = json_match.group()

                try:
                    tool_req = json.loads(payload)
                    tool_result = self._handle_tool_call(tool_req)
                    # Re-inject the original query and give a very direct instruction.
                    current_prompt = (
                        f"Your original query is: '{user_query}'.\n"
                        f"The last tool call returned: {json.dumps(tool_result)}\n\n"
                        "Your task is to answer the original query. "
                        "If you have enough information, provide the final answer now. "
                        "If you need more information, you MUST respond with ONLY a single `TOOL_CALL:` JSON object and nothing else."
                    )
                except json.JSONDecodeError:
                    print("ERROR: Could not decode tool call JSON.")
                    # Ask the model to correct its mistake
                    current_prompt = "Your previous tool call was not valid JSON. Please correct it or answer the user's query directly."
            else:
                # No tool call, so this is the final answer
                print("--- Final Answer ---")
                return text

        print("--- Max loops reached. Returning last response. ---")
        return text

    def _handle_tool_call(self, tool_req: dict):
        """Handles a tool call request from the model, with intent recognition."""
        tool_name = tool_req.get("tool")
        tool_args = tool_req.get("args", {})

        # Intent Recognition: If the model forgets the tool name but provides a file path, infer 'read_file'.
        # Accept multiple variations: file_path, file, path
        if not tool_name and ("file_path" in tool_req or "file" in tool_req or "path" in tool_req):
            tool_name = "read_file"
            # Synthesize the args from the root of the request
            file_path = tool_req.get("file_path") or tool_req.get("file") or tool_req.get("path")
            tool_args = {"file_path": file_path}

        if tool_name == "search_for_file":
            search_term = tool_args.get("search_term")
            if not search_term:
                return {"error": "'search_term' is a required argument for search_for_file."}

            try:
                base_path = self.glimpse.base_path.parent
                found_files = []
                # Search for files containing the term in their name
                for p in base_path.rglob(f"**/*{search_term}*.py"):
                    found_files.append(p)
                # Search for files containing the term in their content
                for p in base_path.rglob("**/*.py"):
                    if search_term in p.read_text(encoding="utf-8", errors="ignore"):
                        if p not in found_files:
                            found_files.append(p)

                if found_files:
                    relative_paths = [str(p.relative_to(base_path)) for p in found_files]
                    return {"found_files": relative_paths}
                else:
                    return {"error": f"No files found containing '{search_term}'."}
            except Exception as e:
                return {"error": f"Failed to search for file: {str(e)}"}

        elif tool_name == "read_file":
            file_path_str = tool_args.get("file_path")
            if not file_path_str:
                return {"error": "'file_path' is a required argument for read_file."}

            try:
                # Security: ensure path is within the project directory
                base_path = self.glimpse.base_path.parent
                target_path = base_path.joinpath(file_path_str).resolve()
                if base_path not in target_path.parents:
                    return {"error": "File path is outside the project directory."}

                if target_path.is_file():
                    content = target_path.read_text(encoding="utf-8")
                    return {"file_path": file_path_str, "content": content[:2000] + "... (truncated)"}
                else:
                    return {"error": f"File not found at {file_path_str}"}
            except Exception as e:
                return {"error": f"Failed to read file: {str(e)}"}

        return {"error": f"Unknown tool: {tool_name}"}

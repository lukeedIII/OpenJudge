import os
import json
import asyncio
from typing import Callable, Dict, Any, AsyncGenerator

from parser import OpenJudgeParser, FormatViolationError
from state_manager import StateManager
from llm_client import call_llm
import tools

class OpenJudgeEngine:
    def __init__(self, max_iterations: int = 25):
        self.max_iterations = max_iterations
        self.parser = OpenJudgeParser()
        self.registered_tools: Dict[str, Dict[str, Any]] = {}
        
        # Load the base system prompt blueprint
        self.system_prompt_blueprint = self._load_blueprint()
        
        # Automatically register the standard toolset
        self._register_default_tools()

    def _load_blueprint(self) -> str:
        prompt_path = os.path.join(os.path.dirname(__file__), 'OPENJUDGE.md')
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return "CRITICAL ERROR: OPENJUDGE.md blueprint not found. The Engine cannot function."

    def register_tool(self, name: str, description: str, func: Callable[[str], str]):
        """
        BYOT SDK Endpoint: Allows developers to dynamically inject custom tools 
        into the OpenJudge cognitive loop.
        """
        self.registered_tools[name] = {
            "description": description,
            "func": func
        }

    def _generate_dynamic_prompt(self, state_context: str) -> str:
        """
        Injects the dynamic Tool Registry and current state into the System Prompt.
        """
        registry_text = ""
        for i, (name, metadata) in enumerate(self.registered_tools.items(), 1):
            registry_text += f"{i}. **{name}**\n   - {metadata['description']}\n"
            
        base_prompt = self.system_prompt_blueprint.replace("{{TOOL_REGISTRY_PLACEHOLDER}}", registry_text)
        return f"{base_prompt}\n\n{state_context}"

    async def stream_execute(self, user_goal: str) -> AsyncGenerator[str, None]:
        """
        The Enterprise Streaming API. Executes the autonomous agent loop and 
        yields structured JSON telemetry events to empower "Observer UI" dashboards.
        """
        state_manager = StateManager()
        
        yield json.dumps({
            "event": "AGENT_START",
            "message": f"Booting OpenJudge Engine. Objective: {user_goal}",
            "registered_tools": list(self.registered_tools.keys())
        })
        
        while True:
            if state_manager.iteration_count >= self.max_iterations:
                yield json.dumps({"event": "ENGINE_HALT", "reason": "MAX_ITERATIONS", "state_dump": state_manager.format_for_prompt()})
                break

            state_manager.increment_iteration()
            iter_num = state_manager.iteration_count
            
            yield json.dumps({"event": "ITERATION_START", "iteration": iter_num})
            
            # Format injection prompt
            state_context = state_manager.format_for_prompt()
            structured_system = self._generate_dynamic_prompt(state_context)
            
            yield json.dumps({"event": "LLM_INFERENCE_START", "iteration": iter_num})
            
            # Note: call_llm is synchronous, in a real ASGI backend we might run this in a threadpool
            # but for this V3 initial prototype we yield before and after.
            raw_response = call_llm(structured_system, f"USER OBJECTIVE: {user_goal}")
            
            if "[CRITICAL LLM API ERROR]" in raw_response:
                yield json.dumps({"event": "API_ERROR", "message": raw_response})
                yield json.dumps({"event": "ENGINE_HALT", "reason": "API_DISRUPTION"})
                break

            try:
                parsed_data = self.parser.parse(raw_response)
                enforcement = parsed_data.get("enforcement")
                tool_req = parsed_data.get("tool_required")
                tool_payload = parsed_data.get("tool_payload")
                
                # Yield the AI's internal reasoning
                yield json.dumps({
                    "event": "THOUGHT_PROCESS",
                    "iteration": iter_num,
                    "state_memory": parsed_data.get("state_memory"),
                    "logical_extern": parsed_data.get("logical_extern"),
                    "verdict": parsed_data.get("verdict"),
                    "enforcement": enforcement
                })
                
                if enforcement == "TERMINATE":
                    yield json.dumps({"event": "ENGINE_HALT", "reason": "TERMINATE_ACHIEVED", "final_logic": parsed_data.get("logical_extern")})
                    break

                if enforcement in ["PROCEED", "PURGE", "PIVOT"]:
                    state_manager.add_action(f"Agent Action: {enforcement}")
                    
                    if tool_req and tool_req in self.registered_tools:
                        yield json.dumps({"event": "TOOL_TRIGGERED", "tool": tool_req, "payload": tool_payload})
                        
                        tool_func = self.registered_tools[tool_req]["func"]
                        try:
                            tool_output = tool_func(tool_payload)
                        except Exception as tool_e:
                            tool_output = f"[ERROR] Tool failed: {str(tool_e)}"
                            
                        # Feed the exact truth back to the ledger
                        state_manager.add_tool_output(tool_req, tool_output)
                        
                        yield json.dumps({
                            "event": "TOOL_RESULT",
                            "tool": tool_req,
                            "output_snippet": str(tool_output)[:200] + ("..." if len(str(tool_output)) > 200 else "")
                        })
                    elif tool_req:
                        err_msg = f"[ERROR] Tool '{tool_req}' requested but is not registered in the BYOT registry."
                        state_manager.add_tool_output(tool_req, err_msg)
                        yield json.dumps({"event": "TOOL_ERROR", "message": err_msg})
                    else:
                        yield json.dumps({"event": "NO_TOOL_REQUESTED", "message": "Enforcement tag received but no physical tool was designated."})

            except FormatViolationError as e:
                err_text = str(e)
                yield json.dumps({"event": "FORMAT_VIOLATION", "error": err_text})
                
                # Self-Healing
                override_msg = (
                    f"SYSTEM OVERRIDE: Invalid output format. {err_text} "
                    "You MUST output the <openjudge_process> XML block containing <state_memory>, "
                    "<logical_extern>, <verdict>, and optionally <tool_required>, <tool_payload>. "
                    "End your response with an [ENFORCE: ACTION] tag. Fix immediately."
                )
                state_manager.add_failure(override_msg)
                
            except Exception as generic_e:
                yield json.dumps({"event": "CRITICAL_ERROR", "message": str(generic_e)})
                state_manager.add_failure(str(generic_e))

    def _register_default_tools(self):
        """Registers the standard OpenJudge suite of deterministic tools."""
        self.register_tool(
            "bash",
            "Payload: The raw shell command string.\n   - Use: System operations, git, file commands, installing packages.",
            tools.execute_bash
        )
        self.register_tool(
            "python",
            "Payload: The raw Python code string.\n   - Use: Executing logic, testing isolated scripts.",
            tools.execute_python
        )
        self.register_tool(
            "read_file",
            "Payload: Absolute or relative filepath.\n   - Use: Reading the contents of a file into your logical extern.",
            tools.read_file
        )
        def write_file_wrapper(payload: str):
            parts = payload.split("|", 1)
            if len(parts) == 2:
                return tools.write_file(parts[0].strip(), parts[1])
            return "[ERROR] Invalid payload for write_file. Expected format: filepath|content"
        
        self.register_tool(
            "write_file",
            "Payload: filepath|content \n   - Use: Writing or overwriting a file with the provided content.",
            write_file_wrapper
        )
        self.register_tool(
            "web_search",
            "Payload: The search query string.\n   - Use: Fetching real-time facts, reference data, or documentation from the web.",
            tools.web_search
        )
        def analyze_image_wrapper(payload: str):
            parts = payload.split("|", 1)
            if len(parts) == 2:
                return tools.analyze_image(parts[0].strip(), parts[1].strip())
            return "[ERROR] Invalid payload for analyze_image. Expected format: filepath|question"
            
        self.register_tool(
            "analyze_image",
            "Payload: filepath|question\n   - Use: Utilizing the Vision API to inspect pixels, verify screenshots, or analyze image data.",
            analyze_image_wrapper
        )
        def git_action_wrapper(payload: str):
            parts = payload.split("|")
            if len(parts) >= 2:
                return tools.git_action(parts[0].strip(), parts[1].strip(), parts[2].strip() if len(parts) > 2 else "", parts[3].strip() if len(parts) > 3 else "")
            return "[ERROR] Invalid payload for git_action. Expected: repo_path|action|[branch]|[message]"
            
        self.register_tool(
            "git_action",
            "Payload: repo_path|action|[branch]|[message]\n   - Actions: init, clone, commit, push, checkout, status\n   - Use: Safe repository orchestration without raw bash errors.",
            git_action_wrapper
        )
        def browser_action_wrapper(payload: str):
            parts = payload.split("|")
            if len(parts) >= 2:
                return tools.browser_action(parts[0].strip(), parts[1].strip(), parts[2].strip() if len(parts) > 2 else "", parts[3].strip() if len(parts) > 3 else "")
            return "[ERROR] Invalid payload for browser_action. Expected: url|action|[selector]|[value]"
            
        self.register_tool(
            "browser_action",
            "Payload: url|action|[selector]|[value]\n   - Actions: goto_and_screenshot, extract_html, click, type\n   - Use: Physically controlling a headless Chrome browser to test SPAs, log in, or scrape dynamic DOMs.",
            browser_action_wrapper
        )
        def memory_store_wrapper(payload: str):
            parts = payload.split("|", 1)
            if len(parts) >= 1:
                return tools.memory_store(parts[0].strip(), parts[1].strip() if len(parts) > 1 else "general")
            return "[ERROR] Invalid payload for memory_store. Expected: document|[type]"
            
        self.register_tool(
            "memory_store",
            "Payload: document_text|[type_tag]\n   - Use: Pushing a factual event or code snippet into ChromaDB Long-Term Vector Memory.",
            memory_store_wrapper
        )
        def memory_query_wrapper(payload: str):
            parts = payload.split("|", 1)
            if len(parts) >= 1:
                return tools.memory_query(parts[0].strip(), parts[1].strip() if len(parts) > 1 else "3")
            return "[ERROR] Invalid payload for memory_query. Expected: query|[count]"
            
        self.register_tool(
            "memory_query",
            "Payload: semantic_search_query|[count]\n   - Use: Retrieving historical actions or state using semantic RAG from Vector Memory to avoid context bloat.",
            memory_query_wrapper
        )

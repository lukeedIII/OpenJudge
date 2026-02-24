import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from parser import OpenJudgeParser, FormatViolationError
from state_manager import StateManager
from llm_client import call_llm
import tools

# Load environment variables (e.g., OPENAI_API_KEY)
load_dotenv()

console = Console()
MAX_ITERATIONS = 25

def execute_action(action_type: str, tool_req: str, tool_payload: str, state_manager: StateManager) -> str:
    """
    Routes the generic action type to specific Python-level tool executions.
    Supports bash, python, read_file, write_file, web_search, analyze_image.
    """
    console.print(f"[*] Action Route Triggered: {action_type}", style="bold yellow")
    
    if action_type == "TERMINATE":
        return "TERMINATE"
        
    if not tool_req or not tool_payload:
        return "[WARNING] Action requested, but no <tool_required> or <tool_payload> provided. Proceeding without physical action."

    tool_req = tool_req.lower().strip()
    console.print(f"[*] Initiating Physical Tool Execution: {tool_req}", style="bold yellow")
    
    # Tool Routing Matrix
    if tool_req == "bash":
        return tools.execute_bash(tool_payload)
    elif tool_req == "python":
        return tools.execute_python(tool_payload)
    elif tool_req == "read_file":
        return tools.read_file(tool_payload.strip())
    elif tool_req == "write_file":
        # Custom syntax for write file: <filepath>|<content>
        parts = tool_payload.split("|", 1)
        if len(parts) == 2:
            return tools.write_file(parts[0].strip(), parts[1])
        else:
            return "[ERROR] Invalid payload for write_file. Expected format: filepath|content"
    elif tool_req == "web_search":
        return tools.web_search(tool_payload.strip())
    elif tool_req == "analyze_image":
        parts = tool_payload.split("|", 1)
        if len(parts) == 2:
            return tools.analyze_image(parts[0].strip(), parts[1].strip())
        else:
            return "[ERROR] Invalid payload for analyze_image. Expected format: filepath|question"
    else:
        return f"[ERROR] Unknown tool requested: '{tool_req}'. Available: bash, python, read_file, write_file, web_search, analyze_image."

def main(automated_goal: str = None):
    console.print(Panel("=== Booting OpenJudge Production Runtime ===", style="bold blue"))
    
    # 1. Read OPENJUDGE.md
    system_prompt_path = os.path.join(os.path.dirname(__file__), 'OPENJUDGE.md')
    try:
        with open(system_prompt_path, 'r', encoding='utf-8') as f:
            system_prompt = f.read()
            console.print("[+] System Prompt (OPENJUDGE.md) loaded successfully.", style="green")
    except FileNotFoundError:
        console.print(f"[!] Critical Error: {system_prompt_path} not found.", style="bold red")
        return

    # Initialize Core Architectures
    parser = OpenJudgeParser()
    state_manager = StateManager()

    # 2. Accept final user goal via terminal input or parameter
    if automated_goal:
        user_goal = automated_goal
        console.print(f"\n--- Mission Control (Automated Mode) ---\nObjective: {user_goal}", style="bold cyan")
    else:
        console.print("\n--- Mission Control ---", style="bold cyan")
        user_goal = input("Enter the objective for OpenJudge: ")
    
    # 3. Enter the autonomous while True loop
    console.print("\n[+] Entering Autonomous Agentic Loop...", style="bold green")
    
    while True:
        if state_manager.iteration_count >= MAX_ITERATIONS:
            console.print(Panel("MAX ITERATIONS REACHED - FORCE HALT", style="bold red on white"))
            try:
                with open("failed_state.log", "w", encoding="utf-8") as f:
                    f.write(state_manager.format_for_prompt())
                console.print("[+] Final state saved to failed_state.log", style="yellow")
            except Exception as e:
                pass
            break

        state_manager.increment_iteration()
        console.print(f"\n======== AGENT ITERATION {state_manager.iteration_count} ========", style="bold magenta")
        
        # Inject state context into system prompt
        state_context = state_manager.format_for_prompt()
        structured_system = f"{system_prompt}\n\n{state_context}"
        
        # 4. Call LLM Gateway
        console.print(">>> [LLM Neural Gateway Engaged. Awaiting Inference...]", style="dim")
        raw_response = call_llm(structured_system, f"USER OBJECTIVE: {user_goal}")
        
        # Check if the API call failed entirely at the socket/key level
        if "[CRITICAL LLM API ERROR]" in raw_response:
             console.print(str(raw_response), style="bold red")
             console.print("[!] Halted due to external API disruption.", style="bold red")
             break
             
        # 5. Parse response through strict XML/Tag parser
        try:
            parsed_data = parser.parse(raw_response)
            enforcement = parsed_data.get("enforcement")
            tool_req = parsed_data.get("tool_required")
            tool_payload = parsed_data.get("tool_payload")
            
            # 6. Observer UI rendering
            # Cyan Panel for Memory & Logic
            thinking_text = f"State Memory:\n{parsed_data.get('state_memory')}\n\nLogical Extern:\n{parsed_data.get('logical_extern')}"
            console.print(Panel(thinking_text, title="Runtime Thought Process", border_style="cyan"))
            
            console.print(f"[*] XML Extract | Verdict: {parsed_data.get('verdict')}", style="bold cyan")
            
            # Action Execution Matrix
            if enforcement == "TERMINATE":
                console.print("\n[!] >>> KILL-SWITCH INITIATED <<< [!]", style="bold green")
                console.print(f">>> OpenJudge Loop Halted Successfully. [ENFORCE: {enforcement}]", style="bold green")
                break
                
            elif enforcement == "PROCEED":
                console.print(f"[*] Output Action : [ENFORCE: {enforcement}]", style="bold green")
            elif enforcement in ["PURGE", "PIVOT"]:
                console.print(f"[*] Output Action : [ENFORCE: {enforcement}]", style="bold red")

            if enforcement in ["PROCEED", "PURGE", "PIVOT"]:
                state_manager.add_action(f"Agent Action: {enforcement}")
                
                # Execute mapped tools
                tool_output = execute_action(enforcement, tool_req, tool_payload, state_manager)
                
                # Feed the literal truth back into the ledger
                state_manager.add_tool_output(tool_req if tool_req else "None", tool_output)
                console.print("[+] Feedback registered to Ledger of Truth:", style="yellow")
                snippet = str(tool_output)[:150].replace('\n', ' ') + ('...' if len(str(tool_output)) > 150 else '')
                console.print(f"    -> {snippet}", style="yellow")
                
        # 7. Self-Healing Mechanism (Catches parsing failure and loops back)
        except FormatViolationError as e:
            console.print(f"\n[!] FORMAT VIOLATION DETECTED: {e}", style="bold red")
            error_msg = (
                f"SYSTEM OVERRIDE: Invalid output format. {str(e)} "
                "You MUST output the <openjudge_process> XML block containing <state_memory>, "
                "<logical_extern>, <verdict>, and optionally <tool_required>, <tool_payload>. "
                "End your response with an [ENFORCE: ACTION] tag. Fix immediately."
            )
            state_manager.add_failure(error_msg)
            console.print("[+] Self-Healing engaged: Error logged to StateManager to force correction.", style="bold red")
            continue
            
        except Exception as generic_e:
            console.print(f"\n[!] CRITICAL RUNTIME ERROR: {generic_e}", style="bold red")
            state_manager.add_failure(str(generic_e))

if __name__ == "__main__":
    main()

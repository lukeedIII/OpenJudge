from typing import List, Dict, Any

class StateManager:
    """
    The 'Ledger of Truth' memory system.
    Maintains history of actions, recognized failures, and tool outputs
    to prevent the LLM from entering infinite loops and to mitigate context amnesia.
    """
    
    def __init__(self):
        self.history_of_actions: List[str] = []
        self.known_failures: List[str] = []
        self.tool_outputs: List[Dict[str, Any]] = []
        self.iteration_count: int = 0

    def add_action(self, action: str) -> None:
        """Logs an action taken by the Judge."""
        self.history_of_actions.append(f"[Iter {self.iteration_count}] {action}")

    def add_failure(self, failure_reason: str) -> None:
        """Logs a failure (e.g., format violation or execution error)."""
        self.known_failures.append(f"[Iter {self.iteration_count}] FAIL: {failure_reason}")

    def add_tool_output(self, tool_name: str, output: str) -> None:
        """Records the result of a tool execution."""
        self.tool_outputs.append({
            "iteration": self.iteration_count,
            "tool": tool_name,
            "output": output
        })

    def increment_iteration(self) -> None:
        """Advances the iteration counter."""
        self.iteration_count += 1

    def format_for_prompt(self) -> str:
        """
        Formats the history cleanly to be injected back into the LLM prompt.
        Ensures context is preserved without excessive bloat.
        """
        state_str = "=== RUNTIME STATE MEMORY ===\n\n"
        
        state_str += f"Current Iteration: {self.iteration_count}\n\n"
        
        state_str += "--- History of Actions ---\n"
        if not self.history_of_actions:
            state_str += "(No actions taken yet)\n"
        for act in self.history_of_actions[-10:]: # Keep recent bounds
            state_str += f"- {act}\n"
            
        state_str += "\n--- Known Failures (DO NOT REPEAT) ---\n"
        if not self.known_failures:
            state_str += "(No recorded failures)\n"
        for fail in self.known_failures[-5:]:
            state_str += f"- {fail}\n"
            
        state_str += "\n--- Recent Tool Logs ---\n"
        if not self.tool_outputs:
            state_str += "(No tools executed yet)\n"
        
        # Only show the last 3-5 tool outputs to prevent context bloat
        recent_outputs = self.tool_outputs[-5:]
        for out in recent_outputs:
            state_str += f"[{out['tool']} Output | Iter {out['iteration']}]:\n"
            # Truncate output if too long
            out_str = str(out['output'])
            if len(out_str) > 1000:
                out_str = out_str[:1000] + "... [TRUNCATED]"
            state_str += f"{out_str}\n"
            
        state_str += "============================\n"
        return state_str

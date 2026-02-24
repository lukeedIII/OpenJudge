import sys
import os
import asyncio
import json

# Add parent directory to path to import engine
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from engine import OpenJudgeEngine

def fake_database_tool(payload: str) -> str:
    """A fake tool to test BYOT SDK injection."""
    return f"[SUCCESS] Queried employee database for: {payload}. Result: John Doe, Salary $120k."

async def run_sdk_test():
    print("==================================================")
    print("🚀 RUNNING: V3 BYOT SDK & Streaming Telemetry Test")
    print("==================================================")
    print("This tests dynamic tool registration and async JSON yielding.\n")
    
    # Instantiate the SDK
    judging_engine = OpenJudgeEngine(max_iterations=5)
    
    # Register a purely custom tool
    judging_engine.register_tool(
        name="query_employee_db",
        description="Payload: employee_id\n   - Use: Queries the secure HR database for employee records.",
        func=fake_database_tool
    )
    
    print("[+] Registered custom tool: 'query_employee_db'")
    print("[+] Initiating Event-Driven Telemetry Stream...\n")
    
    # Goal that forces the LLM to use the new tool
    goal = "Query the employee database for ID 4242. Return the name and salary."
    
    # Consume the AsyncGenerator stream
    async for event_json in judging_engine.stream_execute(goal):
        try:
            event = json.loads(event_json)
            # Pretty-print the event packet
            event_type = event.get("event")
            print(f"[{event_type}] ", end="")
            
            if event_type == "AGENT_START":
                print(f"Goal: {event.get('message')}")
            elif event_type == "TOOL_TRIGGERED":
                print(f"Tool: {event.get('tool')} | Payload: {event.get('payload')}")
            elif event_type == "TOOL_RESULT":
                print(f"Output: {event.get('output_snippet')}")
            elif event_type == "THOUGHT_PROCESS":
                print(f"Verdict: {event.get('verdict')} | Enforcement: {event.get('enforcement')}")
            elif event_type == "ENGINE_HALT":
                print(f"Reason: {event.get('reason')}")
            else:
                print(str(event))
        except Exception as e:
            print(f"Error parsing event: {e}\nRaw: {event_json}")

if __name__ == "__main__":
    asyncio.run(run_sdk_test())

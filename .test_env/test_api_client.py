import asyncio
import json
import httpx

async def stream_openjudge_execution(objective: str):
    """
    Connects to the OpenJudge FastAPI SSE endpoint and natively prints 
    the streaming event packets as they arrive in real-time.
    """
    url = "http://127.0.0.1:8000/api/v1/judge/execute"
    payload = {"objective": objective}
    
    print("==================================================")
    print("🌐 RUNNING: Enterprise Microservice SSE Test")
    print("==================================================")
    print(f"[!] Connecting to OpenJudge Microservice API @ {url}...\n")
    
    # We use httpx to stream the asynchronous HTTP response
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream("POST", url, json=payload) as response:
            
                if response.status_code != 200:
                    print(f"[CRITICAL ERROR] Server returned {response.status_code}")
                    return
                
                print("[+] Connection Established. Streaming Cognitive Events...\n")
                
                # Iterate over the SSE "data: {...}\n\n" blocks
                async for chunk in response.aiter_lines():
                    if chunk.startswith("data: "):
                        # Strip "data: " and parse the JSON payload
                        json_str = chunk[6:]
                        try:
                            event = json.loads(json_str)
                            event_type = event.get("event")
                            
                            print(f"[HTTP] [{event_type}] ", end="")
                            if event_type == "AGENT_START":
                                print(event.get('message'))
                            elif event_type == "THOUGHT_PROCESS":
                                verdict = event.get("verdict")
                                enforce = event.get("enforcement")
                                print(f"Verdict: {verdict} | Action: {enforce}")
                            elif event_type == "TOOL_TRIGGERED":
                                print(f"Tool: {event.get('tool')} | Payload: {event.get('payload')}")
                            elif event_type == "TOOL_RESULT":
                                print(f"Output: {event.get('output_snippet')}")
                            elif event_type == "ENGINE_HALT":
                                print(f"Halt Reason: {event.get('reason')}")
                                break
                            else:
                                print(str(event))
                                
                        except json.JSONDecodeError:
                            print(f"[HTTP] Failed to parse: {chunk}")
                    
    except httpx.ConnectError:
        print("\n[!] FATAL: Could not connect to the microservice. Is Uvicorn running on port 8000?")

if __name__ == "__main__":
    test_objective = "Use Python to calculate 12345 multiplied by 98765. Return the final number."
    asyncio.run(stream_openjudge_execution(test_objective))

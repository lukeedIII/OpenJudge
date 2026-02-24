import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from engine import OpenJudgeEngine

app = FastAPI(title="OpenJudge V3 Microservice API")

# Instantiate a global engine pool (in a real enterprise app, this would be a session-managed factory)
global_engine = OpenJudgeEngine(max_iterations=25)

class ExecuteRequest(BaseModel):
    objective: str

@app.get("/")
def health_check():
    return {"status": "online", "system": "OpenJudge V3 Cognitive Overlord"}

@app.post("/api/v1/judge/execute")
async def execute_agent_loop(request: Request, payload: ExecuteRequest):
    """
    Enterprise Streaming Endpoint.
    Consumes the objective, initiates the OpenJudge LLM verification cycle, 
    and bridges the yield stream over HTTP Server-Sent Events (SSE).
    """
    
    async def sse_event_generator():
        # Iterate over the natively generated AsyncGenerator from engine.py
        async for telemetry_json in global_engine.stream_execute(payload.objective):
            # Checking if the client disconnected (e.g. closed browser)
            if await request.is_disconnected():
                print("[!] Client disconnected. Halting execution.")
                break
                
            # Yield formatted SSE event
            yield {"data": telemetry_json}

    return EventSourceResponse(sse_event_generator())

if __name__ == "__main__":
    import uvicorn
    # Boot the ASGI worker
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)

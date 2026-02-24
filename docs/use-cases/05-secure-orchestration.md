# Use Case 5: Secure Internal API Orchestration (BYOT)

Enterprise software architectures are riddled with closed-off CRMs, HR platforms, proprietary databases, and internal VPN-locked APIs. Standard hosted LLMs cannot reach these securely, nor can they execute commands on them safely.

OpenJudge introduces the **Bring Your Own Tools (BYOT)** SDK architecture, allowing you to securely bridge LLM cognition with your internal APIs without exposing your network to open internet scraping risks.

## The Problem with Vanilla LLMs
If you want an LLM to query your company's proprietary Stripe billing API or Snowflake data warehouse, pasting chunks of JSON context manually is highly inefficient. Furthermore, you cannot trust the LLM to write raw SQL queries and blindly execute them against production databases.

## The OpenJudge Solution
OpenJudge sits *inside* your VPN as a trusted Microservice. It acts as a routing abstraction layer. You don't give the AI raw API keys or database strings; instead, you register highly-structured, heavily-guarded Python functions to the Engine.

```python
from engine import OpenJudgeEngine

engine = OpenJudgeEngine(max_iterations=10)

def cancel_user_subscription(user_id: str):
    # Guardrails: Validate the user_id format
    if not user_id.startswith("cus_"):
        return "ERROR: Invalid customer ID format."
    
    # Securely hit the internal Stripe API (the AI never sees the API Key)
    stripe.Subscription.delete(user_id)
    return "SUCCESS: Subscription cancelled and prorated."

# Inject the SDK Tool
engine.register_tool(
    name="cancel_user_subscription",
    description="Payload: user_id (string). Use: Revokes a user's billing subscription. Strictly requires 'cus_' format.",
    func=cancel_user_subscription
)
```

1. **Security Isolation:** The LLM's only job is to return a strict `<logical_extern>` XML tag mapping to `cancel_user_subscription`. It never touches the real API.
2. **Deterministic Enforcment:** The OpenJudge Engine ensures the `user_id` payload matches the schema.
3. **Execution Guardrails:** Only if the XML is perfectly syntactically sound and the tool is registered will the Engine physically trigger the function.

## Business Value
- **Enterprise Automation:** Construct massive AI-driven CRMs where customer support agents can verbally ask OpenJudge to execute highly secure refunds, database purges, or user role upgrades without exposing raw API credentials.
- **The Telemetry Stream:** All tool injections and executions are streamed back in real-time via the V3 FastAPI JSON stream (`yield`), making it trivial to audit exact chain-of-custody actions for compliance.

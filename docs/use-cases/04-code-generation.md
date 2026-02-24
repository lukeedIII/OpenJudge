# Use Case 4: Deterministic Code Generation

The problem with "AI Coders" (like GitHub Copilot) is that they assume the code they just generated actually compiles and functions correctly. They do not run test suites and they do not verify logical constraints.

OpenJudge introduces **Test-Driven Auto-Coding**.

## The Problem with Vanilla LLMs
An LLM can generate a complex recursive Python algorithm. However, if there is a subtle off-by-one error or an indentation issue, the LLM confidently hands you broken code. You must paste it into your IDE, run it, find the error, and paste the traceback back into the chat.

## The OpenJudge Solution
OpenJudge breaks the hallucination cycle by writing code, executing it locally, capturing the stderr/stdout, and *fixing its own bugs* before ever showing you the final result.

This is the power of the OpenJudge **Execution-Enforcement Loop**.

1. **Generation:** OpenJudge uses the `write_file` tool to save `script.py`.
2. **Execution:** It uses the `execute_python` tool to boot the script in the local environment.
3. **Healing:** If standard error (`stderr`) returns an `IndentationError`, the LLM triggers a `[ENFORCE: PIVOT]` structural override. It amends its own memory ledger, rewrites the file, and tries again.
4. **Delivery:** It will loop iteratively until `script.py` executes cleanly with an Exit Code 0, delivering you a mathematically proven, working piece of software.

## Implementation Example 
Observe the internal XML dialogue as OpenJudge self-corrects:

```xml
<logical_extern>
  <tool_required>execute_python</tool_required>
  <tool_payload>{"code": "print(10 / 0)"}</tool_payload>
</logical_extern>

... Engine Intercepts Error ...

<state_memory>
  [PREVIOUS ERROR]: ZeroDivisionError: division by zero.
  [DECISION]: I must implement safe division constraints in the function logic.
</state_memory>
<logical_extern>
  <tool_required>write_file</tool_required>
  <tool_payload>{"path": "safe_math.py", "content": "..."}</tool_payload>
</logical_extern>
```

## Business Value
- **Autonomous Feature Development:** Stop manually debugging syntax errors from LLMs. OpenJudge delivers working, locally-verified code modules.
- **TDD Native:** Simply supply OpenJudge with a suite of unit tests, and the Engine will autonomously grind through iterations until every single test passes green.

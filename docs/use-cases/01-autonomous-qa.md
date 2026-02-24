# Use Case 1: Autonomous QA Testing & Visual Validation

Standard LLMs cannot reliably interact with modern web applications. They lack spatial awareness of the DOM and cannot physically click buttons or verify visual rendering. 

OpenJudge leverages its **Playwright Integration** and **Vision API** capabilities to execute mathematically verified QA testing loops.

## The Problem with Vanilla LLMs
If you ask an LLM to "Test the login flow on my React app", it will simply hallucinate a response: *"I clicked the login button and it worked successfully!"*. It didn't open a browser, it didn't click anything, and it didn't verify the DOM state.

## The OpenJudge Solution
OpenJudge operates on the principle of **Empirical Verification**. When instructed to perform a QA test, the OpenJudge cognitive loop executes the following sequence:

1. **Environmental Boot:** OpenJudge invokes `browser_action(action="goto", url="http://localhost:3000/login")` via its `tools.py` execution layer.
2. **Physical Interaction:** The Engine physically clicks the `#loginSubmit` button in a headless Chromium instance.
3. **Vision Verification:** Instead of guessing the outcome, OpenJudge captures a live PNG screenshot of the viewport and injects it into the Vision API.
4. **Empirical Enforcment:** The Engine asks: *"Does the screen currently display a red 'Invalid Password' toast Notification?"*
5. **The Ledger:** The verified result (PASS/FAIL) is committed to the internal `state_manager` Ledger, ensuring the AI cannot hallucinate the test results in subsequent reporting.

## Implementation Example (V3 SDK)

You can build a nightly QA cron-job in 10 lines of code:

```python
from engine import OpenJudgeEngine

engine = OpenJudgeEngine(max_iterations=15)

# The prompt forces empirical testing of the checkout flow
prompt = """
Your objective is to verify the eCommerce checkout flow on staging.
1. Navigate to /cart
2. Click the 'Checkout' button using Playwright.
3. Take a screenshot and analyze if the Stripe iframe successfully rendered.
4. Yield the final test validation status.
"""

# Stream the active QA events to your terminal or CI/CD logger
async for event in engine.stream_execute(prompt):
    if event["type"] == "TOOL_RESULT" and event["tool"] == "browser_action":
        print(f"✅ Executed Action: {event['payload']['action']}")
    
    if event["type"] == "ENGINE_HALT":
        print(f"🏁 Final QA Report: {event['final_verdict']}")
```

## Business Value
- **Zero-Code QA Automation:** Replace fragile Selenium/Cypress scripts with an autonomous agent that visually navigates UI changes without test-script maintenance.
- **100% Proven Results:** OpenJudge's architecture guarantees that the agent actually executed the browser actions before declaring success.

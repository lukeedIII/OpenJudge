# Use Case 6: Long-Term Agentic Memory & Codebase RAG

"Context Window Amnesia" kills autonomous AI agents. If you give an LLM a massive 150-file codebase, it conceptually "forgets" variables declared in File A by the time it begins editing File Z.

OpenJudge solves this bottleneck by offloading context accumulation from the standard token stream directly into an embedded **Vector Database (ChromaDB)**.

## The Problem with Vanilla LLMs
Standard conversational agents rely on standard text-blob ledgers. Every time the LLM executes a tool, the context window inflates. Eventually, the API rejects the request (`Context Length Exceeded`), or worse, the LLM hallucinates because the critical facts are buried in a wall of noise.

## The OpenJudge Solution
OpenJudge treats Memory as a physically accessible File System rather than a linear block of text.

1. **Memory Storage:** As OpenJudge navigates a complex multi-file application, it autonomously utilizes the `memory_store("The authentication logic is in jwt_handler.py")` tool.
2. **Vector Space Encoding:** The OpenJudge subsystem (via `memory_db.py`) encodes this text into high-dimensional embeddings and stores it inside ChromaDB locally.
3. **Semantic Retrieval:** 40 iterations later, when OpenJudge is attempting to build a frontend login modal, it realizes it needs the auth schema. Instead of hallucinating, it dynamically executes `memory_query("Where is the authentication logic and what is the payload schema?")`.
4. **Targeted Insertion:** ChromaDB strictly retrieves only the top-K relevant facts and safely injects them into the `state_manager`'s Ledger, keeping the LLM's active prompt highly efficient and focused.

## Implementation Example: Zero-Hallucination Git Agents

This memory architecture fundamentally enables the execution of the `git_action` toolset. 

```bash
[TOOL_TRIGGERED] executing action `git_action` with payload {"action": "clone", "url": "https://github.com/react/core.git"}
[THOUGHT_PROCESS] Repository cloned. I need to understand the Core Hooks architecture.
[TOOL_TRIGGERED] executing action `execute_bash` with payload {"command": "cat src/hooks.js"}
[TOOL_TRIGGERED] executing action `memory_store` with payload {"fact": "Core hooks utilize React.memo heavily on line 400."}
... 50 Steps Later ...
[TOOL_TRIGGERED] executing action `memory_query` with payload {"query": "How do core hooks optimize re-renders?"}
[STATE_MANAGER] React.memo usage retrieved.
```

## Business Value
- **Limitless Codebase Understanding:** Seamlessly orchestrate open-ended repository migrations, wide-scale dependency refactoring, and comprehensive V2 rewrites without blowing up your API billing limits or context constraints.
- **The "Forever Agent":** OpenJudge never forgets. The local `.env` and SQLite storage ensure your instance of OpenJudge continuously learns the idiosyncrasies of your specific corporate infrastructure forever.

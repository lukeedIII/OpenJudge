# Use Case 2: Zero-Hallucination Data Extraction

Enterprise data extraction (financial filings, legal contracts, real-time market data) demands absolute precision. Standard LLMs are prone to confidently hallucinating numbers, dates, and legal clauses.

OpenJudge eliminates hallucination by enforcing a **Read-Verify-Extract** operating loop over live datasets.

## The Problem with Vanilla LLMs
If you provide an LLM with a 100-page SEC 10-K document and ask for the Q3 Revenue, it may accurately retrieve the data, or it may confidently hallucinate "$4.2 Billion" based on parameter weights from its pre-training data. There is no mathematical guarantee of accuracy.

## The OpenJudge Solution
OpenJudge treats data extraction as an **investigative engineering task**, not a text-generation task.

1. **Tool Injection:** Through the V3 BYOT SDK, you inject a custom tool: `search_document_db(query)`.
2. **Iterative Search:** OpenJudge uses the tool to query the exact text. Instead of guessing, it physically reads the returned JSON/Text payload.
3. **Execution Constraints:** If OpenJudge fails to trigger the `search_document_db` tool, the core Engine halts the generation with a `[ENFORCE: PIVOT]` error, refusing to let the AI output a final answer until it has physically ingested empirical data.
4. **Structured Output:** The final verifiable data is returned via the `<verdict>` XML tag, ensuring the payload matches your strict schema.

## Implementation Example (FastAPI Microservice)

Imagine an internal company dashboard asking for live financial data:

```javascript
// From your React Dashboard, hit the OpenJudge Microservice
const response = await fetch("https://api.yourcompany.com/v1/judge/execute", {
  method: "POST",
  body: JSON.stringify({
    directive: "Extract the exact Q3 operating margin from the newly uploaded AAPL_10K.pdf. You must use the 'read_file' tool to physically inspect the document before answering."
  })
});

// OpenJudge returns a JSON stream. It will NOT hallucinate the data.
// It will physically execute the file read, process the buffer, and return the empirical string.
```

## Business Value
- **Financial Compliance:** Guarantee that any metric extracted by your AI tooling actually exists verbatim in the source document.
- **Dynamic Adaptability:** Unlike fixed regex scrapers that break when a website's CSS changes, OpenJudge can visually identify the new location of a table and extract the data dynamically.

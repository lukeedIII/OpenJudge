<div align="center">
  <img src="assets/logo.svg" alt="OpenJudge Banner" width="100%">
  
  <br/>

  **Because LLMs lie. OpenJudge executes.**  
  *An empirical verification-and-enforcement loop that stops AI hallucinations dead in their tracks.*

  <br/>

  [![Python](https://img.shields.io/badge/Python-3.12+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
  [![OpenAI](https://img.shields.io/badge/OpenAI-Vision%20Ready-412991.svg?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
  [![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

</div>

<br/>

---

## ⚡ The Core Problem It Solves

Standard AI Agents suffer from **"Blind Confidence"**. They loop endlessly, hallucinate successful code implementations, and confidently claim their broken scripts run flawlessly. They believe their own text output is reality.

**OpenJudge is a supervisory enforcer that sits ABOVE the generator.** 
It operates on one ruthless principle: **Trust Nothing. Execute Everything.** It strips the LLM of its assumptions and forces it to interact with physical tools. If an AI claims "the bash script works," OpenJudge executes it. If it fails, the error is fed back to the AI as a strict state correction, forcing an immediate pivot or purge.

## 🧠 The Architecture

OpenJudge is not just a prompt; it is a full, self-healing Python runtime composed of four essential pillars:

### 1. The Strict XML Parser (`parser.py`)
Forces the LLM to structure its cognition. It strictly extracts `<state_memory>`, `<logical_extern>`, and `<verdict>`, and enforces physical action via the exact `[ENFORCE: PROCEED | PURGE | PIVOT | TERMINATE]` kill-switch syntax.

### 2. The Ledger of Truth (`state_manager.py`)
Combats context bloat and repetitive looping. It tracks the exact history of actions, logs known failures, and compiles physical tool execution outputs into a highly structured memory block injected into every prompt.

### 3. The Physical Hands (`tools.py`)
Equips the Judge with deterministic interaction. 
- 💻 **`execute_bash` / `execute_python`**: Run real code securely with subprocess timeouts.
- 📁 **`read_file` / `write_file`**: I/O manipulation.
- 🌐 **`web_search`**: DuckDuckGo integration to verify external facts against hallucinations.
- 👁 **`analyze_image`**: OpenAI Vision API integration to physically inspect pixels, verify UI components, and audit visual data.

### 4. The Self-Healing Loop (`main.py`)
A continuous autonomous loop wrapped in a `rich` terminal UI HUD. If the LLM violates the required XML format, `main.py` catches the `FormatViolationError`, injects a **System Override** into the Ledger of Truth, and seamlessly loops—forcing the AI to correct its own structure without crashing the software.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API Key (or LiteLLM compatible endpoint)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/lukeedIII/OpenJudge.git
   cd OpenJudge
   ```
2. Install the core neural and physical dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up the environment:
   ```bash
   cp .env.example .env
   # Edit .env and insert your OPENAI_API_KEY
   ```

### Execution
To test that your "Hands" (tools) are working without burning API credits:
```bash
python sanity_check.py
```

To boot the OpenJudge Autonomous Loop:
```bash
python main.py
```

## 🖥 The Observer UI HUD
We utilize the `rich` library to render the Judge's cognition in real-time.
- 🟦 **Cyan Panels**: Reveal the internal thought process (`<state_memory>`).
- 🟨 **Yellow Text**: Live execution of physical tools (bash, python, web) and their feedback.
- 🟥 **Bold Red**: Structural healing overrides, failures, or `[ENFORCE: PIVOT]` actions.
- 🟩 **Bold Green**: Successful validations and the final `[ENFORCE: TERMINATE]` operation.

<br/>

> *"Never invent acceptance criteria. Fix only what blocks criteria. Do not loop. Terminate with a clear verdict."* — **OpenJudge Prime Directive**

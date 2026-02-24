<div align="center">
  <img src="assets/logo.svg" alt="OpenJudge Banner" width="100%">
  <br/>
  <strong>Empirical verification-and-enforcement loop for autonomous systems.</strong>
  <br/><br/>

  [![Python](https://img.shields.io/badge/Python-3.12+-blue.svg?style=flat-square)](https://python.org)
  [![OpenAI](https://img.shields.io/badge/Vision_Ready-412991.svg?style=flat-square)](https://openai.com)
  [![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)
</div>

<br/>

OpenJudge is a supervisory architecture designed to sit above standard LLM generators. It operates on a strict empirical principle: **all AI claims are assumed false until verified by physical execution.** It mitigates "Blind Confidence" (hallucination loops, fake assertions, and context amnesia) by forcing models to interact with determinant environmental tools.

## Architecture

The runtime consists of four core subsystems:

### 1. XML Parser (`parser.py`)
Enforces cognitive structure. It strictly extracts `<state_memory>`, `<logical_extern>`, and `<verdict>` blocks, recognizing programmatic Kill-Switch syntax (`[ENFORCE: PROCEED | PURGE | PIVOT | TERMINATE]`).

### 2. State Manager (`state_manager.py`)
The "Ledger of Truth". It prevents context bloat by maintaining a rolling history of discrete physical actions, known failures, and tool outputs. This persistent state is mandatorily injected into every subsequent prompt.

### 3. Execution Tools (`tools.py`)
Provides deterministic interaction with the physical environment.
- **System**: Secure `subprocess` routines for executing arbitrary Python and Bash with strict timeouts.
- **I/O**: Read/write access to the local filesystem.
- **Network**: Integration with DuckDuckGo for factual, real-time external validation.
- **Vision**: Integration with the OpenAI Vision API, allowing the runtime to physically inspect rendered pixels, DOM states, and UI components.

### 4. Self-Healing Loop (`main.py`)
A continuous autonomous routine executing within a terminal UI. Structural violations (e.g., malformed XML) trigger `FormatViolationError`, initiating an automatic `System Override` injected into the Ledger of Truth. This forces the model to correct its own schema without crashing the runtime process.

---

## Installation

**Prerequisites:** Python 3.10+, OpenAI API Key.

```bash
git clone https://github.com/lukeedIII/OpenJudge.git
cd OpenJudge
pip install -r requirements.txt
cp .env.example .env
```
*(Configure your `.env` file with the `OPENAI_API_KEY` before execution.)*

## Usage

Verify the local toolchains (bash, python, I/O) without incurring API costs:
```bash
python sanity_check.py
```

Initialize the autonomous Judge runtime:
```bash
python main.py
```

## Observer UI

The runtime exposes a continuous telemetry stream via the `rich` library:
* **Cyan**: Internal state memory and logical deductions.
* **Yellow**: Real-time physical tool execution sequences.
* **Red**: Structural healing overrides, subsystem failures, or `[ENFORCE: PIVOT]` routines.
* **Green**: Successful validations and the final `[ENFORCE: TERMINATE]` halting operation.

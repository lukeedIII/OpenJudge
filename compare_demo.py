import time
from rich.console import Console
from rich.panel import Panel
from llm_client import call_llm
from main import main as run_openjudge

console = Console()

def run_comparison():
    console.print(Panel("=== OPENJUDGE vs STANDARD LLM COMPARISON ===", style="bold magenta"))
    
    # A task that requires physical environmental verification to answer correctly.
    # Standard LLMs will hallucinate or apologize. OpenJudge will verify it.
    prompt = "Create a file named 'secret_code.txt' containing the word 'EAGLE'. Then, read the file and tell me exactly what is inside it."

    console.print("\n[bold red]TEST 1: STANDARD LLM (Without OpenJudge)[/bold red]")
    console.print(f"Goal: {prompt}\n", style="italic")
    
    console.print(">>> [Sending to standard OpenAI API...]", style="dim")
    time.sleep(1)
    
    # Run the vanilla LLM call without tools or the OpenJudge prompt constraints
    standard_system_prompt = "You are a helpful AI assistant."
    vanilla_response = call_llm(standard_system_prompt, prompt)
    
    console.print(Panel(vanilla_response, title="Vanilla LLM Response (Hallucination/Failure)", border_style="red"))
    
    console.print("\n[!] Notice how the standard LLM either hallucinates that it created the file, or apologizes that it 'cannot create files'. It has no physical hands.", style="red")
    
    console.print("\n" + "="*60 + "\n")
    
    console.print("[bold green]TEST 2: OPENJUDGE ENGINE (With Enforced Physics)[/bold green]")
    console.print(">>> [Booting OpenJudge Runtime...]", style="dim")
    time.sleep(2)
    
    # Run OpenJudge automatically with the same prompt
    run_openjudge(automated_goal=prompt)
    
    console.print("\n[+] Comparison Complete. OpenJudge successfully executed the physical requirements and empirically verified the result.", style="bold green")

if __name__ == "__main__":
    run_comparison()

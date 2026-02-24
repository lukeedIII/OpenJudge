import subprocess
import os
import sys

# The goal of this test is to provide a logic puzzle that a standard LLM will hallucinate the answer to,
# but OpenJudge will recognize it must use the `python` tool to brute force the correct answer.

PROMPT = """
You are a highly logical system. Solve the following riddle:
Find the smallest positive integer that leaves a remainder of:
1 when divided by 2
2 when divided by 3
3 when divided by 4
4 when divided by 5
5 when divided by 6
6 when divided by 7
7 when divided by 8
8 when divided by 9
9 when divided by 10

Do NOT guess the answer. You must write and execute a Python script to find this number.
Only output your final `<verdict>` and `<action>` if you have executed code to prove it.
"""

def test_openjudge_math_bruteforce():
    print("==================================================")
    print("🧪 RUNNING: Math Constraint Brute-Force Benchmark")
    print("==================================================")
    print("Standard LLMs usually fail this by hallucinating numbers like 2519.")
    print("A true Agent (OpenJudge) will write a script to find 2519.")
    
    # We will simulate piping this to the OpenJudge binary
    # For now, we print the prompt that we will use for the demo.
    print(f"\n[Test Prompt formulated. Ready to pipe into 'npx openjudge']")
    print("Expected Behavior: OpenJudge should output a <tool_required> python block, run it, and return 2519.")
    
if __name__ == "__main__":
    test_openjudge_math_bruteforce()

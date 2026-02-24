import subprocess
import os
import tempfile
import traceback
import base64
from duckduckgo_search import DDGS

# Note: llm_client import is handled locally within analyze_image 
# to avoid circular dependency since llm_client might be used by main.

def execute_bash(command: str) -> str:
    """
    Executes a shell command. 
    Captures stdout and stderr, with a 30-second timeout to prevent hangs.
    """
    try:
        # We capture both stdout and stderr together or separately. 
        # Using capture_output=True handles both.
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\n--- STDERR ---\n{result.stderr}"
            
        if result.returncode != 0:
            return f"[ERROR] Command failed with return code {result.returncode}.\nOutput: {output}"
            
        return output.strip() if output.strip() else "[SUCCESS] (No output returned)"
        
    except subprocess.TimeoutExpired:
        return "[ERROR] Bash command timed out after 30 seconds."
    except Exception as e:
        return f"[FATAL ERROR] Exception during bash execution: {str(e)}\n{traceback.format_exc()}"


def execute_python(code_string: str) -> str:
    """
    Executes a Python code block by writing it to a temporary file 
    and running it in a subprocess.
    """
    temp_file_path = None
    try:
        # Create a temporary file that won't be deleted immediately upon closing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code_string)
            temp_file_path = temp_file.name

        # Execute the temporary python file
        result = subprocess.run(
            ["python", temp_file_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\n--- STDERR ---\n{result.stderr}"
            
        if result.returncode != 0:
            return f"[ERROR] Python script failed with return code {result.returncode}.\nOutput: {output}"
            
        return output.strip() if output.strip() else "[SUCCESS] (No output returned)"
        
    except subprocess.TimeoutExpired:
        return "[ERROR] Python execution timed out after 30 seconds."
    except Exception as e:
        return f"[FATAL ERROR] Exception during python execution: {str(e)}\n{traceback.format_exc()}"
    finally:
        # Ensure cleanup of the temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except OSError:
                pass


def read_file(filepath: str) -> str:
    """
    Reads the content of a file from the filesystem.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return f"[ERROR] File not found: {filepath}"
    except Exception as e:
        return f"[ERROR] Failed to read {filepath}: {str(e)}"


def write_file(filepath: str, content: str) -> str:
    """
    Writes content to a file. Overwrites if it exists.
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"[SUCCESS] Wrote to {filepath} successfully."
    except Exception as e:
        return f"[ERROR] Failed to write to {filepath}: {str(e)}"

def web_search(query: str, max_results: int = 5) -> str:
    """
    Executes a web search using DuckDuckGo and returns top text snippets.
    """
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(f"Title: {r['title']}\nSnippet: {r['body']}\nURL: {r['href']}")
                
        if not results:
            return f"[SUCCESS] No results found for query: {query}"
            
        return "\n\n".join(results)
    except Exception as e:
        return f"[ERROR] Web search failed: {str(e)}\n{traceback.format_exc()}"

def analyze_image(image_path: str, question: str) -> str:
    """
    Reads a local image, converts to Base64, and dynamically asks the Vision API for analysis.
    """
    try:
        if not os.path.exists(image_path):
            return f"[ERROR] Image not found: {image_path}"
            
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
        # Determine mime type roughly
        ext = os.path.splitext(image_path)[1].lower()
        mime = "image/png" if ext == ".png" else "image/jpeg"
        
        # Local import to prevent circular dependency
        from llm_client import call_llm
        
        sys_prompt = "You are an expert Vision API tool. Answer the user's question about the image accurately based on visual evidence."
        # Note: we pass image_base64 and mime_type to call_llm
        vision_response = call_llm(
            system_prompt=sys_prompt, 
            user_prompt=question, 
            image_base64=base64_image,
            mime_type=mime
        )
        return f"[VISION RESPONSE]\n{vision_response}"
        
        return f"[VISION RESPONSE]\n{vision_response}"
        
    except Exception as e:
        return f"[ERROR] Image analysis failed: {str(e)}\n{traceback.format_exc()}"

def git_action(repo_path: str, action: str, branch: str = "", message: str = "") -> str:
    """
    Dedicated Git Tool for safe repository orchestration.
    Actions: 'init', 'clone', 'commit', 'push', 'checkout', 'status'
    Payload format depends on action.
    """
    try:
        # Default bash execution wrapper for git commands
        def _run_git(cmd):
            res = subprocess.run(f"cd \"{repo_path}\" && {cmd}", shell=True, capture_output=True, text=True)
            if res.returncode != 0:
                raise Exception(res.stderr.strip() or "Unknown Git Error")
            return res.stdout.strip()

        if action == "status":
            return _run_git("git status")
        elif action == "init":
            return subprocess.run(f"git init \"{repo_path}\"", shell=True, capture_output=True, text=True).stdout
        elif action == "clone" and branch: # URL passed in 'branch' param for cloning
            return subprocess.run(f"git clone \"{branch}\" \"{repo_path}\"", shell=True, capture_output=True, text=True).stdout
        elif action == "checkout" and branch:
            return _run_git(f"git checkout -b \"{branch}\" || git checkout \"{branch}\"")
        elif action == "commit":
            _run_git("git add -A")
            msg = message if message else "Autonomous OpenJudge Commit"
            return _run_git(f"git commit -m \"{msg}\"")
        elif action == "push":
            return _run_git("git push origin main")
            
        return f"[ERROR] Invalid or unsupported git_action: {action}"
    except Exception as e:
        return f"[ERROR] Git Action Failed: {str(e)}"

def browser_action(url: str, action: str, selector: str = "", value: str = "") -> str:
    """
    Playwright Browser Automation Tool.
    Actions: 'goto_and_screenshot', 'extract_html', 'click', 'type'
    Note: Click/Type actions require a valid DOM selector.
    """
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            page.goto(url, wait_until="domcontentloaded")
            
            output = "[SUCCESS] Browser Action Triggered"
            
            if action == 'goto_and_screenshot':
                shot_path = f"screenshot_{os.urandom(4).hex()}.png"
                page.screenshot(path=shot_path, full_page=True)
                output = f"Screenshot saved at {shot_path}"
                
            elif action == 'extract_html':
                if selector:
                    output = page.locator(selector).inner_html()
                else:
                    output = page.content()[:3000] # Return the first 3000 chars of body
                    
            elif action == 'click' and selector:
                page.locator(selector).click()
                output = f"Clicked {selector} successfully."
                
            elif action == 'type' and selector and value:
                page.locator(selector).fill(value)
                output = f"Typed '{value}' into {selector}."
                
            browser.close()
            return output
            
    except Exception as e:
         return f"[ERROR] Browser Automation Failed: {str(e)}"

def memory_store(document: str, mem_type: str = "general") -> str:
    """
    Inserts a factual event, snippet, or codebase summary into Vector Memory (ChromaDB).
    """
    import uuid
    from memory_db import memory_db
    
    doc_id = str(uuid.uuid4())
    result = memory_db.store(action_id=doc_id, document=document, metadata={"type": mem_type})
    
    if result is True:
        return f"[SUCCESS] Stored memory fragment {doc_id} into Vector DB."
    return f"[ERROR] Failed to store memory: {result}"

def memory_query(query: str, count: str = "3") -> str:
    """
    Queries the Vector Memory (ChromaDB) for historical state using RAG semantic extraction.
    """
    from memory_db import memory_db
    try:
        num = int(count)
        return memory_db.query(search_text=query, n_results=num)
    except Exception as e:
        return f"[ERROR] Memory Query Failed: {str(e)}"

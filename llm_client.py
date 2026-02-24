import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def call_llm(system_prompt: str, user_prompt: str, model: str = "gpt-4o", image_base64: str = None, mime_type: str = "image/jpeg") -> str:
    """
    API Gateway to communicate with the generic LLM API.
    Supports standard text generation and Vision API capabilities if image_base64 is provided.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[WARNING] OPENAI_API_KEY is not set in environment or .env file.")
        
    try:
        client = OpenAI(api_key=api_key)
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if image_base64:
            # Format payload for Vision API
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_base64}"}}
                ]
            })
        else:
            # Standard Text payload
            messages.append({"role": "user", "content": user_prompt})
            
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.0  # OpenJudge must remain deterministic
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"[CRITICAL LLM API ERROR]: {str(e)}"

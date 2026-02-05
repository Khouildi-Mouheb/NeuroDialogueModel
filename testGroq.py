# Simple Groq API test - no project dependencies
import os

try:
    from groq import Groq
    
    print("🧪 Testing Groq API...\n")
    
    api_key = "REDACTED"
    client = Groq(api_key=api_key)
    
    print("📡 Sending: 'Say hello in one sentence.'\n")
    print("🤖 Response: ", end="", flush=True)
    
    completion = client.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=[
            {
                "role": "user",
                "content": "Say hello in one sentence."
            }
        ],
        temperature=0.7,
        max_tokens=100,
        stream=True
    )
    
    for chunk in completion:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    
    print("\n\n✅ Groq API works perfectly!")
    
except ImportError:
    print("❌ groq package not installed in THIS virtual environment!")
    print("\nRun: pip install groq")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
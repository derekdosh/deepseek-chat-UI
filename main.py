import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# UPDATED: Now using DeepSeek API directly
openai = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),  # Changed from DEEPINFRA_TOKEN
    base_url="https://api.deepseek.com/v1",  # Changed to DeepSeek endpoint
)

@app.get("/")
def home():
    return {"message": "✅ FastAPI + DeepSeek is running!"}

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    user_input = body.get("message", "")
    temperature = body.get("temperature", 0.7)
    # UPDATED: Using DeepSeek's official model names
    model = body.get("model", "deepseek-chat")  # Changed from DeepInfra model

    try:
        chat_completion = openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": user_input}],
            temperature=temperature,
            max_tokens=4096,  # Added max_tokens for DeepSeek
        )

        return {"response": chat_completion.choices[0].message.content}
    except Exception as e:
        return {"response": f"Error: {str(e)}"}

# Optional: Add streaming support
@app.post("/chat/stream")
async def chat_stream(request: Request):
    body = await request.json()
    user_input = body.get("message", "")
    temperature = body.get("temperature", 0.7)
    model = body.get("model", "deepseek-chat")

    try:
        stream = openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": user_input}],
            temperature=temperature,
            stream=True,  # Enable streaming
            max_tokens=4096,
        )
        
        # Return a streaming response
        from fastapi.responses import StreamingResponse
        import json
        
        async def generate():
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield json.dumps({"chunk": chunk.choices[0].delta.content}) + "\n"
        
        return StreamingResponse(generate(), media_type="application/x-ndjson")
    except Exception as e:
        return {"response": f"Error: {str(e)}"}

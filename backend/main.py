from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from deepseek_client import ask_deepseek
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS setup for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    messages: list  # List of {"role": "user"|"assistant", "content": str}

# No response model enforced, return dict for flexibility
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    response = await ask_deepseek(request.messages)
    return response

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 
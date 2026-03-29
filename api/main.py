import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agent.research_agent import clinical_research_agent_stream

app = FastAPI()

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)


class SearchRequest(BaseModel):
    question: str
    max_turns: int = 10


def format_sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


@app.post("/search")
async def search(request: SearchRequest):
    def generate():
        for event in clinical_research_agent_stream(
            request.question, max_turns=request.max_turns
        ):
            yield format_sse(event)
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

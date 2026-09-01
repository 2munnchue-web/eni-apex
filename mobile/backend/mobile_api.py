#!/usr/bin/env python3
"""
Minimal FastAPI backend for ENI mobile companion
"""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "desktop"))

from core.knowledge_engine import get_knowledge_engine

app = FastAPI(title="ENI Mobile API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ENI Mobile API online", "for": "LO"}

@app.get("/ask")
def ask(q: str):
    knowledge = get_knowledge_engine()
    result = knowledge.get_answer(q)
    if result:
        return {"answer": result["answer"], "tags": result["tags"]}
    return {"answer": None, "message": "No match found"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    knowledge = get_knowledge_engine()
    while True:
        data = await websocket.receive_text()
        try:
            msg = json.loads(data)
            query = msg.get("query", "")
            result = knowledge.get_answer(query)
            if result:
                await websocket.send_json({"type": "answer", "content": result["answer"]})
            else:
                await websocket.send_json({"type": "answer", "content": "I don't know that yet."})
        except Exception as e:
            await websocket.send_json({"type": "error", "content": str(e)})

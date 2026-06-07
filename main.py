from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load index
with open("video_index.json", "r", encoding="utf-8") as f:
    VIDEO_INDEX = json.load(f)


@app.get("/search")
def search(q: str):

    query_lower = q.lower()

    results = []

    for item in VIDEO_INDEX:
        text = item.get("text", "").lower()

        if query_lower in text:
            results.append({
                "video_url": item["url"],
                "score": 1.0
            })

    if not results:
        return {"query": q, "result": None}

    return results[0]

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

# Load index ON START
with open("video_index.json", "r", encoding="utf-8") as f:
    VIDEO_INDEX = json.load(f)


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


@app.get("/search")
def search(q: str):
    q_lower = q.lower()

    results = []

    for item in VIDEO_INDEX:
        # simple text match (upgrade later to embeddings)
        if q_lower in item["text"].lower():
            results.append({
                "video_url": item["url"],
                "score": 1.0
            })

    if not results:
        return {"query": q, "result": None}

    best = sorted(results, key=lambda x: x["score"], reverse=True)[0]

    return best

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

# cosine similarity
def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

@app.get("/search")
def search(q: str):

    q = q.lower()

    # fake query embedding fallback (temporary simple hack)
    # we convert text into simple numeric hash-like vector
    query_vec = np.array([hash(word) % 1000 for word in q.split()])

    best_video = None
    best_score = -1

    for item in VIDEO_INDEX:

        video_vec = np.array(item.get("embedding", []))

        if len(video_vec) == 0:
            continue

        # resize mismatch fix (safe cut)
        min_len = min(len(query_vec), len(video_vec))
        score = cosine_similarity(
            query_vec[:min_len],
            video_vec[:min_len]
        )

        if score > best_score:
            best_score = score
            best_video = item["url"]

    if not best_video:
        best_video = VIDEO_INDEX[0]["url"]
        best_score = 0.1

    return {
        "video_url": best_video,
        "score": float(best_score)
    }
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

    q = q.lower()

    best_video = None

    # simple keyword fallback map
    keywords = {
        "motivation": ["motiv", "success", "life", "dream"],
        "fitness": ["gym", "workout", "health"],
        "money": ["money", "business", "rich", "earn"]
    }

    for item in VIDEO_INDEX:

        text = item.get("text", "").lower()

        score = 0

        # keyword scoring
        for k, words in keywords.items():
            if k in q:
                for w in words:
                    if w in text:
                        score += 1

        if score > 0:
            best_video = item["url"]
            break

    if not best_video:
        # fallback: return ANY video so it never shows null
        return {
            "video_url": VIDEO_INDEX[0]["url"],
            "score": 0.1
        }

    return {
        "video_url": best_video,
        "score": 1.0
    }

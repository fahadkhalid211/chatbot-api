from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import json
import numpy as np
from vertexai.language_models import TextEmbeddingModel
import vertexai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CONFIG & INIT
PROJECT_ID = "project-6ddfbc9f-8e2e-42c9-973"
LOCATION = "us-central1"

vertexai.init(project=PROJECT_ID, location=LOCATION)
model = TextEmbeddingModel.from_pretrained("text-embedding-004")

with open("video_index.json", "r", encoding="utf-8") as f:
    VIDEO_INDEX = json.load(f)

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def home():
    return FileResponse("index.html")

@app.get("/search")
def search(q: str):
    if not q.strip():
        return {"results": [], "error": "Empty query"}

    query_embedding = model.get_embeddings([q])[0].values

    matches = []

    for item in VIDEO_INDEX:
        if "embedding" not in item or not item["embedding"]:
            continue
        score = cosine_similarity(query_embedding, item["embedding"])
        matches.append({
            "video_url": item["url"],
            "transcript": item.get("text", "")[:250] + "...",
            "score": float(score)
        })

    # Sort by score and take top 3 (no strict threshold for now)
    matches = sorted(matches, key=lambda x: x["score"], reverse=True)[:3]

    return {"results": matches}
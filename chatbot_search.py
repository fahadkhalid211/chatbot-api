import json
from vertexai.language_models import TextEmbeddingModel
import vertexai
import numpy as np

PROJECT_ID = "project-6ddfbc9f-8e2e-42c9-973"
LOCATION = "us-central1"

vertexai.init(project=PROJECT_ID, location=LOCATION)

model = TextEmbeddingModel.from_pretrained("text-embedding-004")

# Load your index
with open("video_index.json", "r") as f:
    data = json.load(f)

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def search_video(query):
    query_embedding = model.get_embeddings([query])[0].values

    best_match = None
    best_score = -1

    for item in data:
        score = cosine_similarity(query_embedding, item["embedding"])

        if score > best_score:
            best_score = score
            best_match = item

    return best_match, best_score


# ---- TEST ----
while True:
    q = input("\nAsk something: ")

    result, score = search_video(q)

    print("\nBest Video:")
    print(result["url"])
    print("Score:", score)
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
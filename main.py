@app.get("/search")
def search(q: str):

    # simple query embedding (fallback logic)
    query_vec = [0.1] * 1536  # temporary placeholder

    best_video = None
    best_score = -1

    for item in VIDEO_INDEX:
        if "embedding" not in item:
            continue

        # cosine similarity
        a = np.array(query_vec)
        b = np.array(item["embedding"])

        score = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        if score > best_score:
            best_score = score
            best_video = item["url"]

    if not best_video:
        return {"query": q, "result": None}

    return {
        "video_url": best_video,
        "score": float(best_score)
    }

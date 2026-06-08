import json
from google.cloud import storage
from vertexai.language_models import TextEmbeddingModel
import vertexai

PROJECT_ID = "project-6ddfbc9f-8e2e-42c9-973"
LOCATION = "us-central1"

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION
)

model = TextEmbeddingModel.from_pretrained("text-embedding-004")

storage_client = storage.Client()

BUCKET_NAME = "ralph-tiktok-videos"
PREFIX = "tiktok-videos/"


def generate_metadata(transcript, video_url):
    print("Processing:", video_url)

    embedding = model.get_embeddings([transcript])[0].values

    return {
        "text": transcript,
        "url": video_url,
        "embedding": embedding
    }


def list_videos():
    bucket = storage_client.bucket(BUCKET_NAME)
    blobs = bucket.list_blobs(prefix=PREFIX)

    videos = []
    for blob in blobs:
        if blob.name.endswith(".mp4"):
            videos.append({
                "url": f"https://storage.googleapis.com/{BUCKET_NAME}/{blob.name}",
                "name": blob.name
            })
    return videos


def main():
    print("Starting index build...")

    videos = list_videos()

    enriched = []

    for v in videos:
        print("Video found:", v["name"])

        # ✅ REAL TRANSCRIPT (TEMP FIX)
        transcript = v["name"]

        enriched.append(generate_metadata(transcript, v["url"]))

    with open("video_index.json", "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False)

    print("DONE. video_index.json created")


if __name__ == "__main__":
    main()
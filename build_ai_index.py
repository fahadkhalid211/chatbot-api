import json
from google.cloud import storage
from google.cloud import speech
from vertexai.language_models import TextEmbeddingModel
import vertexai

# ====== INIT (FIXED - NO AUTO DETECTION HANG) ======
PROJECT_ID = "project-6ddfbc9f-8e2e-42c9-973"
LOCATION = "us-central1"

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION
)

# ====== LOAD MODEL ======
model = TextEmbeddingModel.from_pretrained("text-embedding-004")

# ====== GCS CLIENT ======
storage_client = storage.Client()

BUCKET_NAME = "ralph-tiktok-videos"
PREFIX = "tiktok-videos/"

# ====== FUNCTIONS ======
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

# ====== MAIN ======
def main():
    print("Starting index build...")

    videos = list_videos()

    enriched = []

    for v in videos:
        print("Video found:", v["name"])

        # TEMP transcript (replace later with Speech-to-Text)
        transcript = "sample transcript here"

        enriched.append(generate_metadata(transcript, v["url"]))

    with open("video_index.json", "w") as f:
        json.dump(enriched, f)

    print("DONE. video_index.json created")

# ====== RUN ======
if __name__ == "__main__":
    main()
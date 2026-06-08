import json
import os
import subprocess

from google.cloud import storage
from google.cloud import speech
from vertexai.language_models import TextEmbeddingModel
import vertexai

# ======================
# CONFIG
# ======================
PROJECT_ID = "project-6ddfbc9f-8e2e-42c9-973"
LOCATION = "us-central1"

BUCKET_NAME = "ralph-tiktok-videos"
PREFIX = "tiktok-videos/"

LOCAL_DIR = "temp_audio"

# ======================
# INIT
# ======================
vertexai.init(project=PROJECT_ID, location=LOCATION)

model = TextEmbeddingModel.from_pretrained("text-embedding-004")

storage_client = storage.Client()
speech_client = speech.SpeechClient()


# ======================
# AUDIO EXTRACTION
# ======================
def extract_audio(mp4_path, wav_path):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", mp4_path,
        "-ar", "16000",
        "-ac", "1",
        wav_path
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ======================
# SPEECH TO TEXT
# ======================
def transcribe_gcs_audio(gcs_uri):
    audio = speech.RecognitionAudio(uri=gcs_uri)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    operation = speech_client.long_running_recognize(
        config=config,
        audio=audio
    )

    print("Transcribing:", gcs_uri)

    response = operation.result(timeout=600)

    transcript = ""

    for result in response.results:
        transcript += result.alternatives[0].transcript + " "

    return transcript.strip()


# ======================
# EMBEDDINGS
# ======================
def generate_metadata(transcript, video_url):
    embedding = model.get_embeddings([transcript])[0].values

    return {
        "text": transcript,
        "url": video_url,
        "embedding": embedding
    }


# ======================
# MAIN
# ======================
def main():
    print("Starting index build...")

    # ✅ FIX: ensure folder exists
    os.makedirs(LOCAL_DIR, exist_ok=True)

    bucket = storage_client.bucket(BUCKET_NAME)
    blobs = list(bucket.list_blobs(prefix=PREFIX))

    print("TOTAL FILES FOUND:", len(blobs))

    enriched = []

    for blob in blobs:
        print("Found:", blob.name)

        if not blob.name.endswith(".mp4"):
            continue

        print("Processing video:", blob.name)

        mp4_path = f"{LOCAL_DIR}/temp.mp4"
        wav_path = f"{LOCAL_DIR}/temp.wav"

        # download mp4
        blob.download_to_filename(mp4_path)

        # extract audio
        extract_audio(mp4_path, wav_path)

        # upload wav
        wav_blob_name = blob.name.replace(".mp4", ".wav")
        wav_blob = bucket.blob(wav_blob_name)
        wav_blob.upload_from_filename(wav_path)

        gcs_audio_uri = f"gs://{BUCKET_NAME}/{wav_blob_name}"

        # speech-to-text
        transcript = transcribe_gcs_audio(gcs_audio_uri)

        enriched.append(
            generate_metadata(
                transcript,
                f"https://storage.googleapis.com/{BUCKET_NAME}/{blob.name}"
            )
        )

    with open("video_index.json", "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)

    print("DONE. video_index.json created with", len(enriched), "items")


if __name__ == "__main__":
    main()
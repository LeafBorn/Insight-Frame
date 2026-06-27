from utils.audio_processor import process_youtube_audio
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions

url = 'https://www.youtube.com/watch?v=ZpPiZiqWjyA'

result = process_youtube_audio(
    youtube_url=url,
    chunk_length_ms=600000  # 1 minute
)

print("\nChunks:")
for chunk in result["chunks"]:
    print(chunk)

print("\nStarting transcription...\n")

transcript = transcribe_all(result["chunks"])

print("\n===== TRANSCRIPT =====\n")
print(transcript)


title = generate_title(transcript)
summary = summarize(transcript)

print("\n" + "=" * 60)
print(f"📌 TITLE: {title}")
print("=" * 60)
print("\n📋 SUMMARY")
print("-" * 60)
print(summary)


action_items = extract_action_items(transcript)
decisions = extract_key_decisions(transcript)
questions = extract_questions(transcript)

print("\n" + "=" * 60)
print("✅ ACTION ITEMS")
print("=" * 60)
print(action_items)

print("\n" + "=" * 60)
print("🔑 KEY DECISIONS")
print("=" * 60)
print(decisions)

print("\n" + "=" * 60)
print("❓ OPEN QUESTIONS")
print("=" * 60)
print(questions)

from youtube_transcript_api import YouTubeTranscriptApi

video_id = 'dQw4w9WgXcQ'
try:
    print("Trying YouTubeTranscriptApi.fetch(video_id)...")
    # Some versions have it as a classmethod, some as instance
    # Let's try instance first if it has self
    api = YouTubeTranscriptApi()
    transcript = api.fetch(video_id)
    print(f"Success! Fetched {len(transcript)} lines.")
except Exception as e:
    print(f"Instance fetch failed: {e}")
    try:
        print("Trying YouTubeTranscriptApi.get_transcript(video_id)...")
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        print(f"Success! Fetched {len(transcript)} lines.")
    except Exception as e2:
        print(f"Class fetch failed: {e2}")

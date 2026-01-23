from youtube_transcript_api import YouTubeTranscriptApi
import inspect

print(f"Type: {type(YouTubeTranscriptApi)}")
print(f"Members: {[m[0] for m in inspect.getmembers(YouTubeTranscriptApi)]}")

try:
    # Standard way
    print(f"Has get_transcript: {hasattr(YouTubeTranscriptApi, 'get_transcript')}")
    # Another way
    print(f"Has list_transcripts: {hasattr(YouTubeTranscriptApi, 'list_transcripts')}")
except Exception as e:
    print(f"Error checking: {e}")

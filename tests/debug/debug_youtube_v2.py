from youtube_transcript_api import YouTubeTranscriptApi
import inspect

print("--- Help on YouTubeTranscriptApi.list ---")
print(inspect.signature(YouTubeTranscriptApi.list))
print(YouTubeTranscriptApi.list.__doc__)

print("\n--- Help on YouTubeTranscriptApi.fetch ---")
print(inspect.signature(YouTubeTranscriptApi.fetch))
print(YouTubeTranscriptApi.fetch.__doc__)

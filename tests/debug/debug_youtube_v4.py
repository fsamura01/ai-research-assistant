from youtube_transcript_api import YouTubeTranscriptApi

video_id = 'dQw4w9WgXcQ'
try:
    api = YouTubeTranscriptApi()
    transcript_list = api.fetch(video_id)
    snippet = transcript_list[0]
    print(f"Snippet Type: {type(snippet)}")
    print(f"Snippet attributes: {[m for m in dir(snippet) if not m.startswith('_')]}")
    
    # Try accessing text
    if hasattr(snippet, 'text'):
        print(f"Text via attribute: {snippet.text[:50]}")
    else:
        print("No .text attribute found!")

except Exception as e:
    print(f"Failed: {e}")

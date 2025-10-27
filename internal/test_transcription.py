#!/usr/bin/env python3

from echoes_modules.youtube_transcriber import transcribe_youtube_video

def test_transcription():
    url = 'https://www.youtube.com/watch?v=wLb9g_8r-mE&t=1434s'
    try:
        result = transcribe_youtube_video(url)
        print(f"SUCCESS: Report saved to {result}")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    test_transcription()

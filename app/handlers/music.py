# GENAI_ASSISTANT/app/handlers/music.py

from ytmusicapi import YTMusic
import webbrowser

ytmusic = YTMusic()

def handle_music(query: str) -> str:
    print(f"[Music Handler] → 🎵 Playing music in the other tab")
    
    search_results = ytmusic.search(query, filter="songs")
    
    if not search_results:
        return "❌ No music found for your query."

    # picking the first result
    top_result = search_results[0]
    video_id = top_result.get('videoId')

    if not video_id:
        return "❌ Unable to fetch video link."
    
    lower_query = query.lower()
    if "mp4" in lower_query or "video" in lower_query:
        # YouTube video
        url = f"https://www.youtube.com/watch?v={video_id}"
        webbrowser.open(url)
        return f"🎬 Playing YouTube video in the other tab"
    else:
        # youTube Music by default
        url = f"https://music.youtube.com/watch?v={video_id}"
        webbrowser.open(url)
        return f"🎵 Playing music in the other tab"

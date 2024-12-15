from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp

def extract_video_id(url):
    """從 URL 中提取影片 ID"""
    try:
        if "youtu.be/" in url:
            video_id = url.split("youtu.be/")[1].split("?")[0]
            print(f"Extracted ID from youtu.be URL: {video_id}")
            return video_id
        elif "youtube.com" in url:
            if "v=" in url:
                video_id = url.split("v=")[1].split("&")[0]
                print(f"Extracted ID from youtube.com URL: {video_id}")
                return video_id
        return url
    except Exception as e:
        print(f"Error in extract_video_id: {str(e)}")
        return None

def get_video_info(url):
    """獲取影片資訊"""
    try:
        video_id = extract_video_id(url)
        if not video_id:
            return None

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            return {
                'title': info.get('title', ''),
                'description': info.get('description', ''),
                'duration': info.get('duration', 0),
                'video_id': video_id
            }
    except Exception as e:
        print(f"Error in get_video_info: {str(e)}")
        return None

def download_subtitle(url, language='zh-TW'):
    """下載字幕"""
    try:
        video_id = extract_video_id(url)
        print(f"Trying to get subtitles for video: {video_id}")
        
        # 嘗試直接獲取指定語言的字幕
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
            print(f"Successfully got {language} subtitles")
        except:
            # 如果失敗，嘗試獲取英文字幕並翻譯
            print(f"Failed to get {language} subtitles, trying English...")
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            print("Got English subtitles")

        # 格式化字幕
        formatted_transcript = []
        for entry in transcript:
            formatted_transcript.append({
                'start': entry['start'],
                'duration': entry['duration'],
                'text': entry['text']
            })
        return formatted_transcript

    except Exception as e:
        print(f"Error in download_subtitle: {str(e)}")
        return None
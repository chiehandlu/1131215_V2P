from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
from deep_translator import GoogleTranslator

LANGUAGE_MAPPINGS = {
    'zh-TW': ['zh-Hant', 'zh-TW', 'zh-HK', 'zh'],
    'en': ['en', 'en-US', 'en-GB'],
    # Add more mappings
}

CHINESE_CODES = [
    'zh', 'zh-Hans', 'zh-Hant',  # 簡體/繁體
    'zh-CN', 'zh-SG',  # 中國大陸/新加坡
    'zh-TW', 'zh-HK'   # 台灣/香港
]

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

def download_subtitle(url, language='zh-TW', auto_translate=True):
    """下載字幕"""
    try:
        video_id = extract_video_id(url)
        print(f"Trying to get subtitles for video: {video_id}")
        
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        available_transcripts = [tr.language_code for tr in transcript_list]
        print(f"Available transcripts: {available_transcripts}")

        # Try to get the requested language directly
        try:
            transcript = transcript_list.find_transcript([language])
            print(f"Found transcript in {language}")
            return format_transcript(transcript.fetch())
        except:
            print(f"No transcript found in {language}")

        # If auto_translate is True and we couldn't get the requested language, try English and translate
        if auto_translate:
            try:
                en_transcript = transcript_list.find_transcript(['en'])
                print("Found English transcript, translating...")
                en_subtitles = format_transcript(en_transcript.fetch())
                return translate_subtitles(en_subtitles, target_lang=language)
            except Exception as e:
                print(f"Error translating from English: {str(e)}")

        # If we still don't have subtitles, try the first available language
        if available_transcripts:
            first_lang = available_transcripts[0]
            print(f"Falling back to first available language: {first_lang}")
            transcript = transcript_list.find_transcript([first_lang])
            subtitles = format_transcript(transcript.fetch())
            if auto_translate and first_lang != language:
                print(f"Translating from {first_lang} to {language}")
                return translate_subtitles(subtitles, target_lang=language)
            return subtitles

        print("No subtitles found")
        return None

    except Exception as e:
        print(f"Error in download_subtitle: {str(e)}")
        return None

def format_transcript(transcript):
    """格式化字幕"""
    return [{
        'start': entry['start'],
        'duration': entry['duration'],
        'text': entry['text']
    } for entry in transcript]

def download_translated_subtitle(url, target_language='zh-TW'):
    """下載並翻譯字幕"""
    try:
        video_id = extract_video_id(url)
        print(f"Trying to get translated subtitles for video: {video_id}")
        
        transcript = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try to get English subtitles first
        try:
            en_transcript = transcript.find_transcript(['en'])
            source_language = 'en'
        except:
            # If no English subtitles, use the first available language
            en_transcript = transcript.find_generated_transcript()
            source_language = en_transcript.language_code
        
        # Get the transcript and format it
        original_transcript = format_transcript(en_transcript.fetch())
        
        # Translate the formatted transcript
        translated_transcript = translate_subtitles(original_transcript, target_language)
        
        return translated_transcript, source_language

    except Exception as e:
        print(f"Error in download_translated_subtitle: {str(e)}")
        return None, None

def download_subtitle_with_ytdlp(url, language='zh-TW'):
    """使用 yt-dlp 下載字幕"""
    try:
        video_id = extract_video_id(url)
        print(f"Trying to get subtitles for video: {video_id}")

        ydl_opts = {
            'writesubtitles': True,
            'subtitleslangs': [language, 'en'],
            'writeautomaticsub': True,
            'skip_download': True,
            'outtmpl': '%(title)s.%(ext)s',
            'subtitlesformat': 'vtt',  # 或 'srt'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                
                # 打印所有可用的字幕信息
                print("\n可用的字幕：")
                if 'subtitles' in info:
                    print("手動字幕:", list(info['subtitles'].keys()))
                if 'automatic_captions' in info:
                    print("自動字幕:", list(info['automatic_captions'].keys()))

                # 按優先順序尋找字幕
                subtitle_sources = [
                    (info.get('subtitles', {}), language, "手動字幕"),
                    (info.get('automatic_captions', {}), language, "自動字幕"),
                    (info.get('subtitles', {}), 'en', "英文手動字幕"),
                    (info.get('automatic_captions', {}), 'en', "英文自動字幕")
                ]

                for source, lang, source_type in subtitle_sources:
                    if lang in source:
                        print(f"\n找到 {source_type} ({lang})")
                        subtitle_info = source[lang]
                        # 打印字幕格式選項
                        print(f"可用格式: {[fmt['ext'] for fmt in subtitle_info]}")
                        return subtitle_info

                print("\n未找到合適的字幕")
                return None

            except Exception as e:
                print(f"提取信息時出錯: {str(e)}")
                return None

    except Exception as e:
        print(f"下載字幕時出錯: {str(e)}")
        return None

def get_subtitles(url, language='zh-TW'):
    """Try multiple methods to get subtitles"""
    # First try YouTube Transcript API
    subtitles = download_subtitle(url, language)
    if subtitles:
        return subtitles
        
    # If that fails, try yt-dlp
    print("Falling back to yt-dlp method")
    return download_subtitle_with_ytdlp(url, language)

def try_multiple_language_codes(url, primary_language):
    """Try multiple language codes for the same language"""
    for lang_code in LANGUAGE_MAPPINGS.get(primary_language, [primary_language]):
        subtitles = download_subtitle(url, lang_code)
        if subtitles:
            return subtitles
    return None

def translate_subtitles(subtitles, target_lang='zh-TW'):
    print(f"Translating subtitles to {target_lang}")
    translator = GoogleTranslator(source='auto', target=target_lang)
    translated_subs = []
    
    for sub in subtitles:
        try:
            translated_text = translator.translate(sub['text'])
            translated_subs.append({
                'start': sub['start'],
                'duration': sub['duration'],
                'text': translated_text
            })
        except Exception as e:
            print(f"Translation error: {str(e)}")
            translated_subs.append(sub)
    
    print(f"Translated {len(translated_subs)} subtitles")
    return translated_subs

# 測試代碼
if __name__ == "__main__":
    # 測試 URL
    test_urls = [
        "https://www.youtube.com/watch?v=K1uuK4QdvGY",
        # 可以添加更多測試 URL
    ]
    
    for url in test_urls:
        print(f"\n測試 URL: {url}")
        print("開始下載字幕...")
        
        # 嘗試不同的語言代碼
        languages = ['zh-Hant', 'zh-TW', 'zh-HK', 'zh']
        
        for lang in languages:
            print(f"\n嘗試語言: {lang}")
            subtitles = get_subtitles(url, language=lang)
            
            if subtitles:
                print(f"\n成功獲取 {lang} 字幕資訊：")
                if isinstance(subtitles, list):
                    for fmt in subtitles[:2]:
                        print(f"格式: {fmt.get('ext', 'unknown')}")
                        print(f"URL: {fmt.get('url', 'no url')[:100]}...")
                break  # 如果找到可用字幕就停止嘗試其他語言
            else:
                print(f"\n無法獲取 {lang} 字幕")
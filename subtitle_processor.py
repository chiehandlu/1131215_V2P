import streamlit as st

def convert_subtitle(subtitle_content, output_format):
    """將字幕轉換為指定格式"""
    if not subtitle_content:
        return ""
    
    result = []
    if output_format == "TXT":
        # 純文字格式，只包含文字內容
        for item in subtitle_content:
            result.append(item['text'])
        return "\n".join(result)
    
    elif output_format == "SRT":
        # SRT 格式包含時間戳記
        for i, item in enumerate(subtitle_content, 1):
            start_time = format_time(item['start'])
            end_time = format_time(item['start'] + item['duration'])
            result.extend([
                str(i),
                f"{start_time} --> {end_time}",
                item['text'],
                ""
            ])
        return "\n".join(result)
    
    elif output_format == "CSV":
        # CSV 格式，包含時間戳記和文字
        result.append("start,end,text")
        for item in subtitle_content:
            start_time = format_time(item['start'])
            end_time = format_time(item['start'] + item['duration'])
            result.append(f"{start_time},{end_time},{item['text']}")
        return "\n".join(result)

def edit_subtitle(subtitle_content):
    """編輯字幕內容"""
    # 如果輸入是字串，直接返回
    if isinstance(subtitle_content, str):
        return subtitle_content
    
    # 如果是列表，轉換為可編輯的文字格式
    result = []
    for item in subtitle_content:
        if isinstance(item, dict):
            result.append(item['text'])
    return "\n".join(result)

def format_time(seconds):
    """將秒數轉換為 HH:MM:SS,mmm 格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"
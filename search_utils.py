def search_keywords(subtitles, query):
    results = []
    for subtitle in subtitles:
        for line in subtitle['content']:
            if query.lower() in line['text'].lower():
                results.append({
                    'video_title': subtitle['video_title'],
                    'timestamp': line['start'],
                    'content': line['text']
                })
    return results

def generate_timestamps(search_results):
    timestamps = []
    for result in search_results:
        timestamps.append(f"{result['video_title']} - {format_time(result['timestamp'])}")
    return timestamps

def format_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d}" 
import json

DATABASE_FILE = "subtitle_database.json"

def save_to_database(video_info, subtitle, language):
    data = {
        'video_info': video_info,
        'subtitle': subtitle,
        'language': language
    }
    
    try:
        with open(DATABASE_FILE, 'r') as f:
            database = json.load(f)
    except FileNotFoundError:
        database = []
    
    database.append(data)
    
    with open(DATABASE_FILE, 'w') as f:
        json.dump(database, f)

def load_from_database(video_title=None):
    try:
        with open(DATABASE_FILE, 'r') as f:
            database = json.load(f)
        
        if video_title:
            for entry in database:
                if entry['video_info']['title'] == video_title:
                    return entry['subtitle']
        else:
            return [entry['video_info']['title'] for entry in database]
    except FileNotFoundError:
        return [] 
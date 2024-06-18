from googleapiclient.discovery import build
import re
import json

def get_video_details(video_url, api_key):
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Extraer el ID del video de la URL
    video_id = re.search(r'v=([^&]+)', video_url).group(1)
    
    # Obtener los detalles del video
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=video_id
    )
    response = request.execute()

    return response['items'][0]

def create_index(video_data):
    # Extraer información relevante
    title = video_data['snippet']['title']
    description = video_data['snippet']['description']
    channel_title = video_data['snippet']['channelTitle']
    published_at = video_data['snippet']['publishedAt']
    view_count = video_data['statistics'].get('viewCount', 'N/A')
    like_count = video_data['statistics'].get('likeCount', 'N/A')

    # Crear un índice con la información
    index = {
        'title': title,
        'description': description,
        'channel_title': channel_title,
        'published_at': published_at,
        'view_count': view_count,
        'like_count': like_count
    }

    return index

def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    video_url = 'https://www.youtube.com/watch?v=nbj88pzHUMM&t=5603s'
    api_key = 'TU_CLAVE_DE_API'  # Reemplaza esto con tu clave de API de YouTube
    
    video_data = get_video_details(video_url, api_key)
    index = create_index(video_data)
    
    save_to_json(index, 'video_details.json')
    print("Datos del video guardados en video_details.json")

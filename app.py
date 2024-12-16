import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

API_KEY = 'key'

def get_channel_id(api_key, custom_url):
    base_url = 'https://www.googleapis.com/youtube/v3/search'
    username = custom_url.split('/')[-1]
    
    # Check if the URL contains the '@' symbol, indicating a YouTube handle
    if '@' in username:
        username = username[1:]  # Remove the '@' symbol
    url = f'{base_url}?key={api_key}&q={username}&type=channel&part=id'

    response = requests.get(url)
    data = response.json()
    
    if 'items' in data and len(data['items']) > 0:
        return data['items'][0]['id']['channelId']
    else:
        return None

def get_video_links(api_key, channel_id):
    base_url = 'https://www.googleapis.com/youtube/v3/search'
    url = f'{base_url}?key={api_key}&channelId={channel_id}&part=snippet,id&order=date&maxResults=50'

    video_links = []

    while True:
        response = requests.get(url)
        data = response.json()

        for item in data['items']:
            if item['id']['kind'] == 'youtube#video':
                video_links.append(item['id']['videoId'])

        if 'nextPageToken' in data:
            next_page_token = data['nextPageToken']
            url = f'{base_url}?key={api_key}&channelId={channel_id}&part=snippet,id&order=date&pageToken={next_page_token}&maxResults=50'
        else:
            break

    return video_links

def get_video_details(api_key, video_id):
    url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={video_id}&key={api_key}'
    response = requests.get(url)
    data = response.json()

    if 'items' in data and len(data['items']) > 0:
        item = data['items'][0]
        snippet = item['snippet']
        statistics = item['statistics']
        return {
            'title': snippet['title'],
            'views': int(statistics.get('viewCount', 0)),
            'likes': int(statistics.get('likeCount', 0)),
            'comments': int(statistics.get('commentCount', 0))
        }
    else:
        return None

def main(custom_url):
    channel_id = get_channel_id(API_KEY, custom_url)
    if channel_id:
        video_links = get_video_links(API_KEY, channel_id)
        video_data_list = []

        for video_id in video_links:
            video_data = get_video_details(API_KEY, video_id)
            if video_data:
                video_data_list.append(video_data)

        df = pd.DataFrame(video_data_list)

        df.to_csv('youtube_video_data.csv', index=False)

        plt.figure(figsize=(10, 6))
        sns.barplot(x='title', y='views', data=df)
        plt.xticks(rotation=90)
        plt.title('Views per Video')
        plt.show()
    else:
        print("Channel ID not found.")

if __name__ == "__main__":
    custom_url = 'https://www.youtube.com/@khaledarman6407'  # Replace with your desired channel URL
    main(custom_url)

import requests 
import base64
import random
import matplotlib.pyplot as plt 
import numpy as np 
import seaborn as sns 
import streamlit as st
from PIL import Image  


def get_token(clientId,clientSecret):
    url = "https://accounts.spotify.com/api/token"
    headers = {}
    data = {}
    message = f"{clientId}:{clientSecret}"
    messageBytes = message.encode('ascii')
    base64Bytes = base64.b64encode(messageBytes)
    base64Message = base64Bytes.decode('ascii')
    headers['Authorization'] = "Basic " + base64Message
    data['grant_type'] = "client_credentials"
    r = requests.post(url, headers=headers, data=data)
    token = r.json()['access_token']
    return token


def filter_unpopular_songs(results, popularity_threshold=30):
    """Filter tracks with popularity below the given threshold."""
    filtered_tracks = []
    for track in results['tracks']['items']:
        if track['popularity'] < popularity_threshold:
            filtered_tracks.append(track)
    return filtered_tracks



def get_genre_tracks(genres, sp_client, num_tracks=5):
    """Get tracks from different genres."""
    genre_tracks = {}
    for genre in genres:
        results = sp_client.search(q='genre:' + genre, type='track', limit=num_tracks)
        genre_tracks[genre] = results['tracks']['items']
    return genre_tracks

def get_track_recommendations_v3(seed_tracks, token, genres=None, target_popularity=random.randint(1,50)):
    limit = 10
    recUrl = f"https://api.spotify.com/v1/recommendations?limit={limit}&seed_tracks={seed_tracks}"
    
    if genres:
        recUrl += f"&seed_genres={','.join(genres)}"
    
    recUrl += f"&target_popularity={target_popularity}"

    headers = {
        "Authorization": "Bearer " + token
    }

    res = requests.get(url=recUrl, headers=headers)
    if res.status_code != 200:
        raise Exception(f"Spotify API Error: {res.json()}")
    return res.json()

def get_track_recommendations(seed_tracks,token,target_popularity = random.randint(1,50)):
    limit = 10
    recUrl = f"https://api.spotify.com/v1/recommendations?limit={limit}&seed_tracks={seed_tracks}"

    recUrl += f"&target_popularity={target_popularity}"

    headers = {
        "Authorization": "Bearer " + token
    }

    res = requests.get(url=recUrl, headers=headers)
    return res.json()


def music_recommendation_viz(reco_df):

    reco_df['duration_min'] = round(reco_df['duration_ms'] / 1000, 0)
    reco_df["popularity_range"] = reco_df["popularity"] - (reco_df['popularity'].min() - 1)
    
    plt.figure(figsize=(15, 6), facecolor=(.9, .9, .9))    

    x = reco_df['name']
    y = reco_df['duration_min']
    s = reco_df['popularity_range']*20
        
    color_labels = reco_df['explicit'].unique()
    rgb_values = sns.color_palette("Set1", 8)
    color_map = dict(zip(color_labels, rgb_values))

    plt.scatter(x, y, s, alpha=0.7, c=reco_df['explicit'].map(color_map))
    plt.xticks(rotation=90)
    plt.legend()
    # show the graph
    plt.show()

    st.pyplot(plt)




def save_album_image(img_url, track_id):
    r = requests.get(img_url)
    open('Images/'+ track_id + '.jpg', "wb").write(r.content)

def get_album_image(track_id):
    return Image.open("Images/" + track_id +'.jpg')
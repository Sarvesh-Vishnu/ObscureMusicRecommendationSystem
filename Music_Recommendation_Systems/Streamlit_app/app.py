# Importing Libraries
import spotipy
import pandas as pd 
import streamlit as st
import polar_plot
import music_recommendations
from spotipy.oauth2 import SpotifyClientCredentials 
from PIL import Image

# Establishing Connections to Spotify API and instantiating Object 
Spotify_Client_ID = '3f171623fda2487bb16422c30f7983e6'
Spotify_Client_Secret = '08867663d6fd4aff8f53ff44ce1711c6'

auth_manager = SpotifyClientCredentials(client_id = Spotify_Client_ID, client_secret = Spotify_Client_Secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# App Development 

# Design

display_image = Image.open('MR_GN.png')
st.set_page_config(page_title='Obscure Music Recommendations',page_icon=display_image,layout='wide')
st.header('Obscure Music RecSys')

st.write('Listening to songs less heard, genres undiscovered, and unfamiliar languages. Welcome to the obscure music recommendation system solely aimed at expanding your musical horizons.  ')
st.sidebar.image("MR_GN.png")

hide_style = """
        <style>
        footer {visibility: hidden;
        </style}
                    """

st.markdown(hide_style, unsafe_allow_html=True)

# Dev

search_choices = ['Song/Track', 'Artist', 'Album']
search_selected = st.sidebar.selectbox("Please choose one: ", search_choices)

search_keyword = st.text_input("Enter " + search_selected + " Name")
button_clicked = st.button("Search")

search_results = []
tracks = []
artists = []
albums = []


if search_keyword is not None and len(str(search_keyword)) > 0:
    if search_selected == 'Song/Track':
        st.write('Start Song/Track Search')
        tracks = sp.search(q='tracks' + search_keyword, type = 'track', limit = 20)
        tracks_list = tracks['tracks']['items']
        if len(tracks_list) > 0:
            for track in tracks_list:
                #st.write(track['name'] + " - By - " + track['artists'][0]['name'])
                search_results.append(track['name'] + " - By - " + track['artists'][0]['name'])

    elif search_selected == 'Artist':
        st.write('Start Artist Search')
        artists = sp.search(q='artist' + search_keyword, type = 'artist', limit = 20)
        artists_list = artists['artists']['items']
        if len(artists_list) > 0:
            for artist in artists_list:
                #st.write(artist['name'])
                search_results.append(artist['name'])

    if search_selected == 'Album':
        st.write('Start Album Search')
        albums = sp.search(q='album' + search_keyword, type = 'album', limit = 20)
        albums_list = albums['albums']['items']
        if len(albums_list) > 0:
            for album in albums_list:
                #st.write(album['name'] + " - By - " + album['artists'][0]['name'])
                #print("Album ID: " + album['id'] + " / Artist ID - " + album['artists'][0]['id'])
                search_results.append(album['name'] + " - By - " + album['artists'][0]['name'])


selected_album = None 
selected_artist = None 
selected_track = None 


if search_selected == 'Song/Track':
    selected_track = st.selectbox("Select your Song/Track: ", search_results)
elif search_selected == 'Artist':
    selected_artist = st.selectbox("Select your Artist: ", search_results)
elif search_selected == 'Album':
    selected_album = st.selectbox("Select your Album", search_results)


if selected_track is not None and len(tracks) > 0:
    tracks_list = tracks['tracks']['items']
    if len(tracks_list) > 0:
            for track in tracks_list:
                str_temp = track['name'] + " - By - " + track['artists'][0]['name']
                if str_temp == selected_track:
                    track_id = track['id']
                    track_album = track['album']['name']
                    img_album = track['album']['images'][1]['url']
                    #st.write(track_id,track_album, img_album)
                    music_recommendations.save_album_image(img_album,track_id)
    selected_track_choice = None                
    if track_id is not None:
        image = music_recommendations.get_album_image(track_id)
        st.image(image)

        track_choices = ['Song Features', 'Recommendations']
        selected_track_choice = st.sidebar.selectbox('Please select track choice: ', track_choices)
        if selected_track_choice == 'Song Features':
            track_features = sp.audio_features(track_id)
            df = pd.DataFrame(track_features, index=[0])
            df_features = df.loc[:,['acousticness','danceability','energy','instrumentalness','liveness','speechiness','valence']]
            st.dataframe(df_features)
            polar_plot.feature_plot(df_features)
        elif selected_track_choice == 'Recommendations':
            token = music_recommendations.get_token(Spotify_Client_ID, Spotify_Client_Secret)
            similar_songs_json = music_recommendations.get_track_recommendations(track_id,token)
            recommendations_list = similar_songs_json['tracks']
            recommendations_list_df = pd.DataFrame(recommendations_list)
            #st.dataframe(recommendations_list_df)
            recommendations_df = recommendations_list_df[['name','duration_ms','explicit','popularity']]
            st.dataframe(recommendations_df)
            music_recommendations.music_recommendation_viz(recommendations_df)
    else: 
        st.write('Please select a track from the list')
elif selected_album is not None and len(albums) > 0: 
    albums_list = albums['albums']['items']
    album_id = None
    album_uri = None
    album_name = None 

    if len(albums_list) > 0:
            for album in albums_list:
                str_temp = album['name'] + " - By - " + album['artists'][0]['name']
                if selected_album == str_temp: 
                    album_id = album['id']
                    album_uri = album['uri']
                    album_name = album['name']
    if album_id is not None and album_uri is not None: 
        st.write("Collecting all the tracks for the album: " + album_name)
        album_tracks = sp.album_tracks(album_id)
        df_album_tracks = pd.DataFrame(album_tracks['items'])
        #st.dataframe(df_album_tracks)
        df_a_tracks_min = df_album_tracks.loc[:,
                                              ['id','name','duration_ms','explicit','preview_url']]
        #st.dataframe(df_a_tracks_min)
        
        for idx in df_a_tracks_min.index:
            with st.container():
                col1, col2, col3, col4 = st.columns((4,4,1,1))
                col11, col12 = st.columns((8,2))
                col1.write(df_a_tracks_min['id'][idx])
                col2.write(df_a_tracks_min['name'][idx])
                col3.write(df_a_tracks_min['duration_ms'][idx])
                col4.write(df_a_tracks_min['explicit'][idx])
                if df_a_tracks_min['preview_url'][idx] is not None: 
                    col11.write(df_a_tracks_min['preview_url'][idx])
                    with col12:
                        st.audio(df_a_tracks_min['preview_url'][idx],format = "audio/mp3")

if selected_artist is not None and len(artists) > 0: 
    artists_list = artists['artists']['items']
    artist_id = None 
    artist_uri = None 
    selected_artist_choice = None
    if len(artists_list) > 0:
        for artist in artists_list:
                if selected_artist == artist['name']:
                    artist_id = artist['id']
                    artist_uri = artist['uri']
    if artist_id is not None: 
        artist_choice = ['Albums','Top Songs']
        selected_artist_choice = st.sidebar.selectbox('Select Artists Choice',artist_choice)
    if selected_artist_choice is not None: 
        if selected_artist_choice == 'Albums':
            artist_uri = 'spotify:artist:' + artist_id 
            album_result = sp.artist_albums(artist_uri, album_type='album')
            all_albums = album_result['items']
            col1,col2,col3 = st.columns((6,4,2))
            for album in all_albums: 
                with st.container(): 
                    col1.write(album['name'])
                    col2.write(album['release_date'])
                    col3.write(album['total_tracks'])
        elif selected_artist_choice == 'Top Songs':
            artist_uri = 'spotify:artist:' + artist_id 
            top_songs_result = sp.artist_top_tracks(artist_uri)
            for track in top_songs_result['tracks']:
                with st.container(): 
                    col1,col2,col3,col4 = st.columns((4,4,2,2))
                    col11, col12 = st.columns((10,2))
                    col21, col22 = st.columns((11,1))
                    col31,col32 = st.columns((11,1))
                    col1.write(track['id'])
                    col2.write(track['name'])
                    col3.write(track['duration_ms'])
                    col4.write(track['popularity'])
                    if track['preview_url'] is not None: 
                        col11.write(track['preview_url'])
                        with col12: 
                            st.audio(track['preview_url'],format='audio/mp3')
                        with col3: 
                            def feature_requested(): 
                                track_features = sp.audio_features(track['id'])
                                df = pd.DataFrame(track_features, index=[0])
                                df_features = df.loc[:,['acousticness','danceability','energy','instrumentalness','liveness','speechiness','valence']]
                                with col21: 
                                    st.dataframe(df_features)
                                with col31:
                                    polar_plot.feature_plot(df_features)
                            feature_botton_state = st.button('Track Audio Features', key = track['id'], on_click = feature_requested)

                        with col4: 
                            def music_rec_requested(): 
                                token = music_recommendations.get_token(Spotify_Client_ID, Spotify_Client_Secret)
                                similar_songs_json = music_recommendations.get_track_recommendations(track['id'],token)
                                recommendations_list = similar_songs_json['tracks']
                                recommendations_list_df = pd.DataFrame(recommendations_list)
                                recommendations_df = recommendations_list_df[['name','duration_ms','explicit','popularity']]
                                with col21: 
                                    st.dataframe(recommendations_df)
                                with col31: 
                                    music_recommendations.music_recommendation_viz(recommendations_df)
                            similar_rec_state = st.button('Similar Music', key = track['name'], on_click = music_rec_requested)
                        st.write('-----------------------')
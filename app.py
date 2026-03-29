import streamlit as st
import pickle
import requests
import pandas as pd
import os
import gdown

# --- CONFIGURATION ---
st.set_page_config(page_title="Movie Recommender", layout="wide")

# --- DOWNLOAD LARGE FILE FROM GOOGLE DRIVE ---
# This part handles your 762MB similarity file
file_id = '1SFyS6KHDQVKsX8RYih2UDKeyc37FSguT'
output = 'similarity.pkl'

if not os.path.exists(output):
    with st.spinner('Downloading similarity data from Google Drive... Please wait, this is a large file.'):
        url = f'https://drive.google.com/uc?id={file_id}'
        try:
            gdown.download(url, output, quiet=False)
        except Exception as e:
            st.error(f"Failed to download the data file: {e}")
            st.stop()

# --- HELPER FUNCTIONS ---

def fetch_movie_details(movie_id):
    """Fetches movie poster URL and release date from TMDB API."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=c7ec19ffdd3279641fb606d19ceb9bb1&language=en-US"
    
    poster = "https://via.placeholder.com/500x750?text=No+Poster"
    release_date = "N/A"
    
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            poster = "https://image.tmdb.org/t/p/w500/" + poster_path
        release_date = data.get('release_date', 'Unknown Date')
    except Exception:
        pass 
        
    return poster, release_date

def recommend(movie):
    """Finds top 10 similar movies based on cosine similarity."""
    try:
        index = movies[movies['title'] == movie].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        
        recommend_movie = []
        recommend_poster = []
        recommend_date = [] 
        
        # Slicing for 10 movies
        for i in distances[1:11]:
            movie_data = movies.iloc[i[0]]
            m_id = movie_data.get('id')
            genre_info = movie_data.get('genre', 'Unknown')
            display_name = f"{movie_data['title']} ({genre_info})"
            
            poster, date = fetch_movie_details(m_id)
            
            recommend_movie.append(display_name)
            recommend_poster.append(poster)
            recommend_date.append(date)
            
        return recommend_movie, recommend_poster, recommend_date

    except Exception as e:
        st.error(f"Error during recommendation: {e}")
        return [], [], []

# --- DATA LOADING ---
try:
    movies_dict = pickle.load(open("movies_dict.pkl", 'rb'))
    movies = pd.DataFrame(movies_dict)
    # Loading the downloaded similarity file
    similarity = pickle.load(open(output, 'rb'))
except Exception as e:
    st.error(f"Error loading data files: {e}")
    st.stop()

# --- STREAMLIT UI ---
st.header("Movie Recommendation System")

movies_list = movies['title'].values
selected_movie = st.selectbox("Select a movie", movies_list)

if st.button("Show Recommendation"):
    with st.spinner('Fetching recommendations...'):
        names, posters, dates = recommend(selected_movie)
    
    if names:
        # Row 1
        row1_cols = st.columns(5)
        for i in range(0, 5):
            with row1_cols[i]:
                st.write(f"**{names[i]}**")
                st.caption(f"Released: {dates[i]}")
                st.image(posters[i])

        st.markdown("---") 

        # Row 2
        row2_cols = st.columns(5)
        for i in range(5, 10):
            if i < len(names):
                with row2_cols[i - 5]:
                    st.write(f"**{names[i]}**")
                    st.caption(f"Released: {dates[i]}")
                    st.image(posters[i])
    else:
        st.warning("No recommendations found.")
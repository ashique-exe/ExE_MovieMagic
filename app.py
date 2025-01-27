import streamlit as st
import pickle
import pandas as pd
import requests
from pathlib import Path

# ----------------------------
# Load CSS
# ----------------------------
def load_css():
    """Loads custom CSS for the application."""
    try:
        css_path = Path(__file__).parent / "style.css"
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading styles: {e}")
        st.stop()

# ----------------------------
# Data Fetching Functions
# ----------------------------
def fetch_poster(movie_title):
    """Fetches movie details from TMDB API."""
    api_key = st.secrets['TMDB_API_KEY']
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_title}"
    try:
        data = requests.get(url).json()
        if data['results']:
            result = data['results'][0]
            return {
                'poster_url': f"https://image.tmdb.org/t/p/w500/{result.get('poster_path', '')}" if result.get('poster_path') else None,
                'overview': result.get('overview', 'No description available'),
                'rating': result.get('vote_average', 'N/A'),
                'release_date': result.get('release_date', 'Unknown'),
                'id': result.get('id')
            }
    except Exception as e:
        print(f"Error fetching poster: {e}")
        return None

def fetch_streaming_links(movie_id, movie_title):
    """Fetches streaming providers with error handling and direct homepage links."""
    api_key = st.secrets['TMDB_API_KEY']
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()

        streaming_links = []
        if data.get('results'):
            us_providers = data['results'].get('US', {})
            if us_providers.get('flatrate'):
                for provider in us_providers['flatrate']:
                    provider_name = provider['provider_name']
                    provider_links = {
                        "Netflix": "https://www.netflix.com",
                        "Amazon Prime Video": "https://www.amazon.com/primevideo",
                        "Disney Plus": "https://www.disneyplus.com",
                        "HBO Max": "https://www.hbomax.com",
                        "Paramount Plus": "https://www.paramountplus.com",
                        "Fubo TV": "https://www.fubo.tv",
                    }
                    # Only add the provider if it exists in the provider_links dictionary
                    if provider_name in provider_links:
                        link = provider_links.get(provider_name, '#')
                        streaming_links.append({'provider_name': provider_name, 'link': link})
                return streaming_links if streaming_links else None
            else:
                return None  # No flatrate providers found
        else:
            return None  # No results found
    except Exception as e:
        print(f"Error fetching streaming links: {e}")
        return None

# ----------------------------
# Recommendation Logic
# ----------------------------
def recommend(movie):
    """Generates movie recommendations."""
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distance = similarity[movie_index]
        movie_list = sorted(list(enumerate(distance)), reverse=True, key=lambda x: x[1])[1:6]
        return [movies.iloc[i[0]].title for i in movie_list]
    except Exception as e:
        st.error(f"Recommendation error: {e}")
        return []

# ----------------------------
# Load Data
# ----------------------------
try:
    movie_dict = pickle.load(open('movies_dict.pkl', 'rb'))
    movies = pd.DataFrame(movie_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except Exception as e:
    st.error(f"Error loading data files: {e}")
    st.stop()

# ----------------------------
# UI Configuration
# ----------------------------
load_css()
st.markdown('''
<div class="header">
    <div class="main-title">Movie</div>
    <div class="sub-title">Recommended Engine</div>
    <div class="version">__ExE__</div>
    <div class="subhead">YOUR GATEWAY TO THE NEXT CINEMATIC EXPERIENCE</div>
</div>
''', unsafe_allow_html=True)

# ----------------------------
# Dynamic Background with Soft Blur
# ----------------------------
def set_background(movie_title):
    """Sets dynamic background with soft blur."""
    try:
        api_key = st.secrets['TMDB_API_KEY']
        url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_title}"
        data = requests.get(url).json()
        if data.get('results'):
            bg_path = data['results'][0].get('backdrop_path', '')
            if bg_path:
                background_url = f"https://image.tmdb.org/t/p/w1280/{bg_path}"
                st.markdown(f"""
                    <style>
                    .stApp {{
                        background-image: url('{background_url}') !important;
                        background-size: cover !important;
                        background-position: center !important;
                    }}
                    .stApp::before {{
                        content: '';
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        background: inherit;
                        filter: blur(10px);
                        z-index: -1;
                    }}
                    </style>
                """, unsafe_allow_html=True)
    except Exception as e:
        print(f"Background error: {e}")

# ----------------------------
# Main Application
# ----------------------------
selected_movie = st.selectbox(
    '🔮 SELECT INPUT TITLE',
    movies['title'].values,
    help='Choose a movie to get ExE_enhanced recommendations'
)

set_background(selected_movie)

if st.button('🚀 INITIATE FULL SCAN'):
    with st.spinner('ACCESSING NEURAL NETWORK...'):
        st.markdown('<div class="scan-line"></div>', unsafe_allow_html=True)
        recommendations = recommend(selected_movie)

    if recommendations:
        st.markdown('### 🔍 SCAN RESULTS:')
        cols = st.columns(2)

        for idx, movie in enumerate(recommendations):
            with cols[idx % 2]:
                movie_data = fetch_poster(movie)
                streaming_links = None

                if movie_data and 'id' in movie_data:
                    streaming_links = fetch_streaming_links(movie_data['id'], movie)

                card_content = f"""
                    <div class="movie-card">
                        <h4 style="color: var(--neon-blue);">🎬 {movie}</h4>
                        {f'<img class="poster-image" src="{movie_data.get("poster_url", "")}" width="100%">'
                if movie_data and movie_data.get('poster_url') else '<p style="color: var(--hot-pink);">⚠️ IMAGE NOT FOUND</p>'}
                        <div class="rating-badge" style="margin: 10px 0;">
                            ⚡ RATING: {movie_data.get('rating', 'N/A')}/10</div>
                        <p style="color: var(--matrix-green);">📅 RELEASE: {movie_data.get('release_date', 'Unknown')}</p>
                        <p style="color: #ffffff; font-size: 1.1rem;">{movie_data.get('overview', 'No description available')}</p>
                """

                # Only display streaming links if they are available
                if streaming_links:
                    card_content += "<p style='color: var(--neon-blue); margin-top: 10px; font-size: 1.2rem;'>🎥 STREAM ON:</p>"
                    for link in streaming_links:
                        card_content += f"""
                            <a href='{link['link']}' target='_blank'>
                                <button class='watch-now-button'>{link['provider_name']}</button>
                            </a>
                        """
                else:
                    # Fallback message if no streaming links are found
                    card_content += "<p style='color: var(--hot-pink); margin-top: 10px; font-size: 1.2rem;'>⚠️ NO STREAMING LINK FOUND</p>"

                card_content += "</div>"
                st.markdown(card_content, unsafe_allow_html=True)

# ----------------------------
# Footer
# ----------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--cyber-purple); padding: 20px;">
    ⚡ POWERED BY TMDB DATABASE | __eXE__ v2.4.1 ⚡<br>
    [SYSTEM STATUS: OPERATIONAL]
</div>
""", unsafe_allow_html=True)


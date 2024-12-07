import requests
from flask import Flask, request, render_template
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)

# Insert your API keys here
SPOTIPY_CLIENT_ID = "0cbec824ac6d401c821418e53214d5f3"  # Replace with your actual Spotify Client ID
SPOTIPY_CLIENT_SECRET = "4654475589cd4363806221270cecb4ec"  # Replace with your actual Spotify Client Secret
WEATHER_API_KEY = "6c1f32a9cc93b6ca3080b6d5bb8f3351"  # Replace with your actual OpenWeatherMap API Key

# Initialize Spotify Client
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID,
                                                           client_secret=SPOTIPY_CLIENT_SECRET))

# Function to get weather data based on city
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    weather_data = response.json()
    
    if weather_data['cod'] != 200:
        return None
    
    weather = weather_data['weather'][0]['main'].lower()
    temp = weather_data['main']['temp']
    return weather, temp

# Function to map weather conditions to mood
def get_mood_from_weather(weather):
    if weather == 'clear':
        return "happy"
    elif weather == 'rain' or weather == 'snow':
        return "calm"
    elif weather == 'clouds':
        return "relaxed"
    elif weather == 'thunderstorm':
        return "energetic"
    else:
        return "neutral"

# Function to get recommended songs from Spotify based on mood
def get_music_recommendations(mood):
    query = ""

    # Set the query based on the mood
    if mood == "happy":
        query = "genre:pop"
    elif mood == "calm":
        query = "genre:acoustic"
    elif mood == "relaxed":
        query = "genre:chill"
    elif mood == "energetic":
        query = "genre:rock"
    else:
        query = "genre:indie"

    # Get recommendations from Spotify
    results = sp.search(q=query, type='track', limit=10)
    songs = []
    
    for idx, track in enumerate(results['tracks']['items']):
        song_info = {
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'url': track['external_urls']['spotify']
        }
        songs.append(song_info)
    
    return songs

# Define Routes for the Flask App

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    city = request.form['city']
    weather_data = get_weather(city)
    
    if not weather_data:
        return render_template('index.html', error="Invalid city name. Please try again.")
    
    weather, temp = weather_data
    mood = get_mood_from_weather(weather)
    songs = get_music_recommendations(mood)
    
    return render_template('index.html', mood=mood, weather=weather, temp=temp, songs=songs)

if __name__ == '__main__':
    app.run(debug=True)

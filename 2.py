#1. Flask App for Web Scraping
from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Scraping YouTube
def scrape_youtube():
    url = 'https://www.youtube.com/results?search_query=python+programming'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    videos = soup.find_all('a', {'class': 'yt-uix-tile-link'})
    results = [{'title': video['title'], 'link': f"https://www.youtube.com{video['href']}"} for video in videos[:10]]
    return results

@app.route('/')
def index():
    youtube_data = scrape_youtube()
    return render_template('index.html', youtube_data=youtube_data)

if __name__ == "__main__":
    app.run(debug=True)
#index.html
<!DOCTYPE html>
<html>
<head>
    <title>YouTube Scraper</title>
</head>
<body>
    <h1>YouTube Videos</h1>
    <ul>
        {% for video in youtube_data %}
            <li><a href="{{ video.link }}">{{ video.title }}</a></li>
        {% endfor %}
    </ul>
</body>
</html>
#2. Flask App Consuming External APIs

from flask import Flask, render_template
import requests

app = Flask(__name__)

# Fetching data from an external API (Example: OpenWeather API)
def get_weather(city):
    api_key = 'your_openweather_api_key'
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(url)
    return response.json()

@app.route('/weather/<city>')
def weather(city):
    weather_data = get_weather(city)
    return render_template('weather.html', weather=weather_data)

if __name__ == "__main__":
    app.run(debug=True)
#weather.html

<!DOCTYPE html>
<html>
<head>
    <title>Weather Data</title>
</head>
<body>
    <h1>Weather in {{ weather['name'] }}</h1>
    <p>Temperature: {{ weather['main']['temp'] }}K</p>
    <p>Weather: {{ weather['weather'][0]['description'] }}</p>
</body>
</html>
#3. OAuth2 Authentication (Google)

from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = 'random_secret_key'
oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id='your_google_client_id',
    client_secret='your_google_client_secret',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={
        'scope': 'openid profile email',
    }
)

@app.route('/')
def index():
    return 'Welcome to OAuth2 with Google'

@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    token = google.authorize_access_token()
    user_info = google.get('userinfo').json()
    session['profile'] = user_info
    return f'Logged in as {user_info["name"]}'

if __name__ == "__main__":
    app.run(debug=True)
#4. Recommendation System

from flask import Flask, render_template, request
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Sample user preference data
users = {'user': ['Alice', 'Bob', 'Charlie'],
         'book1': [1, 0, 1],
         'book2': [1, 1, 0],
         'book3': [0, 1, 1]}
df = pd.DataFrame(users)

# Function to generate recommendations
def recommend(user):
    user_vector = df[df['user'] == user].drop('user', axis=1).values
    similarity_matrix = cosine_similarity(user_vector, df.drop('user', axis=1).values)
    similar_users = similarity_matrix.argsort()[0][-2]
    recommended = df.iloc[similar_users]['user']
    return f"Based on your preferences, we recommend {recommended}'s choices!"

@app.route('/recommend/<user>')
def recommendation(user):
    rec = recommend(user)
    return rec

if __name__ == "__main__":
    app.run(debug=True)

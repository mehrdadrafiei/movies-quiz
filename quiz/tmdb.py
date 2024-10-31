# tmdb.py
import requests
from django.db import IntegrityError

TMDB_API_KEY = '97de56f16e75de6d50e3de5ad8dfea47'
TMDB_BASE_URL = 'https://api.themoviedb.org/3'




# downloader.py
from .models import Movie
import requests

class TMDBDownloader:
    def __init__(self, api_key=None):
        self.api_key = TMDB_API_KEY
        self.genres = {
            28:"Action",
            12:"Adventure",
            16: "Animation",
            35: "Comedy",
            80: "Crime",
            99: "Documentary",
            18: "Drama",
            10751: "Family",
            14: "Fantasy",
            36: "History",
            27: "Horror",
            10402: "Music",
            9648: "Mystery",
            10749: "Romance",
            878: "Science Fiction",
            10770: "TV Movie",
            53: "Thriller",
            10752: "War",
            37: "Western"
        }
        
    def fetch_and_store_movies(self, count=10):
        # Clear the database before adding new movies
        Movie.objects.all().delete()

        movies = self.fetch_popular_movies()[:count]
        for movie in movies[:count]:
            genre_names = [self.get_genre(genre_id) for genre_id in movie['genre_ids']]
            genre_hint = f"Genre: {', '.join(genre_names)}" if genre_names else "Genre not available"
            title_hint = f"The title starts with '{movie['title'][0]}'"

            try:
                Movie.objects.get_or_create(
                    id=movie["id"],
                    title=movie['title'],
                    overview=movie['overview'],
                    release_year=int(movie['release_date'][:4]),
                    genre=", ".join(genre_names),
                    hints=[title_hint, genre_hint]
                )
            except IntegrityError:
                # If the movie ID already exists, skip adding this movie
                print(f"Movie with ID {movie['id']} already exists. Skipping.")


    def get_genre(self, id):
        return self.genres[id]

    def fetch_popular_movies(self):
        # Fetch popular movies
        url = f"{TMDB_BASE_URL}/movie/popular?api_key={TMDB_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()['results']
        return []


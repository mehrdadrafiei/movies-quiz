from django.urls import path
from .views import StartGameView, GuessMovieView


urlpatterns = [
    path('start/', StartGameView.as_view(), name='start_game'),
    path('guess/', GuessMovieView.as_view(), name='guess_movie'),
]
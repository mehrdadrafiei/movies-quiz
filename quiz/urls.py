from django.urls import path
from .views import start_game, guess_movie


urlpatterns = [
    path('start/', start_game, name='start_game'),
    path('guess/', guess_movie, name='guess_movie'),
]
# views.py
from django.shortcuts import render, redirect
from .tmdb import TMDBDownloader
from .models import Movie
import time

def start_game(request):
    # Reset session data
    request.session['current_index'] = 0
    request.session['score'] = 0
    request.session['start_time'] = time.time()
    request.session['hints_used'] = 0

    if request.method == 'POST':
        tmdb = TMDBDownloader()
        tmdb.fetch_and_store_movies()
        return redirect('guess_movie')

    return render(request, 'start_game.html')

def guess_movie(request):
    current_index = request.session.get('current_index', 0)
    score = request.session.get('score', 0)
    movies = Movie.objects.all()[:5]
    total_movies = movies.count()

    if current_index >= total_movies:
        return render(request, 'finished.html')  # End of game

    current_movie = movies[current_index]
    hints_used = request.session.get('hints_used', 0)
    max_hints = len(current_movie.hints)
    hints = current_movie.hints[:hints_used] if hints_used > 0 else []
    progress_percentage = (current_index / total_movies) * 100 if total_movies > 0 else 0
    remaining_questions = total_movies - current_index

    context = {
        'movie': current_movie,
        'overview': current_movie.overview,
        'hints': hints,
        'current_index': current_index + 1,
        'total_movies': total_movies,
        'progress_percentage': progress_percentage,
        'score': score,
        'remaining_questions': remaining_questions,
        'error': None,
    }

    if request.method == 'POST':
        if 'submit_guess' in request.POST:
            user_guess = request.POST.get('guess', '').strip()
            if user_guess.lower() == current_movie.title.lower():
                score += 1
                request.session['score'] = score
                current_index += 1
                request.session['current_index'] = current_index
                request.session['hints_used'] = 0
                return redirect('guess_movie')
            else:
                context['error'] = "Incorrect guess! Moving to the next movie."
                current_index += 1
                request.session['current_index'] = current_index
                return redirect('guess_movie')
        elif 'hint' in request.POST:
            if hints_used < max_hints:
                hints_used += 1
                request.session['hints_used'] = hints_used
                return redirect('guess_movie')
            else:
                context['error'] = "No more hints available."

    return render(request, 'guess_movie.html', context)

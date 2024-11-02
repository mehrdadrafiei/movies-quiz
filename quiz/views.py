# views.py
from django.shortcuts import render, redirect
from django.contrib import messages  # Import messages
from .tmdb import TMDBDownloader
from .models import Movie
import time

def start_game(request):
    # Reset session data
    request.session['current_index'] = 0
    request.session['score'] = 0
    request.session['start_time'] = time.time()
    request.session['global_hints_used'] = 0  # Reset global hints
    request.session['hints_used_for_current_movie'] = 0  # Initialize hints for the current movie

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
    global_hints_used = request.session.get('global_hints_used', 0)
    max_global_hints = 5  # Total hints allowed for all movies
    hints_used_for_current_movie = request.session.get('hints_used_for_current_movie', 0)

    # Reset hints for the current movie at the start of guessing
    if hints_used_for_current_movie == 0 and current_index > 0:
        request.session['hints_used_for_current_movie'] = 0  # Reset for the new movie

    hints = current_movie.hints[:hints_used_for_current_movie] if hints_used_for_current_movie > 0 else []

    # progress_percentage = (current_index / total_movies) * 100 if total_movies > 0 else 0
    remaining_questions = total_movies - current_index

    context = {
        'movie': current_movie,
        'overview': current_movie.overview,
        'hints': hints,
        'current_index': current_index + 1,
        'total_movies': total_movies,
        #'progress_percentage': progress_percentage,
        'score': score,
        'remaining_questions': remaining_questions,
        'error': None,
        'global_hints_remaining': max_global_hints - global_hints_used,
    }

    if request.method == 'POST':
        if 'submit_guess' in request.POST:
            user_guess = request.POST.get('guess', '').strip()
            if user_guess.lower() == current_movie.title.lower():
                score += 1
                request.session['score'] = score
                current_index += 1
                request.session['current_index'] = current_index
                request.session['hints_used_for_current_movie'] = 0  # Reset for the next movie
                messages.add_message(request, messages.SUCCESS, 'Correct! Great job!', extra_tags='success')
                return redirect('guess_movie')
            else:
                current_index += 1
                request.session['current_index'] = current_index
                request.session['hints_used_for_current_movie'] = 0  # Reset for the next movie
                messages.add_message(request, messages.ERROR, 'Incorrect guess! Better luck next time.', extra_tags='danger')
                return redirect('guess_movie')

        elif 'hint' in request.POST:
            # Check if hints used for the current movie are less than 2
            if hints_used_for_current_movie < 2:
                if global_hints_used < max_global_hints:
                    global_hints_used += 1
                    hints_used_for_current_movie += 1
                    request.session['global_hints_used'] = global_hints_used
                    request.session['hints_used_for_current_movie'] = hints_used_for_current_movie
                    # messages.info(request, 'Hint used successfully!')  # Informational message
                else:
                    # context['error'] = "No more global hints available."
                    messages.warning(request, "No more global hints available.")  # Warning message
            else:
                # context['error'] = "No more global hints available."
                messages.info(request, "You have already used the maximum number of hints for this movie.")  # Informational message

            return redirect('guess_movie')

    return render(request, 'guess_movie.html', context)

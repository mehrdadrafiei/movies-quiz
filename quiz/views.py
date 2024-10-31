

# views.py
from django.shortcuts import render, redirect
from .tmdb import TMDBDownloader
from .models import Movie


def start_game(request):    
    # Reset session data if necessary
    request.session['current_index'] = 0
    request.session['hints_used'] = 0

    if request.method == 'POST':
        # Fetch movies from TMDB API
        tmdb = TMDBDownloader()
        tmdb.fetch_and_store_movies()
        return redirect('guess_movie')

    return render(request, 'start_game.html')


def guess_movie(request):
    # Get the current movie index, defaulting to 0 if not set
    current_index = request.session.get('current_index', 0)
    movies = Movie.objects.all()[:5]
    total_movies = movies.count()

    # Check if the game is finished
    if current_index >= total_movies:
        return render(request, 'finished.html')  # Display a finished game page

    # Get the current movie based on the index
    current_movie = movies[current_index]
    hints_used = request.session.get('hints_used', 0)
    max_hints = len(current_movie.hints)

    # Only reveal hints incrementally based on hints_used count
    hints = current_movie.hints[:hints_used] if hints_used > 0 else []

    # Calculate progress percentage
    progress_percentage = (current_index / total_movies) * 100 if total_movies > 0 else 0


    context = {
        'movie': current_movie,
        'overview': current_movie.overview,
        'hints': hints,
        'current_index': current_index + 1,
        'total_movies': total_movies,
        'progress_percentage': progress_percentage,  # Pass the percentage to the template
        'error': None,    }

    if request.method == 'POST':
        if 'submit_guess' in request.POST:
            user_guess = request.POST.get('guess', '').strip()
            if user_guess.lower() == current_movie.title.lower():
                # Correct guess, move to the next movie and reset hints
                current_index += 1
                request.session['current_index'] = current_index
                request.session['hints_used'] = 0
                return redirect('guess_movie')
            else:
                # Incorrect guess
                context['error'] = "Incorrect guess! Try again."

        elif 'hint' in request.POST:
            # Increment hints_used only if it’s below the max
            if hints_used < max_hints:
                hints_used += 1
                request.session['hints_used'] = hints_used
                return redirect('guess_movie')
            else:
                context['error'] = "No more hints available for this movie."

    return render(request, 'guess_movie.html', context)

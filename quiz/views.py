from django.shortcuts import render,redirect
from django.contrib import messages
from .tmdb import TMDBDownloader
from .models import Movie
import random
import time
from django.http import JsonResponse

def start_game(request):
    request.session['current_index'] = 0
    request.session['score'] = 0
    request.session['start_time'] = time.time()
    request.session['global_hints_used'] = 0
    request.session['hints_used_for_current_movie'] = 0

    if request.method == 'POST':
        tmdb = TMDBDownloader()
        tmdb.fetch_and_store_movies()
        return redirect('guess_movie')

    return render(request, 'start_game.html')

def guess_movie(request):
    current_index = request.session.get('current_index', 0)
    score = request.session.get('score', 0)
    movies = list(Movie.objects.all()[:5])
    total_movies = len(movies)

    if current_index >= total_movies:
        context = {
            'score': score,
            'total_movies': total_movies,
            'global_hints_used': request.session.get('global_hints_used', 0),
        }
        return render(request, 'finished.html', context)

    current_movie = movies[current_index]
    global_hints_used = request.session.get('global_hints_used', 0)
    max_global_hints = 5
    hints_used_for_current_movie = request.session.get('hints_used_for_current_movie', 0)
    if hints_used_for_current_movie == 0 and current_index > 0:
        request.session['hints_used_for_current_movie'] = 0  # Reset for the new movie

    hints = current_movie.hints[:hints_used_for_current_movie] if hints_used_for_current_movie > 0 else []

    all_movies = list(Movie.objects.all())
    choices = [current_movie.title]
    while len(choices) < 4:
        random_movie = random.choice(all_movies)
        if random_movie.title not in choices:
            choices.append(random_movie.title)

    random.shuffle(choices)

    if request.method == 'POST':
        if 'selected_guess' in request.POST:
            selected_guess = request.POST.get('selected_guess', '').strip()
            is_correct = selected_guess.lower() == current_movie.title.lower()

            if is_correct:
                score += 1
                request.session['score'] = score
                request.session['hints_used_for_current_movie'] = 0
                request.session['current_index'] = current_index + 1
                return JsonResponse({'is_correct': True, 'correct_answer': current_movie.title})

            else:
                request.session['hints_used_for_current_movie'] = 0  # Reset for the next movie
                request.session['current_index'] = current_index + 1
                return JsonResponse({'is_correct': False, 'correct_answer': current_movie.title})

        elif 'hint' in request.POST:
            if hints_used_for_current_movie < 2:
                if global_hints_used < max_global_hints:
                    global_hints_used += 1
                    hints_used_for_current_movie += 1
                    request.session['global_hints_used'] = global_hints_used
                    request.session['hints_used_for_current_movie'] = hints_used_for_current_movie
                    hints = current_movie.hints[:hints_used_for_current_movie]  # Update hints
                    return JsonResponse({
                        'success': True,
                        'hints': hints,
                        'global_hints_remaining': max_global_hints - global_hints_used
                    })
                else:
                    return JsonResponse({'success': False, 'message': "No more global hints available."})
            else:
                return JsonResponse({'success': False, 'message': "You have already used the maximum number of hints for this movie."})

    context = {
        'movie': current_movie,
        'overview': current_movie.overview,
        'hints': hints,
        'choices': choices,
        'current_movie_display': f"{current_index + 1}/{total_movies}",
        'score': score,
        'remaining_questions': total_movies - current_index,
        'global_hints_remaining': max_global_hints - global_hints_used,
    }

    return render(request, 'guess_movie.html', context)

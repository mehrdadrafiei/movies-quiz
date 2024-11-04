from django.views import View
from django.shortcuts import render, redirect
from .tmdb import TMDBDownloader
from .models import Movie
import random
import time
from django.http import JsonResponse

class StartGameView(View):
    template_name = 'game/start_game.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        request.session['current_index'] = 0
        request.session['score'] = 0
        request.session['start_time'] = time.time()
        request.session['global_hints_used'] = 0
        request.session['hints_used_for_current_movie'] = 0
        request.session['remaining_time'] = 6 * 60  # 6 minutes in seconds

        tmdb = TMDBDownloader()
        tmdb.fetch_and_store_movies()
        return redirect('guess_movie')


class GuessMovieView(View):
    template_name = 'game/guess_movie.html'
    max_hints = 5
    
    def get(self, request):
        current_index = request.session.get('current_index', 0)
        score = request.session.get('score', 0)
        movies = list(Movie.objects.all()[:5])
        total_movies = len(movies)

        if current_index >= total_movies:
            total_time = (time.time() - request.session['start_time']) / 60  # Convert seconds to minutes
            context = {
                'score': score,
                'total_movies': total_movies,
                'global_hints_used': request.session.get('global_hints_used', 0),
                'total_time': round(total_time, 2),
            }
            return render(request, 'game/finished.html', context)

        current_movie = movies[current_index]
        hints_used_for_current_movie = request.session.get('hints_used_for_current_movie', 0)

        # Reset hints for the new movie
        if hints_used_for_current_movie == 0 and current_index > 0:
            request.session['hints_used_for_current_movie'] = 0

        hints = current_movie.hints[:hints_used_for_current_movie] if hints_used_for_current_movie > 0 else []

        choices = self.get_choices(current_movie, movies)

        context = {
            'movie': current_movie,
            'overview': current_movie.overview,
            'hints': hints,
            'choices': choices,
            'current_movie_display': f"{current_index + 1}/{total_movies}",
            'score': score,
            'remaining_questions': total_movies - current_index,
            'global_hints_remaining': self.max_hints - request.session.get('global_hints_used', 0),
            'remaining_time': self.calculate_remaining_time(request),
        }

        return render(request, self.template_name, context)

    def post(self, request):
        current_index = request.session.get('current_index', 0)
        movies = list(Movie.objects.all()[:5])
        current_movie = movies[current_index]

        if 'selected_guess' in request.POST:
            return self.handle_guess(request, current_movie)

        elif 'hint' in request.POST:
            return self.handle_hint(request, current_movie)

    def handle_guess(self, request, current_movie):
        selected_guess = request.POST.get('selected_guess', '').strip()
        score = request.session.get('score', 0)
        is_correct = selected_guess.lower() == current_movie.title.lower()

        if is_correct:
            score += 1
            request.session['score'] = score
            request.session['hints_used_for_current_movie'] = 0
            request.session['current_index'] = request.session.get('current_index', 0) + 1
            return JsonResponse({'is_correct': True, 'correct_answer': current_movie.title})

        else:
            request.session['hints_used_for_current_movie'] = 0
            request.session['current_index'] = request.session.get('current_index', 0) + 1
            return JsonResponse({'is_correct': False, 'correct_answer': current_movie.title})

    def handle_hint(self, request, current_movie):
        global_hints_used = request.session.get('global_hints_used', 0)
        hints_used_for_current_movie = request.session.get('hints_used_for_current_movie', 0)

        if hints_used_for_current_movie < 2 and global_hints_used < 5:
            global_hints_used += 1
            hints_used_for_current_movie += 1
            request.session['global_hints_used'] = global_hints_used
            request.session['hints_used_for_current_movie'] = hints_used_for_current_movie
            hints = current_movie.hints[:hints_used_for_current_movie]
            return JsonResponse({
                'success': True,
                'hints': hints,
                'global_hints_remaining': 5 - global_hints_used
            })
        elif global_hints_used >= 5:
            return JsonResponse({'success': False, 'message': "No more global hints available."})
        else:
            return JsonResponse({'success': False, 'message': "You have already used the maximum number of hints for this movie."})

    def get_choices(self, current_movie, movies):
        all_movies = list(Movie.objects.all())
        choices = [current_movie.title]
        while len(choices) < 4:
            random_movie = random.choice(all_movies)
            if random_movie.title not in choices:
                choices.append(random_movie.title)

        random.shuffle(choices)
        return choices

    def calculate_remaining_time(self, request):
        elapsed_time = time.time() - request.session['start_time']
        remaining_time = max(0, request.session['remaining_time'] - int(elapsed_time))
        request.session['remaining_time'] = remaining_time
        return remaining_time

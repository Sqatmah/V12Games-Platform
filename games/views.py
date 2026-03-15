import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Game, Genre, Collection, GameRequest
from reviews.models import Review
from reviews.forms import ReviewForm


def home(request):
    featured = Game.objects.filter(is_featured=True).prefetch_related('genres')[:10]
    trending = Game.objects.filter(is_trending=True).order_by('-downloads').prefetch_related('genres')[:16]
    latest = Game.objects.order_by('-created_at').prefetch_related('genres')[:16]
    upcoming = Game.objects.filter(is_upcoming=True).prefetch_related('genres')[:6]
    genres = Genre.objects.all()
    collections = Collection.objects.prefetch_related('games')[:4]
    top_game = Game.objects.order_by('-downloads').first()
    context = {
        'featured': featured,
        'trending': trending,
        'latest': latest,
        'upcoming': upcoming,
        'genres': genres,
        'collections': collections,
        'top_game': top_game,
    }
    return render(request, 'games/home.html', context)


def game_list(request):
    games = Game.objects.all().prefetch_related('genres')
    q = request.GET.get('q', '').strip()
    if q:
        games = games.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(genres__name__icontains=q)
        ).distinct()
    genre_slug = request.GET.get('genre', '')
    if genre_slug:
        games = games.filter(genres__slug=genre_slug)
    year = request.GET.get('year', '')
    if year:
        games = games.filter(release_year=year)
    sort = request.GET.get('sort', '-created_at')
    sort_options = ['-created_at', '-downloads', '-views', 'title']
    if sort not in sort_options:
        sort = '-created_at'
    games = games.order_by(sort)
    paginator = Paginator(games, 24)
    page_obj = paginator.get_page(request.GET.get('page'))
    years = Game.objects.values_list('release_year', flat=True).distinct().order_by('-release_year')
    genres = Genre.objects.all()
    active_genre = Genre.objects.filter(slug=genre_slug).first() if genre_slug else None
    context = {
        'games': page_obj,
        'page_obj': page_obj,
        'genres': genres,
        'years': years,
        'q': q,
        'active_genre': active_genre,
        'active_genre_slug': genre_slug,
        'active_year': year,
        'active_sort': sort,
        'total_count': paginator.count,
    }
    return render(request, 'games/list.html', context)


def game_detail(request, slug):
    game = get_object_or_404(Game, slug=slug)
    Game.objects.filter(pk=game.pk).update(views=F('views') + 1)
    screenshots = game.screenshots.all()
    links = game.download_links.filter(is_active=True)
    reviews = game.reviews.select_related('user').order_by('-created_at')
    related = Game.objects.filter(genres__in=game.genres.all()).exclude(pk=game.pk).distinct()[:6]
    user_review = None
    form = ReviewForm()
    if request.user.is_authenticated:
        user_review = Review.objects.filter(game=game, user=request.user).first()
        if request.method == 'POST' and not user_review:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.game = game
                review.user = request.user
                review.save()
                return redirect('game_detail', slug=game.slug)
    context = {
        'game': game,
        'screenshots': screenshots,
        'links': links,
        'reviews': reviews,
        'related': related,
        'user_review': user_review,
        'form': form,
        'avg_rating': game.average_rating(),
        'avg_stars': game.average_rating_stars(),
    }
    return render(request, 'games/detail.html', context)


def genre_games(request, slug):
    genre = get_object_or_404(Genre, slug=slug)
    games = genre.games.all().prefetch_related('genres')
    paginator = Paginator(games, 24)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {
        'games': page_obj,
        'page_obj': page_obj,
        'genre': genre,
        'genres': Genre.objects.all(),
        'active_genre': genre,
        'active_genre_slug': slug,
        'total_count': paginator.count,
        'page_title': f'{genre.name} Games',
    }
    return render(request, 'games/list.html', context)


def leaderboard(request):
    top_downloaded = Game.objects.order_by('-downloads').prefetch_related('genres')[:50]
    top_viewed = Game.objects.order_by('-views').prefetch_related('genres')[:50]
    return render(request, 'games/leaderboard.html', {
        'top_downloaded': top_downloaded,
        'top_viewed': top_viewed,
    })


def collections_view(request):
    collections = Collection.objects.prefetch_related('games').all()
    return render(request, 'games/collections.html', {'collections': collections})


def collection_detail(request, slug):
    collection = get_object_or_404(Collection, slug=slug)
    games = collection.games.all().prefetch_related('genres')
    return render(request, 'games/collection_detail.html', {
        'collection': collection,
        'games': games,
    })


@require_POST
@login_required
def like_game(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    user = request.user
    if user in game.liked_by.all():
        game.liked_by.remove(user)
        liked = False
    else:
        game.liked_by.add(user)
        liked = True
    game.likes = game.liked_by.count()
    game.save(update_fields=['likes'])
    return JsonResponse({'liked': liked, 'count': game.likes})


def random_game(request):
    count = Game.objects.count()
    if count == 0:
        return redirect('home')
    game = Game.objects.all()[random.randint(0, count - 1)]
    return redirect(game.get_absolute_url())




def search_api(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': [], 'count': 0})

    games = Game.objects.filter(
        Q(title__icontains=q) |
        Q(genres__name__icontains=q)
    ).distinct().prefetch_related('genres')[:8]

    results = []
    for game in games:
        results.append({
            'title': game.title,
            'slug': game.slug,
            'url': game.get_absolute_url(),
            'poster': game.poster.url if game.poster else None,
            'year': game.release_year,
            'file_size': game.file_size,
            'version': game.version,
            'genres': [g.name for g in game.genres.all()[:2]],
            'downloads': game.downloads,
        })

    return JsonResponse({'results': results, 'count': len(results)})   



def search_api(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': [], 'count': 0})
    games = Game.objects.filter(
        Q(title__icontains=q) | Q(genres__name__icontains=q)
    ).distinct().prefetch_related('genres')[:8]
    results = []
    for game in games:
        results.append({
            'title': game.title,
            'url': game.get_absolute_url(),
            'poster': game.poster.url if game.poster else None,
            'year': game.release_year,
            'file_size': game.file_size,
            'version': game.version,
            'genres': [g.name for g in game.genres.all()[:2]],
            'downloads': game.downloads,
        })
    return JsonResponse({'results': results, 'count': len(results)}) 







def request_game(request):
    message = None
    error = None

    if request.method == 'POST':
        title = request.POST.get('game_title', '').strip()
        note = request.POST.get('note', '').strip()
        email = request.POST.get('email', '').strip()

        if title:
            existing = GameRequest.objects.filter(
                game_title__iexact=title
            ).first()

            if existing:
                existing.votes += 1
                existing.save()
                message = f'✅ Your vote has been added to "{title}"! ({existing.votes} votes total)'
            else:
                GameRequest.objects.create(
                    game_title=title,
                    user=request.user if request.user.is_authenticated else None,
                    user_email=email,
                    note=note,
                )
                message = f'✅ "{title}" has been requested! We\'ll add it soon.'

                # إرسال إشعار Discord
                _notify_discord_new_request(title, note, request.user)
        else:
            error = 'Please enter a game title.'

    # الأدمن يشوف كل الطلبات — اليوزر العادي لا يشوف شيء
    pending = None
    added = None
    if request.user.is_authenticated and request.user.is_staff:
        pending = GameRequest.objects.filter(status='pending').order_by('-votes')[:20]
        added = GameRequest.objects.filter(status='added').order_by('-created_at')[:10]

    return render(request, 'games/request_game.html', {
        'pending': pending,
        'added': added,
        'message': message,
        'error': error,
        'is_admin': request.user.is_authenticated and request.user.is_staff,
    })


def _notify_discord_new_request(title, note, user):
    """إرسال إشعار لـ Discord عند طلب لعبة جديدة"""
    import requests as req
    from django.conf import settings

    webhook_url = getattr(settings, 'DISCORD_WEBHOOK_URL', '')
    if not webhook_url:
        return

    username = user.username if user.is_authenticated else 'Guest'

    embed = {
        "title": "🎮 New Game Request!",
        "color": 7419530,  # Purple
        "fields": [
            {"name": "🎯 Game Title", "value": title, "inline": False},
            {"name": "👤 Requested by", "value": username, "inline": True},
        ],
        "footer": {"text": "V12Games — Game Request System"},
        "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
    }

    if note:
        embed["fields"].append({"name": "📝 Notes", "value": note, "inline": False})

    try:
        req.post(webhook_url, json={
            "username": "V12Games Bot",
            "avatar_url": "https://cdn.discordapp.com/embed/avatars/0.png",
            "embeds": [embed]
        }, timeout=5)
    except Exception:
        pass

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('games/', views.game_list, name='game_list'),
    path('game/<slug:slug>/', views.game_detail, name='game_detail'),
    path('genre/<slug:slug>/', views.genre_games, name='genre_games'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('collections/', views.collections_view, name='collections'),
    path('collection/<slug:slug>/', views.collection_detail, name='collection_detail'),
    path('like/<int:game_id>/', views.like_game, name='like_game'),
    path('random/', views.random_game, name='random_game'),
    path('api/search/', views.search_api, name='search_api'),
    path('request/', views.request_game, name='request_game'),
]
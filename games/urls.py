from django.urls import path
from .views import (
    home_view, dashboard_view, create_game_view, game_detail_view,
    favorites_view, add_favorite_view, remove_favorite_view,
    toggle_privacy_view, explore_view
)

urlpatterns = [
    path('dashboard/', dashboard_view, name='dashboard'),
    path('create/', create_game_view, name='create'),
    path('explore/', explore_view, name='explore'),
    path('<int:pk>/', game_detail_view, name='detail'),
    path('<int:pk>/favorite/', add_favorite_view, name='favorite'),
    path('<int:pk>/unfavorite/', remove_favorite_view, name='unfavorite'),
    path('<int:pk>/toggle-privacy/', toggle_privacy_view, name='toggle_privacy'),
    path('favorites/', favorites_view, name='favorites'),
]

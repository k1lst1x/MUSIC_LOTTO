from django.urls import path
from .views import create_music_lotto, music_lotto_list, music_lotto_detail, music_lotto_tracks, play_track, clear_session, get_tracks_state

urlpatterns = [
    path('create-music-lotto/', create_music_lotto, name='create_music_lotto'),
    path('choose-music-lotto/', music_lotto_list, name='music_lotto_list'),  # Список музыкальных лотто
    path('<int:id>/', music_lotto_detail, name='music_lotto_detail'),
    path('music_lotto/<int:id>/', music_lotto_tracks, name='music_lotto_tracks'),
    path('play_track/', play_track, name='play_track'),
    path('clear-session/', clear_session, name='clear_session'),
    path('music_lotto/<int:id>/tracks_state/', get_tracks_state, name='get_tracks_state'),

]

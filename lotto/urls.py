from django.urls import path
from .views import create_music_lotto, music_lotto_list, music_lotto_detail

urlpatterns = [
    path('create-music-lotto/', create_music_lotto, name='create_music_lotto'),
    path('choose-music-lotto/', music_lotto_list, name='music_lotto_list'),  # Список музыкальных лотто
    path('<int:id>/', music_lotto_detail, name='music_lotto_detail'),  # Страница одного музыкального лотто
]

from django.db import models
from django.utils.text import get_valid_filename
from django.core.files.storage import FileSystemStorage
import os

class CustomFileSystemStorage(FileSystemStorage):
    def get_valid_name(self, name):
        # Сохраняем пробелы, вместо замены их на подчёркивания
        return get_valid_filename(name).replace("_", " ")

custom_storage = CustomFileSystemStorage()

def upload_to(instance, filename):
    """Динамический путь для сохранения файлов."""
    return f'music_lotto/{instance.music_lotto.id}/{filename}'

class MusicLotto(models.Model):
    name = models.CharField(
        max_length=255, 
        verbose_name="Название", 
        help_text="Введите название музыкальной лотереи"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    edited_at = models.DateTimeField(auto_now=True, verbose_name="Дата редактирования")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    def __str__(self):
        return self.name or f"Music Lotto #{self.id}"


class PlaylistFile(models.Model):
    music_lotto = models.ForeignKey(
        MusicLotto, 
        related_name='playlist_files', 
        on_delete=models.CASCADE,
        verbose_name="Музыкальная лотерея"
    )
    file = models.FileField(upload_to=upload_to, storage=custom_storage, verbose_name="Файл плейлиста")

    def __str__(self):
        return os.path.basename(self.file.name)
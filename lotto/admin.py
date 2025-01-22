from django.contrib import admin
from .models import MusicLotto, PlaylistFile

class MusicLottoAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'edited_at', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)
    ordering = ('-created_at',)

class PlaylistFileAdmin(admin.ModelAdmin):
    list_display = ('music_lotto', 'file', 'id')
    search_fields = ('music_lotto__name',)
    list_filter = ('music_lotto',)
    ordering = ('-id',)

# Регистрируем модели в админке
admin.site.register(MusicLotto, MusicLottoAdmin)
admin.site.register(PlaylistFile, PlaylistFileAdmin)

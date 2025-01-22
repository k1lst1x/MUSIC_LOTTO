from django import forms
from .models import MusicLotto

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True  # Включаем поддержку нескольких файлов

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())  # Используем кастомный виджет
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class MusicLottoForm(forms.ModelForm):
    playlist_files = MultipleFileField(
        label='Загрузите плейлист',
        required=False
    )

    class Meta:
        model = MusicLotto
        fields = ['name', 'is_active']  # Указываем только поля из модели MusicLotto

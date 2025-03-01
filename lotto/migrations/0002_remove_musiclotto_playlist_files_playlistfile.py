# Generated by Django 5.1.5 on 2025-01-21 15:52

import django.db.models.deletion
import lotto.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lotto', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='musiclotto',
            name='playlist_files',
        ),
        migrations.CreateModel(
            name='PlaylistFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=lotto.models.upload_to, verbose_name='Файл плейлиста')),
                ('music_lotto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='playlist_files', to='lotto.musiclotto', verbose_name='Музыкальная лотерея')),
            ],
        ),
    ]

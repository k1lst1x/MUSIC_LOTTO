# Generated by Django 5.1.5 on 2025-03-12 09:51

import lotto.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lotto', '0003_musiclotto_name_alter_musiclotto_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playlistfile',
            name='file',
            field=models.FileField(storage=lotto.models.CustomFileSystemStorage(), upload_to=lotto.models.upload_to, verbose_name='Файл плейлиста'),
        ),
    ]

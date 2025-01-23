from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .models import MusicLotto, PlaylistFile
from .forms import MusicLottoForm
import os
import subprocess
import sys

python_executable = sys.executable

def create_music_lotto(request):
    if request.method == 'POST':
        form = MusicLottoForm(request.POST, request.FILES)
        files = request.FILES.getlist('playlist_files')  # Получаем список загруженных файлов
        if form.is_valid():
            music_lotto = form.save()  # Сохраняем основной объект
            for file in files:
                # Создаём объект PlaylistFile для каждого файла
                PlaylistFile.objects.create(music_lotto=music_lotto, file=file)
            return redirect('music_lotto_list')  # Перенаправляем на страницу успеха
    else:
        form = MusicLottoForm()
    return render(request, 'create_music_lotto.html', {'form': form})

def music_lotto_list(request):
    music_lottos = MusicLotto.objects.all()  # Получаем все музыкальные лотто
    return render(request, 'choose_music_lotto.html', {'music_lottos': music_lottos})

def music_lotto_detail(request, id):
    # Получаем объект лотереи
    music_lotto = get_object_or_404(MusicLotto, id=id)

    # Путь к папке с треками
    folder_path = os.path.join('uploads', 'music_lotto', str(id))
    excel_file_path = f"{folder_path}.xlsx"
    tickets_pdf_path = os.path.join(folder_path, "tickets.pdf")

    # Проверка наличия PDF-файла
    tickets_pdf_exists = os.path.exists(tickets_pdf_path)
    tickets_pdf_url = f"/{folder_path}/tickets.pdf" if tickets_pdf_exists else None

    if request.method == 'POST':
        # Обработка кнопки "Сгенерировать"
        if 'generate' in request.POST:
            if not os.path.exists(folder_path):
                messages.error(request, "Папка с треками не найдена.")
                return redirect('music_lotto_detail', id=id)

            try:
                script_path = os.path.join(os.path.dirname(__file__), 'generate.py')
                result = subprocess.run(
                    [sys.executable, script_path, folder_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                if result.returncode == 0:
                    messages.success(request, f"Файл успешно сгенерирован: {excel_file_path}")
                else:
                    messages.error(request, f"Ошибка генерации: {result.stderr}")
            except Exception as e:
                messages.error(request, f"Ошибка выполнения команды: {str(e)}")

        # Обработка кнопки "Создать билеты"
        elif 'create_tickets' in request.POST:
            ticket_count = request.POST.get('ticket_count', 1)
            if not os.path.exists(excel_file_path):
                messages.error(request, "Файл с треками не найден. Сначала сгенерируйте его.")
                return redirect('music_lotto_detail', id=id)

            try:
                script_path = os.path.join(os.path.dirname(__file__), 'tickets.py')
                result = subprocess.run(
                    [sys.executable, script_path, str(ticket_count), excel_file_path, folder_path, "1"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                if result.returncode == 0:
                    messages.success(request, "Билеты успешно созданы.")
                else:
                    messages.error(request, f"Ошибка создания билетов: {result.stderr}")
            except Exception as e:
                messages.error(request, f"Ошибка выполнения команды: {str(e)}")

        # Обработка кнопки "Вывод треков"
        elif 'show_tracks' in request.POST:
            try:
                script_path = os.path.join(os.path.dirname(__file__), 'play4.py')
                result = subprocess.run(
                    [sys.executable, script_path, folder_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                if result.returncode == 0:
                    messages.success(request, "Треки успешно выведены.")
                else:
                    messages.error(request, f"Ошибка вывода треков: {result.stderr}")
            except Exception as e:
                messages.error(request, f"Ошибка выполнения команды: {str(e)}")

        return redirect('music_lotto_detail', id=id)

    # Рендерим страницу
    return render(request, 'music_lotto_detail.html', {
        'music_lotto': music_lotto,
        'default_ticket_count': 1,
        'tickets_pdf_exists': tickets_pdf_exists,
        'tickets_pdf_url': tickets_pdf_url,
    })


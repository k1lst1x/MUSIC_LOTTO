from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .models import MusicLotto, PlaylistFile
from .forms import MusicLottoForm
import os
import subprocess
import sys
import pandas as pd
import numpy as np
import pickle
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

python_executable = sys.executable

@login_required(login_url='/users/login/?/')
def create_music_lotto(request):
    if request.method == 'POST':
        form = MusicLottoForm(request.POST, request.FILES)
        files = request.FILES.getlist('playlist_files')

        if form.is_valid():
            music_lotto = form.save()  # Сохраняем основной объект

            # Оптимизированное сохранение файлов
            playlist_files = [
                PlaylistFile(music_lotto=music_lotto, file=file)
                for file in files
            ]
            PlaylistFile.objects.bulk_create(playlist_files)  # Один запрос в БД вместо множества

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({"status": "success", "redirect_url": "/music-lotto/choose-music-lotto/"})

            return redirect('music_lotto_list')

    else:
        form = MusicLottoForm()

    return render(request, 'create_music_lotto.html', {'form': form})

@login_required(login_url='/users/login/?/')
def music_lotto_list(request):
    music_lottos = MusicLotto.objects.all()  # Получаем все музыкальные лотто
    return render(request, 'choose_music_lotto.html', {'music_lottos': music_lottos})

@login_required(login_url='/users/login/?/')
def music_lotto_detail(request, id):
    # Получаем объект лотереи
    music_lotto = get_object_or_404(MusicLotto, id=id)

    # Путь к папке с треками
    folder_path = os.path.join('uploads', 'music_lotto', str(id))
    excel_file_path = f"{folder_path}.xlsx"
    tickets_pdf_path = os.path.join(folder_path, "tickets.pdf")

    # Проверка наличия PDF-файла
    tickets_pdf_exists = os.path.exists(tickets_pdf_path)
    tickets_pdf_url = f"/{tickets_pdf_path}" if tickets_pdf_exists else None

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
            round_number = request.POST.get('round_number', 1)

            if not os.path.exists(excel_file_path):
                messages.error(request, "Файл с треками не найден. Сначала сгенерируйте его.")
                return redirect('music_lotto_detail', id=id)

            try:
                # Удаляем старый PDF, если есть
                if os.path.exists(tickets_pdf_path):
                    os.remove(tickets_pdf_path)

                script_path = os.path.join(os.path.dirname(__file__), 'tickets.py')
                os.makedirs(folder_path, exist_ok=True)

                # Запуск генерации в фоне
                subprocess.Popen(
                    [sys.executable, script_path, str(ticket_count), excel_file_path, folder_path, str(round_number)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

                messages.success(request, "Создание билетов запущено в фоне. Проверьте PDF через некоторое время.")
            except Exception as e:
                messages.error(request, f"Ошибка запуска генерации билетов: {str(e)}")

        # Переход к трекам
        elif 'show_tracks' in request.POST:
            return redirect('music_lotto_tracks', id=id)

        return redirect('music_lotto_detail', id=id)

    # Рендерим страницу
    return render(request, 'music_lotto_detail.html', {
        'music_lotto': music_lotto,
        'folder_path': folder_path,
        'default_ticket_count': 1,
        'default_round_number': 1,
        'tickets_pdf_exists': os.path.exists(tickets_pdf_path),  # ещё раз проверка
        'tickets_pdf_url': tickets_pdf_url,
    })

# Хранилище состояния
state = {
    'played_tracks': [],
    'current_track': None,
    'bingo_info': '',
    'triple_bingo_info': '',
    'full_bingo_info': '',
    'tickets': [],
    'folder_path': '',
}

@login_required(login_url='/users/login/?/')
def save_state_to_session(request):
    request.session['state'] = {
        'played_tracks': state['played_tracks'],
        'current_track': state['current_track'],
        'bingo_info': state['bingo_info'],
        'triple_bingo_info': state['triple_bingo_info'],
        'full_bingo_info': state['full_bingo_info'],
    }
    request.session.modified = True

@login_required(login_url='/users/login/?/')
def load_state_from_session(request):
    session_state = request.session.get('state', {})
    state['played_tracks'] = session_state.get('played_tracks', [])
    state['current_track'] = session_state.get('current_track', None)
    state['bingo_info'] = session_state.get('bingo_info', '')
    state['triple_bingo_info'] = session_state.get('triple_bingo_info', '')
    state['full_bingo_info'] = session_state.get('full_bingo_info', '')

def read_order_file(folder_path):
    order_path = os.path.join(folder_path, 'order.xlsx')
    if not os.path.exists(order_path):
        raise FileNotFoundError(f"Order file not found: {order_path}")
    df = pd.read_excel(order_path)
    if 'Порядковый номер' not in df.columns:
        raise KeyError("Missing 'Порядковый номер' column in order.xlsx")
    return df['Порядковый номер'].tolist()

def read_tickets_file(folder_path):
    tickets_path = os.path.join(folder_path, 'tickets.pkl')
    if not os.path.exists(tickets_path):
        raise FileNotFoundError(f"Tickets file not found: {tickets_path}")
    with open(tickets_path, 'rb') as f:
        tickets = pickle.load(f)
    return [np.array(ticket).reshape(5, 5) for ticket in tickets]

def check_bingo(ticket, played_set):
    bingo_results = []
    # строки и столбцы
    for i in range(5):
        row = ticket[i, :]
        col = ticket[:, i]
        if all(x in played_set for x in row):
            bingo_results.append(f"Ряд {i+1}")
        if all(x in played_set for x in col):
            bingo_results.append(f"Колонка {i+1}")
    # диагонали
    main_diag = [ticket[i, i] for i in range(5)]
    sec_diag = [ticket[i, 4 - i] for i in range(5)]
    if all(x in played_set for x in main_diag):
        bingo_results.append("Главная диагональ")
    if all(x in played_set for x in sec_diag):
        bingo_results.append("Вторая диагональ")
    return bingo_results

def is_full_bingo(ticket, played_set):
    # blackout — закрыты все 25 клеток
    return all(x in played_set for x in ticket.flatten())

@login_required(login_url='/users/login/?/')
def music_lotto_tracks(request, id):
    folder_path = os.path.join('uploads', 'music_lotto', str(id))
    print(f"Resolved folder path: {folder_path}")

    if not os.path.exists(folder_path):
        return JsonResponse({'error': f'Folder not found: {folder_path}'}, status=404)

    try:
        load_state_from_session(request)  # Загружаем состояние из сессии
        state['folder_path'] = folder_path
        state['tickets'] = read_tickets_file(folder_path)
        tracks = read_order_file(folder_path)
        return render(request, 'music_lotto_tracks.html', {
            'tracks': tracks,
            'folder_path': folder_path,
            'bingo_info': state['bingo_info'],
            'triple_bingo_info': state['triple_bingo_info'],
            'full_bingo_info': state['full_bingo_info'],
        })
    except Exception as e:
        print(f"Error in music_lotto_tracks: {e}")
        return JsonResponse({'error': 'Failed to load tracks', 'details': str(e)}, status=500)

@csrf_exempt
@login_required(login_url='/users/login/?/')
def play_track(request):
    if request.method == 'POST':
        try:
            data = request.POST
            track_idx = int(data.get('track_idx', 0))
            folder_path = data.get('folder_path')

            print(f"Получен запрос на воспроизведение: track_idx={track_idx}, folder_path={folder_path}")

            tracks = read_order_file(folder_path)
            if track_idx < 0 or track_idx >= len(tracks):
                print("Ошибка: Некорректный индекс трека")
                return JsonResponse({'error': 'Invalid track index'}, status=400)

            # Обновляем текущий трек и сыгранные треки
            state['current_track'] = tracks[track_idx]
            state['played_tracks'].append(tracks[track_idx])

            print(f"Текущий трек обновлен: {state['current_track']}, сыгранные треки: {state['played_tracks']}")
            
            played_set = set(state['played_tracks'])

            # Определение Bingo
            bingo_tickets = []
            triple_bingo_tickets = []
            full_bingo_tickets = []

            for idx, ticket in enumerate(state['tickets']):
                bingo_results = check_bingo(ticket, played_set)

                if bingo_results:
                    bingo_tickets.append(idx + 1)

                if len(bingo_results) >= 3:
                    triple_bingo_tickets.append(idx + 1)

                if is_full_bingo(ticket, played_set):   # <-- вот ключевая правка
                    full_bingo_tickets.append(idx + 1)

            # Обновляем информацию о Bingo
            state['bingo_info'] = f"Bingo билеты: {', '.join(map(str, bingo_tickets))}" if bingo_tickets else "Нет Bingo"
            state['triple_bingo_info'] = f"Triple Bingo билеты: {', '.join(map(str, triple_bingo_tickets))}" if triple_bingo_tickets else "Нет Triple Bingo"
            state['full_bingo_info'] = f"Полный Bingo билеты: {', '.join(map(str, full_bingo_tickets))}" if full_bingo_tickets else "Нет Полного Bingo"

            save_state_to_session(request)

            # Проверка файла перед отправкой URL
            track_file = os.path.join(folder_path, f"{tracks[track_idx]}.mp3")
            if not os.path.exists(track_file):
                print(f"Ошибка: Файл не найден {track_file}")
                return JsonResponse({'error': 'Track file not found'}, status=404)

            track_url = f"/media/{os.path.relpath(track_file, 'media')}"

            print(f"Трек готов к воспроизведению: {track_url}")

            return JsonResponse({
                'message': f'Трек {tracks[track_idx]} проигрывается',
                'state': {
                    'current_track': state['current_track'],
                    'played_tracks': state['played_tracks'],
                    'bingo_info': state['bingo_info'],
                    'triple_bingo_info': state['triple_bingo_info'],
                    'full_bingo_info': state['full_bingo_info']
                },
                'track_url': track_url
            })
        except Exception as e:
            print(f"Ошибка сервера: {e}")
            return JsonResponse({'error': 'Internal server error', 'details': str(e)}, status=500)

@login_required(login_url='/users/login/?/')
def clear_session(request):
    if request.method == 'POST':
        request.session['state'] = {
            'played_tracks': [],
            'current_track': None,
            'bingo_info': '',
            'triple_bingo_info': '',
            'full_bingo_info': '',
        }
        request.session.modified = True
        return JsonResponse({'message': 'Информация о лотто успешно очищена.'})
    return JsonResponse({'error': 'Неверный метод запроса.'}, status=400)

@login_required(login_url='/users/login/?/')
def get_tracks_state(request, id):
    """ Возвращает обновленные списки треков для `music_lotto_tracks.html` """
    folder_path = os.path.join('uploads', 'music_lotto', str(id))
    try:
        tracks = read_order_file(folder_path)  # Все треки
        available_tracks = [t for t in tracks if t not in state['played_tracks']]  # Только несыгранные

        return JsonResponse({
            # 'played_tracks': state['played_tracks'][-10:],  # Последние 10 треков
            'played_tracks': state['played_tracks'][-5:],  # Последние 10 треков
            'available_tracks': available_tracks  # Оставшиеся треки
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

import sys
import os
import pandas as pd
import pickle
import pygame
import numpy as np
from pygamevideo import Video
import threading

running = True
user_input = ''

play_start = 5



def get_user_input():
    global user_input
    while running:
        user_input = input("Введите номер трека для воспроизведения (или 'exit' для выхода): ")

input_thread = threading.Thread(target=get_user_input)
input_thread.start()

def read_order_file(folder_path):
    order_path = os.path.join(folder_path, 'order.xlsx')
    df = pd.read_excel(order_path)
    return df['Порядковый номер'].tolist()

def read_tickets_file(folder_path):
    tickets_path = os.path.join(folder_path, 'tickets.pkl')
    with open(tickets_path, 'rb') as f:
        tickets = pickle.load(f)
    return tickets

def check_bingo(ticket, played_tracks, current_track):
    bingo_results = []
    for i in range(5):
        row = ticket[i, :]
        column = ticket[:, i]
        if all(x in played_tracks for x in row):
            bingo_results.append(('Row', i))
        if all(x in played_tracks for x in column):
            bingo_results.append(('Column', i))

    main_diag = [ticket[i, i] for i in range(5)]
    sec_diag = [ticket[i, 4 - i] for i in range(5)]
    if all(x in played_tracks for x in main_diag):
        bingo_results.append(('Main diagonal', 0))
    if all(x in played_tracks for x in sec_diag):
        bingo_results.append(('Secondary diagonal', 0))

    return bingo_results

def play_tracks(folder_path, tracks, tickets_matrices):
    pygame.init()
    clock = pygame.time.Clock()
    pygame.mixer.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption('Music Bingo')
    font = pygame.font.Font(None, 45)

    font2 = pygame.font.Font(None, 50)
    color = (255, 255, 255)  # Белый цвет

    played_tracks = set()
    played_tracks_list = []  # Список для хранения порядка проигранных треков
    bingo_info = ''
    triple_bingo_info = ''
    full_bingo_info = ''  # Добавлено для отслеживания полного бинго
    is_video = False



    def play_track(idx, bingo_info, triple_bingo_info, full_bingo_info):
        global play_start
        pygame.mixer.music.stop()
        current_track = tracks[idx]
        mp3_path = os.path.join(folder_path, current_track + '.mp3')
        mp4_path = os.path.join(folder_path, current_track + '.mp4')

        if os.path.exists(mp4_path):
            video = Video(mp4_path)
            video.play()
        elif os.path.exists(mp3_path):
            video = False
            pygame.mixer.music.load(mp3_path)
            pygame.mixer.music.play(start=play_start)
        else:
            print("No valid media file found for", current_track)
            video = False

        played_tracks.add(current_track)
        played_tracks_list.append(current_track)
        if len(played_tracks_list) > 10:
            played_tracks_list.pop(0)

        for ticket_idx, ticket in enumerate(tickets_matrices):
            bingo_results = check_bingo(ticket, played_tracks, current_track)
            bingo_count = len(bingo_results)

            for bingo_type, line_idx in bingo_results:
                bingo_info += f' {ticket_idx + 1} '

            # Проверка на тройное бинго
            if bingo_count >= 3:
                triple_bingo_info += f' {ticket_idx + 1} '

            # Проверка на полное бинго
            if all(item in played_tracks for row in ticket for item in row):
                full_bingo_info += f' {ticket_idx + 1} '

        if os.path.exists(mp3_path):
            display_info(idx, bingo_info, triple_bingo_info, full_bingo_info, played_tracks_list)
        elif os.path.exists(mp4_path):
            display_info(idx, bingo_info, triple_bingo_info, full_bingo_info, played_tracks_list, False)

        return bingo_info, triple_bingo_info, full_bingo_info, video

    def display_info(idx, bingo_info, triple_bingo_info, full_bingo_info, played_tracks_list, audio=True):
        track_info_text = f"{idx + 1}. {tracks[idx]}"



        if audio:
             screen.fill((0, 0, 0))


        numbers = [int(num) for num in bingo_info.split()]
        unique_numbers = set(numbers)
        bingo_info = sorted(list(unique_numbers))



        if audio:
            y_offset1 = 100
            y_offset2 = 100
            for track in played_tracks_list:
                recent_track_rendered = font.render(track, True, color)
                recent_track_rect = recent_track_rendered.get_rect(center=(screen.get_width()*0.75, y_offset1))
                screen.blit(recent_track_rendered, recent_track_rect)
                y_offset1 += 60  # Увеличиваем отступ для следующего трека

            for idx, track in enumerate(tracks):
                row = idx // 10  # Вычисляем номер строки
                col = idx % 10   # Вычисляем номер столбца

                # Задаем координаты для отображения индексов
                x_offset = screen.get_width() * 0.05 + col * 55  # Расстояние между колонками
                y_offset = y_offset2 + row * 90  # Расстояние между строками

                # Определяем цвет: черный если трек в played_tracks_list, иначе белый
                color2 = (0, 0, 0) 
                if track not in played_tracks:
                    color2 = (255, 255, 255)

                recent_track_rendered = font2.render(str(idx + 1), True, color2)
                recent_track_rect = recent_track_rendered.get_rect(center=(x_offset, y_offset))
                screen.blit(recent_track_rendered, recent_track_rect)



            

        #os.system('clear')
        print(track_info_text)
        print(f'Bingo: {bingo_info}')
        print(f'Triple Bingo: {triple_bingo_info}')
        print(f'Full Bingo: {full_bingo_info}')
        print("Последние 10 треков:")
        for track in played_tracks_list:
            print(track)

        pygame.display.flip()


    paused = False  # Флаг для отслеживания состояния паузы
    fullscreen = False
    global running
    global user_input
    track_idx = 0


    while running:
        if user_input !='':
            if user_input.lower() == 'exit':
                running = False

            try:
                track_idx = int(user_input) - 1
                if 0 <= track_idx < len(tracks):
                    paused = False  # Сброс флага паузы при переключении трека
                    bingo_info, triple_bingo_info, full_bingo_info, video = play_track(track_idx, bingo_info, triple_bingo_info, full_bingo_info)
                else:
                    print(f"Некорректный номер трека. Введите число от 1 до {len(tracks)}.")
                
            except ValueError:
                print("Пожалуйста, введите числовое значение.")
        user_input = ''

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if paused:
                        if video:
                            video.resume()
                        pygame.mixer.music.unpause()
                        paused = False
                    else:
                        if video:
                            video.pause()
                        pygame.mixer.music.pause()
                        paused = True
                if event.key == pygame.K_f:  # Переключение режима по нажатию 'F'
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        # if track_idx >0:
                        #     bingo_info, triple_bingo_info, full_bingo_info, video = play_track(track_idx, bingo_info, triple_bingo_info, full_bingo_info)
                    else:
                        screen = pygame.display.set_mode((1280, 720))
                        # if track_idx > 0:
                        #     bingo_info, triple_bingo_info, full_bingo_info, video = play_track(track_idx, bingo_info, triple_bingo_info, full_bingo_info)

                    for idx, track in enumerate(tracks):
                        row = idx // 10  # Вычисляем номер строки
                        col = idx % 10   # Вычисляем номер столбца

                        # Задаем координаты для отображения индексов
                        x_offset = screen.get_width() * 0.05 + col * 55  # Расстояние между колонками
                        y_offset = 100 + row * 90  # Расстояние между строками

                        # Определяем цвет: черный если трек в played_tracks_list, иначе белый
                        color2 = (0, 0, 0) 
                        if track not in played_tracks:
                            color2 = (255, 255, 255)

                        recent_track_rendered = font2.render(str(idx + 1), True, color2)
                        recent_track_rect = recent_track_rendered.get_rect(center=(x_offset, y_offset))
                        screen.blit(recent_track_rendered, recent_track_rect)
                        pygame.display.flip()

    pygame.quit()
    input_thread.join()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python script.py имя_папки")
        sys.exit(1)

    folder_name = sys.argv[1]
    if not os.path.exists(folder_name):
        print(f"Папка {folder_name} не найдена.")
        sys.exit(1)

    if len(sys.argv) == 3 and sys.argv[2]:
        play_start=int(sys.argv[2])

    tracks = read_order_file(folder_name)
    tickets = read_tickets_file(folder_name)
    tickets_matrices = [np.array(ticket).reshape(5, 5) for ticket in tickets]
    play_tracks(folder_name, tracks, tickets_matrices)
    

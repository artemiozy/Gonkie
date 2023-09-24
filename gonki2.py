import tkinter as tk
import random
import keyboard
import winsound
import threading

background_music_thread = None

def play_background_music():
    global background_music_thread, sound_enabled
    if sound_enabled:
        filename = "Native_Home.wav"
        if background_music_thread is None or not background_music_thread.is_alive():
            background_music_thread = threading.Thread(target=winsound.PlaySound, args=(filename, winsound.SND_ASYNC))
            background_music_thread.start()


# Глобальная переменная для отслеживания состояния звука
sound_enabled = True

# Функция для включения/выключения звука
def toggle_sound():
    global sound_enabled
    sound_enabled = not sound_enabled
    if sound_enabled:
        play_background_music()  # Если звук включен, воспроизвести музыку
    else:
        winsound.PlaySound(None, winsound.SND_PURGE)  # Если звук выключен, остановить музыку

#Создание игрового холста
root = tk.Tk()
root.title("Гонки")
root.attributes('-fullscreen', True)
canvas_width = 500
canvas_height = 600
canvas = tk.Canvas(root)
canvas.pack()
canvas.place(relx=0.5, rely=0.43, anchor='center', width=canvas_width, height=canvas_height )
canvas.config(highlightbackground='cyan2')
root.config(width=canvas_width, height=canvas_height, bg="gray45")

# Загрузка изображений машин
player_car_image = tk.PhotoImage(file="abrobike.png")
enemy_car_images = [
    tk.PhotoImage(file="cops.png"),
    tk.PhotoImage(file="taxi.png"),
    tk.PhotoImage(file="gg.png"),
    tk.PhotoImage(file="enemy.png"),
    tk.PhotoImage(file="enemy2.png"),
    tk.PhotoImage(file="enemy3.png"),
    tk.PhotoImage(file="enemy4.png"),
    tk.PhotoImage(file="enemy5.png"),
]

# Загрузка изображений для фона (дороги)
road_images = [tk.PhotoImage(file="road1.png"), tk.PhotoImage(file="road2.png")]

# Размеры машин
car_width = 60
car_height = 70

# Отступы для учета крайней части машины игрока
player_margin_x = 44 / 2  # Ширина мотоцикла игрока
player_margin_y = 100 / 2  # Высота мотоцикла игрока

# Позиция игрока
player_x = canvas_width // 2
player_y = canvas_height - player_margin_y - 10  # Оставляем небольшой отступ от нижней границы

# Скорость игрока
player_speed = 3

# Отображение фона на холсте
background_images = [canvas.create_image(canvas_width // 2, canvas_height * i, image=image)
                     for i, image in enumerate(road_images)]

# Смещение фона в начале игры
background_offset = 0

# Создание игрока
player = canvas.create_image(player_x, player_y, image=player_car_image, anchor=tk.CENTER)

# Флаг для отслеживания начала игры
game_started = False

# Флаг для отслеживания проигрыша
game_over_flag = False

# Счетчик очков
score = 0
score_label = None

# Создание списка вражеских машин
enemies = []

# Максимальное количество противников на экране
max_enemies = 4

# Список координат всех активных машин противников
active_enemy_coordinates = []

def create_enemy():
    if len(enemies) < max_enemies:
        while True:
            x = random.randint(car_width // 2, canvas_width - car_width // 2)
            y = 0
            enemy_image = random.choice(enemy_car_images)
            new_enemy_coords = (x, y)
            # Проверяем, чтобы новые координаты не пересекались с координатами других машин
            if all(
                    abs(new_enemy_coords[0] - coord[0]) > car_width + 10
                    or abs(new_enemy_coords[1] - coord[1]) > car_height + 10
                    for coord in active_enemy_coordinates
            ):
                enemy = canvas.create_image(x, y, image=enemy_image, anchor=tk.CENTER)
                enemies.append({"id": enemy, "alive": True, "speed": random.randint(10, 19)})
                active_enemy_coordinates.append(new_enemy_coords)
                break


# Функция движения игрока
def move_player():
    global player_x, player_y, game_started
    if game_started:
        if keyboard.is_pressed("a") and player_x > player_margin_x:  # Влево
            player_x -= player_speed
        if keyboard.is_pressed("d") and player_x < canvas_width - player_margin_x:  # Вправо
            player_x += player_speed
        if keyboard.is_pressed("w") and player_y > player_margin_y:  # Вперед
            player_y -= player_speed
        if keyboard.is_pressed("s") and player_y < canvas_height - player_margin_y:  # Назад
            player_y += player_speed
        canvas.coords(player, player_x, player_y)
    root.after(10, move_player)  # Рекурсивный вызов функции для непрерывного отслеживания клавиш

# Функция движения вражеских машин
def move_enemies():
    global player_x, player_y, game_started, score, game_over_flag

    if game_started:
        create_enemy()
        collision = False
        enemies_to_remove = []

        for i, enemy in enumerate(enemies):
            if enemy["alive"]:
                try:
                    x, y = canvas.coords(enemy["id"])
                    if y > canvas_height:
                        enemy["alive"] = False
                        canvas.delete(enemy["id"])
                        enemies_to_remove.append(i)
                    else:
                        canvas.move(enemy["id"], 0, enemy["speed"])  # Двигаем машину вниз

                    # Проверяем столкновение с игроком
                    if (
                            player_x - player_margin_x < x + car_width / 2 and
                            player_x + player_margin_x > x - car_width / 2 and
                            player_y - player_margin_y < y + car_height / 2 and
                            player_y + player_margin_y > y - car_height / 2
                    ):
                        enemy["alive"] = False
                        collision = True  # Обновляем флаг столкновения
                        game_over_flag = True  # Устанавливаем флаг проигрыша
                        winsound.PlaySound(None, winsound.SND_PURGE)  # Остановить фоновую музыку

                except tk.TclError:
                    pass

        for index in enemies_to_remove:
            if index < len(active_enemy_coordinates):
                active_enemy_coordinates.pop(index)

        enemies[:] = [enemy for enemy in enemies if enemy["alive"]]

        if not collision:
            update_score(1)

        if game_over_flag:
            game_over()  # Вызываем функцию game_over, если игра окончена

        root.after(100, move_enemies)


# Функция завершения игры
def game_over():
    global game_started, score_label
    game_started = False  # Останавливаем игру
    canvas.delete("all")
    canvas.create_text(canvas_width // 2, canvas_height // 2, text="Игра окончена", font=("Algerian", 24))
    canvas.create_text(canvas_width // 2, canvas_height // 2 + 30, text="Ваш счёт - " + str(score),
                       font=("Algerian", 24))
    score_label.destroy()  # Удаляем счетчик очков


# Функция для движения фона (дороги)
def move_background():
    global game_started
    if game_started:
        for background_image in background_images:
            canvas.move(background_image, 0, 5)

        for i in range(len(background_images)):
            x, y = canvas.coords(background_images[i])
            if y >= canvas_height:
                prev_image_index = (i - 1) % len(background_images)
                canvas.coords(background_images[i], canvas_width // 2, canvas_height // 2 - canvas_height)
                canvas.coords(background_images[prev_image_index], canvas_width // 2, canvas_height // 2)

        root.after(20, move_background)


# Функция для обновления счета
def update_score(points):
    global score, score_label
    score += points
    if score_label is not None:
        score_label.config(text="Счёт: " + str(score))


# Запуск игры
def start_game():
    global game_started, score_label, score, game_over_flag
    score = 0  # Сброс счета при начале игры
    canvas.itemconfig(title_text, state=tk.HIDDEN)
    if score_label is not None:
        score_label.destroy()  # Удаляем предыдущий счетчик очков
    game_started = True
    game_over_flag = False  # Сброс флага проигрыша
    move_player()  # Запускаем функцию для управления игроком
    move_enemies()  # Запускаем функцию для движения противников
    move_background()  # Запускаем функцию для движения фона
    sound_enabled = True  # Изначально звук включен
    background_music_thread = None  # Переменная для отслеживания фоновой музыки
    sound_button = tk.Button(root, text="Музыка вкл/выкл", bg="gray", width=13, height=1, command=toggle_sound)
    sound_button.pack()
    start_button.destroy()
    score_label = tk.Label(root, text="Счёт: 0", bg="gray", font=("Algerian", 9))
    score_label.pack()
    play_background_music()  # Вызываем функцию для проигрывания музыки при запуске игры

title_text = canvas.create_text(canvas_width // 2, canvas_height // 3,  text="Гонки", font=("Courier New", 63,"bold"),
                                fill="red")
start_button = tk.Button(root, text="Играть",  bg="gray", width=10, height=1, command=start_game)
start_button.pack()
exit_button = tk.Button(root, text="Выход",  bg="gray", width=10, height=1,  command=root.destroy)
exit_button.pack()

root.mainloop()
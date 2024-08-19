import pygame
import os
from mutagen.mp3 import MP3

class Music:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.music_queue = self.find_music("music")
        self.music_pos = -1
        self.is_paused = False
        self.current_start_time = 0

        # Установим пользовательское событие для окончания трека
        self.MUSIC_END = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.MUSIC_END)

    def find_music(self, directory):
        """Ищет все MP3 файлы в указанной директории."""
        return [os.path.join(directory, filename)
                for filename in os.listdir(directory)
                if filename.endswith('.mp3')]

    def play(self, from_current=False):
        """Проигрывает текущий или следующий трек."""
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
        else:
            if not from_current and self.music_pos < len(self.music_queue) - 1:
                self.music_pos += 1
            if self.music_pos < len(self.music_queue):
                pygame.mixer.music.load(self.music_queue[self.music_pos])
                self.current_start_time = 0
                pygame.mixer.music.play()
                pygame.mixer.music.set_endevent(self.MUSIC_END)  # Включаем событие завершения трека


    def pause(self):
        """Ставит воспроизведение на паузу или снимает с паузы."""
        if pygame.mixer.music.get_busy():
            if self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False
            else:
                pygame.mixer.music.pause()
                self.is_paused = True

    def stop(self):
        """Останавливает воспроизведение и сбрасывает позицию."""
        pygame.mixer.music.stop()
        self.music_pos = -1
        self.is_paused = False
        self.current_start_time = 0

    def track(self, pos):
        self.music_pos = pos
        self.play(from_current=True)

    def next(self):
        """Переходит к следующему треку в очереди."""
        if self.music_pos < len(self.music_queue) - 1:
            self.music_pos += 1
            self.play(from_current=True)

    def unnext(self):
        """Возвращается к предыдущему треку в очереди."""
        if self.music_pos > 0:
            self.music_pos -= 1
            self.play(from_current=True)

    def set_time(self, seconds):
        """Перематывает трек на указанное количество секунд."""
        if self.music_pos >= 0 and self.music_pos < len(self.music_queue):
            total_time = self.get_total_time()  # Получаем общую продолжительность трека
            
            # Устанавливаем буфер перед концом трека
            if seconds >= total_time - 2:  # Буфер в 2 секунды перед концом трека
                seconds = total_time - 2

            pygame.mixer.music.stop()
            pygame.mixer.music.load(self.music_queue[self.music_pos])
            self.current_start_time = seconds
            pygame.mixer.music.play(start=seconds)
            
            # Обновляем событие окончания трека только если оно не близко к завершению
            if seconds < total_time - 2:
                pygame.mixer.music.set_endevent(self.MUSIC_END)
            else:
                pygame.mixer.music.set_endevent(None)  # Отключаем автоматическое переключение


    def get_total_time(self):
        """Возвращает общую продолжительность текущего трека в секундах."""
        if self.music_pos >= 0 and self.music_pos < len(self.music_queue):
            audio = MP3(self.music_queue[self.music_pos])
            return int(audio.info.length)
        return 0

    def get_elapsed_time(self):
        """Возвращает прошедшее время с начала воспроизведения текущего трека."""
        if pygame.mixer.music.get_busy():
            return int(pygame.mixer.music.get_pos() / 1000) + self.current_start_time
        return self.current_start_time

    def get_remaining_time(self):
        """Возвращает оставшееся время до конца трека в секундах."""
        total_time = self.get_total_time()
        elapsed_time = self.get_elapsed_time()
        return max(total_time - elapsed_time, 0)

class Console:
    def __init__(self):
        self.music = Music()

    def main(self):
        """Главный цикл консоли для управления музыкой."""
        while True:
            for event in pygame.event.get():
                if event.type == self.music.MUSIC_END:
                    self.music.next()  # Переход к следующему треку по завершении текущего

            x = input("> ").strip().lower()
            match x.split():
                case ["pause"]:
                    self.music.pause()
                case ["play"]:
                    if not pygame.mixer.music.get_busy() and not self.music.is_paused:
                        self.music.play()
                    elif self.music.is_paused:
                        self.music.play()
                case ["stop"]:
                    self.music.stop()
                case ["next"]:
                    self.music.next()
                case ["unnext"]:
                    self.music.unnext()
                case ["track", pos]:
                    try:
                        pos = int(pos)
                        self.music.track(pos=pos)
                    except ValueError:
                        print("Введите корректное количество секунд.")
                case ["all"]:
                    for index, filename in enumerate(self.music.music_queue, start=1):
                        print(f"{index}. {os.path.basename(filename)}")
                case ["seek", seconds]:
                    try:
                        seconds = int(seconds)
                        self.music.set_time(seconds)
                    except ValueError:
                        print("Введите корректное количество секунд.")
                case ["time"]:
                    total_time = self.music.get_total_time()
                    elapsed_time = self.music.get_elapsed_time()
                    remaining_time = self.music.get_remaining_time()
                    print(f"Общая продолжительность трека: {total_time} сек")
                    print(f"Прошло времени: {elapsed_time} сек")
                    print(f"Осталось времени: {remaining_time} сек")
                case ["exit"]:
                    self.music.stop()
                    break

if __name__ == "__main__":
    console = Console()
    console.main()

import pygame
import socket
import threading
import time
from datetime import datetime
import sqlite3

# Pygame başlatma
pygame.init()

# Ekran boyutları
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Akıllı Otopark Sistemi")

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)


def get_latest_status():
    """Veritabanından en son park yeri durumunu alır"""
    try:
        conn = sqlite3.connect('parking_system.db')  # Veritabanı adı güncellendi
        cursor = conn.cursor()
        cursor.execute("""
            SELECT status FROM parking_status 
            ORDER BY timestamp DESC 
            LIMIT 1
        """)
        result = cursor.fetchone()
        conn.close()

        if result:
            return result[0] == "Dolu"
        return False
    except Exception as e:
        print(f"Veritabanı okuma hatası: {e}")
        return False


class ParkingLot:
    def __init__(self):
        self.spaces = {i: False for i in range(1, 11)}  # False = Boş, True = Dolu
        # 2-10 arası rastgele dolu/boş durumları
        for i in range(2, 11):
            self.spaces[i] = bool(int(time.time() * i) % 2)  # Rastgele ama sabit durumlar

        # İlk başlatmada veritabanından son durumu al
        self.spaces[1] = get_latest_status()

        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Veritabanı güncelleme thread'ini başlat
        self.update_thread = threading.Thread(target=self.database_update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()

    def database_update_loop(self):
        """Veritabanını periyodik olarak kontrol eder ve görselleştirmeyi günceller"""
        while True:
            try:
                current_status = get_latest_status()
                self.spaces[1] = current_status
            except Exception as e:
                print(f"Güncelleme hatası: {e}")
            time.sleep(1)  # Her saniye kontrol et

    def draw(self, screen):
        # Başlık
        title = self.font.render("Akıllı Otopark Sistemi", True, BLACK)
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 20))

        # Park yerlerini çiz
        space_width = 120
        space_height = 150
        spaces_per_row = 5
        start_x = (WINDOW_WIDTH - (spaces_per_row * space_width)) // 2
        start_y = 100

        for i in range(1, 11):
            row = (i - 1) // spaces_per_row
            col = (i - 1) % spaces_per_row
            x = start_x + (col * space_width)
            y = start_y + (row * space_height)

            # Park yeri dikdörtgeni
            color = RED if self.spaces[i] else GREEN
            pygame.draw.rect(screen, color, (x, y, space_width - 10, space_height - 10))

            # Park yeri ID
            id_text = self.font.render(str(i), True, WHITE)
            screen.blit(id_text, (x + 10, y + 10))

            # Durum metni
            status = "DOLU" if self.spaces[i] else "BOŞ"
            status_text = self.font.render(status, True, WHITE)
            screen.blit(status_text, (x + 10, y + space_height - 40))

            # Sensör işareti (sadece 1 numaralı park yeri için)
            if i == 1:
                pygame.draw.rect(screen, BLUE, (x, y, space_width - 10, space_height - 10), 3)
                sensor_text = self.small_font.render("Sensörlü", True, BLACK)
                screen.blit(sensor_text, (x + 10, y + space_height - 70))

                # Son güncelleme zamanını göster
                try:
                    conn = sqlite3.connect('parking_system.db')  # Veritabanı adı güncellendi
                    cursor = conn.cursor()
                    cursor.execute("SELECT timestamp FROM parking_status ORDER BY timestamp DESC LIMIT 1")
                    last_update = cursor.fetchone()
                    conn.close()
                    if last_update:
                        update_text = self.small_font.render(f"Son: {last_update[0]}", True, BLACK)
                        screen.blit(update_text, (x + 10, y + space_height - 90))
                except Exception as e:
                    print(f"Zaman bilgisi alınamadı: {e}")

        # Lejant
        legend_y = start_y + (2 * space_height) + 20
        pygame.draw.rect(screen, GREEN, (start_x, legend_y, 20, 20))
        boş_text = self.small_font.render("BOŞ", True, BLACK)
        screen.blit(boş_text, (start_x + 30, legend_y))

        pygame.draw.rect(screen, RED, (start_x + 100, legend_y, 20, 20))
        dolu_text = self.small_font.render("DOLU", True, BLACK)
        screen.blit(dolu_text, (start_x + 130, legend_y))

        pygame.draw.rect(screen, WHITE, (start_x + 200, legend_y, 20, 20))
        pygame.draw.rect(screen, BLUE, (start_x + 200, legend_y, 20, 20), 3)
        sensor_text = self.small_font.render("Sensörlü Park Yeri", True, BLACK)
        screen.blit(sensor_text, (start_x + 230, legend_y))


def main():
    parking_lot = ParkingLot()
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Ekranı temizle
        screen.fill(WHITE)

        # Park yerlerini çiz
        parking_lot.draw(screen)

        # Ekranı güncelle
        pygame.display.flip()

        # FPS sınırı
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
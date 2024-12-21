import cv2
import numpy as np
import urllib.request
from ocr import process_plate
from database import init_db
import time


def live_camera_processing():
    """
    ESP32-CAM üzerinden anlık plaka algılama, giriş/çıkış işlemi,
    ve işlemden sonra 30 saniye bekleme.
    """
    # ESP32-CAM'in IP adresi ve stream URL'i
    esp32_cam_url = "http://192.168.1.16/stream"

    print("ESP32-CAM stream başlatılıyor...")

    last_plate_time = None  # Son plaka işleme zamanı
    last_detected_plate = None  # Son algılanan plaka

    connection_retry_count = 0
    max_retries = 5

    while True:
        try:
            # ESP32-CAM'den görüntü al
            img_resp = urllib.request.urlopen(esp32_cam_url)
            imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
            frame = cv2.imdecode(imgnp, -1)

            if frame is None:
                print("Frame alınamadı!")
                time.sleep(1)
                continue

            connection_retry_count = 0  # Başarılı bağlantıda sayacı sıfırla
            current_time = time.time()

            # Eğer 30 saniye geçmediyse işlem yapma
            if last_plate_time and (current_time - last_plate_time < 30):
                cv2.imshow("Plaka Algılama - ESP32-CAM", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue

            # Plaka algılama ve işleme
            plates = process_plate(frame)
            if plates:
                for plate in plates:
                    if plate != last_detected_plate:
                        print(f"Plaka algılandı: {plate}")
                        handle_vehicle_entry_exit(plate)  # Giriş/çıkış işlemi yap
                        last_detected_plate = plate
                        last_plate_time = current_time
                        break
            else:
                print("Plaka algılanamadı.")

            # Görüntüyü ekranda göster
            cv2.imshow("Plaka Algılama - ESP32-CAM", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        except Exception as e:
            print(f"Hata oluştu: {e}")
            connection_retry_count += 1

            if connection_retry_count >= max_retries:
                print(f"Maksimum bağlantı deneme sayısına ulaşıldı ({max_retries})")
                print("ESP32-CAM'e bağlantı kurulamıyor. Lütfen bağlantıyı kontrol edin.")
                break

            time.sleep(2)  # Hata durumunda 2 saniye bekle
            continue

    cv2.destroyAllWindows()


if __name__ == "__main__":
    init_db()  # Veritabanını başlat
    live_camera_processing()
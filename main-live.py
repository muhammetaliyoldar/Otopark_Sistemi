import cv2
from ocr import process_plate
from database import init_db
import time


def live_camera_processing():
    """
    Kamera üzerinden anlık plaka algılama, giriş/çıkış işlemi,
    ve işlemden sonra 30 saniye bekleme.
    """
    cap = cv2.VideoCapture(0)  # Kamerayı başlat
    if not cap.isOpened():
        print("Kamera başlatılamadı!")
        return

    print("Kamera açık. Çıkmak için 'q' tuşuna basın.")

    last_plate_time = None  # Son plaka işleme zamanı
    last_detected_plate = None  # Son algılanan plaka

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Kamera çerçevesi okunamadı!")
            break

        current_time = time.time()

        # Eğer 30 saniye geçmediyse işlem yapma
        if last_plate_time and (current_time - last_plate_time < 30):
            cv2.imshow("Plaka Algılama - Anlık Görüntü", frame)
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
                    last_plate_time = current_time  # Son işlem zamanını güncelle
                    break
        else:
            print("Plaka algılanamadı.")

        # Görüntüyü ekranda göster
        cv2.imshow("Plaka Algılama - Anlık Görüntü", frame)

        # Çıkış için 'q' tuşuna basın
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    init_db()  # Veritabanını başlat
    live_camera_processing()
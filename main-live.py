import cv2
from ocr import process_plate
from database import init_db

def live_camera_processing():
    """
    Kamera üzerinden anlık plaka algılama ve giriş/çıkış işlemi.
    """
    cap = cv2.VideoCapture(0)  # Kamera başlatılır

    if not cap.isOpened():
        print("Kamera başlatılamadı!")
        return

    print("Kamera açık. Çıkmak için 'q' tuşuna basın.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Kamera çerçevesi okunamadı!")
            break

        # Plaka algılama
        plates = process_plate(frame)
        print(f"Algılanan Plakalar: {plates}")

        # Görüntüyü göster
        cv2.imshow("Plaka Algılama - Anlık Görüntü", frame)

        # 'q' tuşu ile çıkış
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    init_db()  # Veritabanını başlat
    live_camera_processing()
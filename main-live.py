import cv2
from ultralytics import YOLO
import pytesseract
from datetime import datetime
from database import insert_entry, update_exit

# Tesseract OCR Yolu
pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# YOLOv11 Model Yolu
model_path = r'C:\Users\muham\PycharmProjects\Otopark_Sistemi\plate-detector.pt'
model = YOLO(model_path)

# Bellekte plakaların durumunu takip etmek için bir dictionary
plate_status = {}


def validate_plate(plate_text):
    """
    OCR'den gelen plaka metnini doğrular ve temizler.
    Türkiye plakası formatına uymayan metinleri filtreler.
    """
    import re
    plate_pattern = r'^[0-9]{2}\s?[A-Z]{1,3}\s?[0-9]{1,4}$'
    plate_text = re.sub(r'[^A-Z0-9\s]', '', plate_text.upper().strip())
    if re.match(plate_pattern, plate_text):
        return plate_text
    return None


def process_frame(frame):
    """
    Kamera çerçevesinde plaka tespiti yapar, OCR ile plakayı okur ve giriş/çıkış işlemi yapar.
    """
    results = model.predict(source=frame, save=False, save_txt=False)
    plates = []

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            plate_img = frame[y1:y2, x1:x2]
            plate_text = pytesseract.image_to_string(plate_img, config='--psm 7').strip()

            valid_plate = validate_plate(plate_text)
            if valid_plate:
                plates.append(valid_plate)

                # Giriş/Çıkış işlemi yap
                if valid_plate not in plate_status:
                    entry_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    insert_entry(valid_plate, entry_time)
                    plate_status[valid_plate] = "entry"
                    print(f"Plaka {valid_plate} kaydedildi. Giriş Saati: {entry_time}")
                elif plate_status[valid_plate] == "entry":
                    exit_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    update_exit(valid_plate, exit_time, calculate_fee(valid_plate))
                    plate_status[valid_plate] = "exit"
                    print(f"Plaka {valid_plate} çıkış yaptı. Çıkış Saati: {exit_time}")

            # Görselleştirme için kutular ve metin
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, valid_plate if valid_plate else "Geçersiz",
                        (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                        (0, 255, 0) if valid_plate else (0, 0, 255), 2)

    return frame, plates


def calculate_fee(plate):
    """
    Basit bir ücretlendirme hesaplama fonksiyonu.
    """
    from database import get_all_records
    records = get_all_records()
    for record in records:
        if record[1] == plate and record[3] is None:
            entry_time = datetime.strptime(record[2], '%Y-%m-%d %H:%M:%S')
            duration = (datetime.now() - entry_time).total_seconds() / 3600
            return round(duration * 10, 2)
    return 0


def live_camera_processing():
    """
    Anlık kamera görüntüsü üzerinden plaka algılama.
    """
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Kamera başlatılamadı!")
        return

    print("Kamera açık. Çıkmak için 'q' tuşuna basın.")

    frame_counter = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Kamera çerçevesi okunamadı!")
            break

        frame_counter += 1

        if frame_counter % 5 == 0:
            processed_frame, _ = process_frame(frame)
        else:
            processed_frame = frame

        cv2.imshow("Plaka Algılama - Anlık Görüntü", processed_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    from database import init_db

    init_db()
    live_camera_processing()
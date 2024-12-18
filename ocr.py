from ultralytics import YOLO
import pytesseract
import cv2
from database import add_parking_log, update_parking_log, add_parking_status
from datetime import datetime

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

MODEL_PATH = r'C:\Users\muham\PycharmProjects\Otopark_Sistemi\plate-detector.pt'
model = YOLO(MODEL_PATH)

def process_plate(image):
    """
    YOLO modeli ve Tesseract OCR ile plaka algılar ve giriş/çıkış işlemi yapar.
    """
    # YOLO modeliyle tahmin yap
    results = model.predict(source=image, save=False, save_txt=False)
    plates = []

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Koordinatları al
            cropped_img = image[y1:y2, x1:x2]  # Plaka bölgesini kırp

            # Tesseract ile OCR işlemi yap
            plate_text = pytesseract.image_to_string(cropped_img, config='--psm 7').strip()
            if plate_text:
                plates.append(plate_text)
                handle_vehicle_entry_exit(plate_text)  # Giriş/çıkış işlemini yap

    return plates

def handle_vehicle_entry_exit(plate_text):
    """
    Araç giriş/çıkış işlemini yönetir ve park durumunu günceller.
    """
    from database import get_all_parking_logs

    # Giriş/çıkış durumunu kontrol et
    logs = get_all_parking_logs()
    for log in logs:
        if log[1] == plate_text and log[3] is None:  # Çıkışı olmayan kayıt varsa
            exit_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            fee = calculate_fee(log[2])
            update_parking_log(plate_text, exit_time, fee)
            print(f"Plaka {plate_text} çıkış yaptı. Çıkış Saati: {exit_time}, Ücret: {fee} TL")

            # Park durumunu güncelle
            update_parking_status("Boş")
            return

    # Yeni giriş
    entry_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    add_parking_log(plate_text, entry_time)
    print(f"Plaka {plate_text} giriş yaptı. Giriş Saati: {entry_time}")

    # Park durumunu güncelle
    update_parking_status("Dolu")

def calculate_fee(entry_time):
    """
    Araç giriş-çıkış süresine göre ücret hesaplar.
    """
    entry_time = datetime.strptime(entry_time, '%Y-%m-%d %H:%M:%S')
    duration = (datetime.now() - entry_time).total_seconds() / 3600  # Saat cinsinden
    return round(duration * 10, 2)  # Saatlik 10 TL ücret

def update_parking_status(status):
    """
    Park durumu (Dolu/Boş) bilgilerini günceller.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    add_parking_status(status, timestamp)
    print(f"Park durumu güncellendi: {status}, Zaman: {timestamp}")
from ultralytics import YOLO
import cv2
import pytesseract
from datetime import datetime
from database import insert_entry, update_exit, get_all_records

# Tesseract OCR Yolu
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# YOLOv11 Model Yolu
model_path = r'C:\Users\muham\PycharmProjects\Otopark_Sistemi\plate-detector.pt'
model = YOLO(model_path)  # YOLOv11 modelini yükle

def detect_and_register_plate(image_path):
    """
    YOLOv11 ile plaka tespiti yapar, OCR ile plakayı okur ve veritabanına kaydeder.
    """
    img = cv2.imread(image_path)
    results = model.predict(source=img, save=False, save_txt=False)
    plates = []

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            plate_img = img[y1:y2, x1:x2]
            plate_text = pytesseract.image_to_string(plate_img, config='--psm 7').strip()
            plates.append(plate_text)
            if plate_text:
                entry_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                insert_entry(plate_text, entry_time)
                print(f"Plaka {plate_text} kaydedildi. Giriş Saati: {entry_time}")
    return plates

def detect_and_register_exit(image_path):
    """
    YOLOv11 ile plaka tespiti yapar, çıkış işlemini tamamlar ve veritabanını günceller.
    """
    img = cv2.imread(image_path)
    results = model.predict(source=img, save=False, save_txt=False)
    plates = []

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            plate_img = img[y1:y2, x1:x2]
            plate_text = pytesseract.image_to_string(plate_img, config='--psm 7').strip()
            plates.append(plate_text)
            if plate_text:
                exit_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                update_exit_info(plate_text, exit_time)
    return plates

def update_exit_info(plate, exit_time):
    """
    Veritabanında çıkış kaydını günceller ve ücreti hesaplar.
    """
    records = get_all_records()
    for record in records:
        if record[1] == plate and record[3] is None:
            entry_time = datetime.strptime(record[2], '%Y-%m-%d %H:%M:%S')
            duration = (datetime.now() - entry_time).total_seconds() / 3600
            fee = round(duration * 10, 2)
            update_exit(plate, exit_time, fee)
            print(f"Plaka {plate} çıkış yaptı. Çıkış Saati: {exit_time}, Ücret: {fee} TL")
            return
    print(f"Plaka {plate} için çıkış kaydı bulunamadı veya zaten çıkış yapılmış.")
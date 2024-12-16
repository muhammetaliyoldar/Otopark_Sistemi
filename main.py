import os
from database import init_db, get_all_records, clear_database
from ocr import detect_and_register_plate, detect_and_register_exit

# Görüntülerin bulunduğu klasör
IMAGE_FOLDER = r"C:\Users\muham\PycharmProjects\Otopark_Sistemi"

def process_all_images_for_entry():
    """
    Klasördeki tüm görüntüleri okuyarak araç giriş işlemi yapar.
    """
    for file_name in os.listdir(IMAGE_FOLDER):
        if file_name.lower().endswith(".jpg"):  # Sadece JPG dosyalarını işliyoruz
            image_path = os.path.join(IMAGE_FOLDER, file_name)
            print(f"Görüntü işleniyor: {image_path}")
            detected_plates = detect_and_register_plate(image_path)
            print(f"Giriş İşlemi - Tespit Edilen Plakalar: {detected_plates}")

def process_all_images_for_exit():
    """
    Klasördeki tüm görüntüleri okuyarak araç çıkış işlemi yapar.
    """
    for file_name in os.listdir(IMAGE_FOLDER):
        if file_name.lower().endswith(".jpg"):  # Sadece JPG dosyalarını işliyoruz
            image_path = os.path.join(IMAGE_FOLDER, file_name)
            print(f"Görüntü işleniyor: {image_path}")
            detected_plates = detect_and_register_exit(image_path)
            print(f"Çıkış İşlemi - Tespit Edilen Plakalar: {detected_plates}")

def main_menu():
    """
    Kullanıcı menüsü: Giriş, çıkış ve kayıt listeleme işlemleri için.
    """
    while True:
        print("\n1. Tüm Görüntüler için Araç Giriş")
        print("2. Tüm Görüntüler için Araç Çıkış")
        print("3. Kayıtları Listele")
        print("4. Veritabanını Sıfırla")
        print("5. Çıkış")
        choice = input("Seçiminiz: ")

        if choice == "1":
            process_all_images_for_entry()  # Tüm görüntüler için giriş işlemi
        elif choice == "2":
            process_all_images_for_exit()  # Tüm görüntüler için çıkış işlemi
        elif choice == "3":
            records = get_all_records()
            print("Veritabanındaki Kayıtlar:")
            for record in records:
                print(record)
        elif choice == "4":
            confirm = input("Veritabanını sıfırlamak istediğinize emin misiniz? (E/h): ")
            if confirm.lower() == "e":
                clear_database()
        elif choice == "5":
            print("Sistem kapatılıyor...")
            break
        else:
            print("Geçersiz seçim. Tekrar deneyin.")

if __name__ == "__main__":
    init_db()  # Veritabanını başlat
    main_menu()
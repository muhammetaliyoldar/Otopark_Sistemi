import os
from database import init_db, get_all_parking_logs, clear_table
from ocr import process_plate

def process_images_for_entry(folder_path):
    """
    Belirtilen klasördeki görüntüleri araç giriş işlemi için işler.
    """
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(folder_path, file_name)
            from cv2 import imread  # Görselleri okumak için cv2'den imread
            image = imread(image_path)  # Görseli oku
            plates = process_plate(image)  # Görsel üzerinden plaka algıla
            print(f"Giriş İşlemi - Algılanan Plakalar: {plates}")

def process_images_for_exit(folder_path):
    """
    Belirtilen klasördeki görüntüleri araç çıkış işlemi için işler.
    """
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(folder_path, file_name)
            from cv2 import imread  # Görselleri okumak için cv2'den imread
            image = imread(image_path)  # Görseli oku
            plates = process_plate(image)  # Görsel üzerinden plaka algıla
            print(f"Çıkış İşlemi - Algılanan Plakalar: {plates}")

def main_menu():
    """
    Ana menü.
    """
    folder_path = "C:/Users/muham/PycharmProjects/Otopark_Sistemi"  # Görsellerin olduğu klasör
    while True:
        print("\n1. Araç Giriş İşlemi")
        print("2. Araç Çıkış İşlemi")
        print("3. Araç Kayıtlarını Görüntüle")
        print("4. Kayıtları Sıfırla")
        print("5. Çıkış")
        choice = input("Seçiminiz: ")
        if choice == "1":
            process_images_for_entry(folder_path)
        elif choice == "2":
            process_images_for_exit(folder_path)
        elif choice == "3":
            logs = get_all_parking_logs()
            if logs:
                print("Araç Kayıtları:")
                for log in logs:
                    print(log)
            else:
                print("Veritabanında kayıt bulunamadı.")
        elif choice == "4":
            confirm = input("Tüm araç kayıtlarını sıfırlamak istediğinize emin misiniz? (E/h): ")
            if confirm.lower() == 'e':
                clear_table("parking_log")
                print("Araç kayıtları sıfırlandı.")
        elif choice == "5":
            print("Çıkış yapılıyor...")
            break
        else:
            print("Geçersiz seçim. Lütfen tekrar deneyin.")

if __name__ == "__main__":
    init_db()
    main_menu()
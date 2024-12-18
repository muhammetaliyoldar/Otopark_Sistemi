from database import (
    init_db, clear_table, add_parking_log, update_parking_log,
    add_parking_status, delete_parking_log, delete_parking_status,
    get_all_parking_logs, get_all_parking_status
)

def yönetim_menüsü():
    """
    Veritabanı yönetim menüsü (Türkçe).
    """
    while True:
        print("\n--- Veritabanı Yönetim Menüsü ---")
        print("1. Araç Kayıtlarını Yönet")
        print("2. Park Durumlarını Yönet")
        print("3. Kayıtları Listele")
        print("4. Veritabanını Sıfırla")
        print("5. Çıkış")
        seçim = input("Seçiminiz: ")

        if seçim == "1":
            araç_kayıt_menüsü()
        elif seçim == "2":
            park_durumu_menüsü()
        elif seçim == "3":
            kayıtları_listele()
        elif seçim == "4":
            tablo_adı = input("Sıfırlanacak tablo (parking_log / parking_status): ")
            clear_table(tablo_adı)
        elif seçim == "5":
            print("Çıkış yapılıyor...")
            break
        else:
            print("Geçersiz seçim! Lütfen tekrar deneyin.")

def araç_kayıt_menüsü():
    """
    Araç kayıtlarını yönetme menüsü.
    """
    while True:
        print("\n--- Araç Kayıtları Yönetim Menüsü ---")
        print("1. Yeni Araç Kaydı Ekle")
        print("2. Araç Kaydı Sil")
        print("3. Geri Dön")
        seçim = input("Seçiminiz: ")

        if seçim == "1":
            plaka = input("Plaka: ")
            giriş_saati = input("Giriş Saati (YYYY-MM-DD HH:MM:SS): ")
            add_parking_log(plaka, giriş_saati)
        elif seçim == "2":
            kayıt_id = input("Silinecek kayıt ID'si: ")
            delete_parking_log(kayıt_id)
        elif seçim == "3":
            break
        else:
            print("Geçersiz seçim! Lütfen tekrar deneyin.")

def park_durumu_menüsü():
    """
    Park durumlarını yönetme menüsü.
    """
    while True:
        print("\n--- Park Durumları Yönetim Menüsü ---")
        print("1. Yeni Durum Kaydı Ekle (Dolu/Boş)")
        print("2. Durum Kaydını Sil")
        print("3. Geri Dön")
        seçim = input("Seçiminiz: ")

        if seçim == "1":
            durum = input("Durum (Dolu/Boş): ")
            zaman_damgası = input("Zaman Damgası (YYYY-MM-DD HH:MM:SS): ")
            add_parking_status(durum, zaman_damgası)
        elif seçim == "2":
            kayıt_id = input("Silinecek kayıt ID'si: ")
            delete_parking_status(kayıt_id)
        elif seçim == "3":
            break
        else:
            print("Geçersiz seçim! Lütfen tekrar deneyin.")

def kayıtları_listele():
    """
    Tüm kayıtları listeler.
    """
    print("\n--- Araç Kayıtları ---")
    logs = get_all_parking_logs()
    if logs:
        for log in logs:
            print(log)
    else:
        print("Hiç araç kaydı bulunamadı.")

    print("\n--- Park Durumları ---")
    statuses = get_all_parking_status()
    if statuses:
        for status in statuses:
            print(status)
    else:
        print("Hiç park durumu kaydı bulunamadı.")

if __name__ == "__main__":
    init_db()
    yönetim_menüsü()
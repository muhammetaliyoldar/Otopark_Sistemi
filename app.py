from datetime import datetime
from database import insert_entry, update_exit, get_all_records

# Giriş İşlemi
def handle_entry(plate):
    entry_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    insert_entry(plate, entry_time)
    print(f"Giriş kaydedildi: {plate}, Saat: {entry_time}")

# Çıkış İşlemi
def handle_exit(plate):
    exit_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    records = get_all_records()
    for record in records:
        if record[1] == plate and record[3] is None:  # Çıkış yapılmamış kayıt
            entry_time = datetime.strptime(record[2], '%Y-%m-%d %H:%M:%S')
            duration = (datetime.now() - entry_time).total_seconds() / 3600
            fee = round(duration * 10, 2)  # Saatlik ücret: 10 TL
            update_exit(plate, exit_time, fee)
            print(f"Çıkış kaydedildi: {plate}, Saat: {exit_time}, Ücret: {fee} TL")
            return
    print("Plaka bulunamadı veya araç zaten çıkış yapmış.")
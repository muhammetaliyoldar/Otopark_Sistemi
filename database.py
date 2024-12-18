import sqlite3

def init_db():
    """
    Veritabanını başlatır ve gerekli tabloları oluşturur.
    """
    conn = sqlite3.connect("parking_system.db")
    cursor = conn.cursor()

    # Araç giriş/çıkış tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS parking_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plate TEXT NOT NULL,
        entry_time TEXT NOT NULL,
        exit_time TEXT,
        fee REAL
    )
    """)

    # Park yeri durumu tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS parking_status (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        status TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

# ----------------- Genel Silme ve Sıfırlama ------------------

def clear_table(table_name):
    """
    Belirtilen tabloyu sıfırlar (tüm kayıtları siler).
    """
    conn = sqlite3.connect("parking_system.db")
    cursor = conn.cursor()

    try:
        cursor.execute(f"DELETE FROM {table_name}")
        conn.commit()
        print(f"{table_name} tablosu sıfırlandı.")
    except sqlite3.OperationalError as e:
        print(f"Hata: {e}")
    finally:
        conn.close()

# ----------------- Araç Kayıtları İşlemleri ------------------

def add_parking_log(plate, entry_time):
    """
    Yeni bir araç giriş kaydı ekler.
    """
    conn = sqlite3.connect("parking_system.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO parking_log (plate, entry_time) VALUES (?, ?)", (plate, entry_time))
    conn.commit()
    print(f"Plaka {plate} giriş kaydı eklendi.")
    conn.close()

def update_parking_log(plate, exit_time, fee):
    """
    Araç çıkış kaydını günceller.
    """
    conn = sqlite3.connect("parking_system.db")
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE parking_log
    SET exit_time = ?, fee = ?
    WHERE plate = ? AND exit_time IS NULL
    """, (exit_time, fee, plate))
    conn.commit()
    print(f"Plaka {plate} çıkış kaydı güncellendi.")
    conn.close()

def delete_parking_log(log_id):
    """
    Belirli bir araç kaydını siler.
    """
    conn = sqlite3.connect("parking_system.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM parking_log WHERE id = ?", (log_id,))
    conn.commit()
    print(f"ID {log_id} araç kaydı silindi.")
    conn.close()

# ----------------- Park Durumu İşlemleri ------------------

def add_parking_status(status, timestamp):
    """
    Yeni bir park durumu kaydı ekler.
    """
    conn = sqlite3.connect("parking_system.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO parking_status (status, timestamp) VALUES (?, ?)", (status, timestamp))
    conn.commit()
    print(f"Park durumu ({status}) kaydı eklendi.")
    conn.close()

def delete_parking_status(status_id):
    """
    Belirli bir park durumu kaydını siler.
    """
    conn = sqlite3.connect("parking_system.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM parking_status WHERE id = ?", (status_id,))
    conn.commit()
    print(f"ID {status_id} park durumu kaydı silindi.")
    conn.close()

# ----------------- Kayıt Listeleme ------------------

def get_all_parking_logs():
    """
    Tüm araç giriş/çıkış kayıtlarını döndürür.
    """
    conn = sqlite3.connect("parking_system.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM parking_log")
    records = cursor.fetchall()
    conn.close()
    return records

def get_all_parking_status():
    """
    Tüm park yeri durum kayıtlarını döndürür.
    """
    conn = sqlite3.connect("parking_system.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM parking_status")
    records = cursor.fetchall()
    conn.close()
    return records
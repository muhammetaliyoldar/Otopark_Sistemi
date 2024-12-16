import sqlite3

def init_db():
    """
    Veritabanını başlatır ve tabloyu oluşturur.
    """
    conn = sqlite3.connect("parking_system.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS parking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plate TEXT NOT NULL,
        entry_time TEXT NOT NULL,
        exit_time TEXT,
        fee REAL
    )
    """)
    conn.commit()
    conn.close()

def insert_entry(plate, entry_time):
    """
    Yeni bir araç giriş kaydı ekler.
    """
    conn = sqlite3.connect("parking_system.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO parking (plate, entry_time) VALUES (?, ?)", (plate, entry_time))
    conn.commit()
    conn.close()

def update_exit(plate, exit_time, fee):
    """
    Araç çıkış kaydını günceller.
    """
    conn = sqlite3.connect("parking_system.db")
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE parking
    SET exit_time = ?, fee = ?
    WHERE plate = ? AND exit_time IS NULL
    """, (exit_time, fee, plate))
    conn.commit()
    conn.close()

def get_all_records():
    """
    Tüm kayıtları döndürür.
    """
    conn = sqlite3.connect("parking_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM parking")
    records = cursor.fetchall()
    conn.close()
    return records

def clear_database():
    """
    Veritabanındaki tüm kayıtları siler.
    """
    conn = sqlite3.connect("parking_system.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM parking")
    conn.commit()
    conn.close()
    print("Veritabanı sıfırlandı!")
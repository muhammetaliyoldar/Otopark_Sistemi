import socket
from database import init_db, add_parking_status

def start_tcp_server():
    """
    TCP sunucusunu başlatır ve gelen verileri işleyerek parking_status tablosuna kaydeder.
    """
    HOST = '192.168.1.6'  # Sunucu tüm ağ arayüzlerinde çalışır
    PORT = 12345      # ESP32 ile uyumlu port

    # Veritabanını başlat
    init_db()

    # Sunucu soketini oluştur-
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)  # Maksimum 5 bağlantı kuyruğu

    print(f"Sunucu {HOST}:{PORT} üzerinde çalışıyor, bağlantı bekleniyor...")

    while True:
        # Bağlantıyı kabul et
        client_socket, client_address = server_socket.accept()
        print(f"Bağlantı kabul edildi: {client_address}")

        try:
            # Veriyi al
            data = client_socket.recv(1024).decode().strip()
            if data:
                print(f"Gelen Veri: {data}")

                # Veriyi işleyerek parking_status tablosuna yaz
                process_data(data)
        except Exception as e:
            print(f"Veri işleme sırasında hata: {e}")
        finally:
            client_socket.close()
            print(f"Bağlantı kapatıldı: {client_address}")

def process_data(data):
    """
    Gelen veriyi ayıklar ve veritabanına kaydeder.
    """
    try:
        # Veriyi ayrıştır
        # Örnek veri: "Park Yeri: Dolu, Tarih: 18/12/2024, Saat: 14:30:15"
        parts = data.split(", ")
        status = parts[0].split(": ")[1]
        date = parts[1].split(": ")[1]
        time = parts[2].split(": ")[1]

        # Zaman damgasını oluştur
        timestamp = f"{date} {time}"

        # Veriyi veritabanına yaz
        add_parking_status(status, timestamp)
        print(f"Park durumu kaydedildi: {status}, Zaman Damgası: {timestamp}")
    except Exception as e:
        print(f"Veriyi işlerken hata oluştu: {e}")

if __name__ == "__main__":
    start_tcp_server()
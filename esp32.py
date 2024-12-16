import socket

def start_esp32_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 12345))
    server.listen(1)
    print("ESP32 sunucusu başlatıldı...")

    while True:
        client, addr = server.accept()
        data = client.recv(1024).decode()
        print(f"ESP32 Verisi: {data}")
        client.close()
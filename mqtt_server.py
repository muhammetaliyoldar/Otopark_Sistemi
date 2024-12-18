import paho.mqtt.client as mqtt
from database import insert_entry, update_exit
from datetime import datetime


# MQTT Callback Fonksiyonları
def on_connect(client, userdata, flags, rc):
    print("MQTT Bağlantısı Başarılı. Durum Kodu: ", rc)
    client.subscribe("parking/sensor")


def on_message(client, userdata, msg):
    data = msg.payload.decode()
    print(f"Gelen Veri: {data}")  # Örn: "Park 1, Dolu, 2024-12-13 14:23:45"

    try:
        park_id, status, timestamp = data.split(", ")
        plate = f"Dummy-{park_id}"  # Örnek plaka, gerçek plaka OCR tarafından tespit edilir.

        if status == "Dolu":
            print("Giriş işlemi kaydediliyor...")
            insert_entry(plate, timestamp)
        elif status == "Boş":
            print("Çıkış işlemi kaydediliyor...")
            exit_time = timestamp
            update_exit(plate, exit_time, fee=10.0)  # Örnek ücret, geliştirme yapılabilir.
    except Exception as e:
        print(f"Veri işlenirken hata oluştu: {e}")


# MQTT Sunucusunu Başlatma
def start_mqtt_server():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("192.168.1.6", 1883, 60)  # Lokal sunucu
    client.loop_forever()


if __name__ == "__main__":
    print("MQTT Sunucusu Başlatılıyor...")
    start_mqtt_server()
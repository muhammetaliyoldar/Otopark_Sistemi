import paho.mqtt.client as mqtt

# MQTT Callback Fonksiyonları
def on_connect(client, userdata, flags, rc):
    print("MQTT Bağlantısı Başarılı. Durum Kodu: ", rc)
    client.subscribe("parking/sensor")

def on_message(client, userdata, msg):
    data = msg.payload.decode()
    print(f"Gelen Veri: {data}")  # Örn: "Park 1, Dolu, 2024-12-13 14:23:45"

    # Gelen veriyi işleyin (örneğin, park durumunu güncellemek için)
    park_id, status, timestamp = data.split(", ")
    print(f"Park Yeri: {park_id}, Durum: {status}, Zaman: {timestamp}")

# MQTT Sunucusunu Başlatma
def start_mqtt_server():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("0.0.0.0", 1883, 60)  # Lokal sunucu
    client.loop_forever()

if __name__ == "__main__":
    print("MQTT Sunucusu Başlatılıyor...")
    start_mqtt_server()
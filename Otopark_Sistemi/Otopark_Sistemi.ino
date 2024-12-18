#include <WiFi.h>
#include <Wire.h>
#include "RTClib.h"

RTC_DS3231 rtc;

// Sensör ve LED pinleri
const int trigPin = 16;
const int echoPin = 4;
const int ledRed = 25;
const int ledGreen = 26;

// WiFi bilgileri
const char* ssid = "SUPERONLINE_Wi-Fi_1388";
const char* password = "3yDutU64TFFE";

// TCP sunucu bilgileri
const char* serverIP = "192.168.1.6";
const uint16_t serverPort = 12345;

WiFiClient client;

const float threshold = 100.0; // 1 metre eşik değeri (cm)
bool lastStatus = false; // Önceki durumun kaydı (dolu/boş)
unsigned long lastSendTime = 0; // Son veri gönderim zamanı
const unsigned long sendInterval = 60000; // 60 saniye aralık

void setup() {
  Serial.begin(115200);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(ledRed, OUTPUT);
  pinMode(ledGreen, OUTPUT);

  // RTC başlatma
  if (!rtc.begin()) {
    Serial.println("RTC modülü bulunamadı!");
    while (1);
  }

  if (rtc.lostPower()) {
    Serial.println("RTC saati doğru değil, bilgisayar saatine göre ayarlanıyor...");
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
  }

  // WiFi bağlantısı
  connectToWiFi();

  // TCP sunucu bağlantısı
  connectToServer();
}

void connectToWiFi() {
  Serial.println("WiFi'ye bağlanılıyor...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nWiFi bağlantısı başarılı!");
}

void connectToServer() {
  Serial.println("TCP sunucusuna bağlanılıyor...");
  while (!client.connect(serverIP, serverPort)) {
    Serial.println("Sunucuya bağlanılamadı, yeniden deneniyor...");
    delay(2000);
  }
  Serial.println("Sunucuya bağlanıldı!");
}

float measureDistance() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH);
  return duration * 0.034 / 2; // cm cinsinden mesafe
}

void loop() {
  float distance = measureDistance();
  DateTime now = rtc.now();

  bool currentStatus = distance <= threshold; // true: dolu, false: boş

  // Durum değişikliği veya belirli bir süre geçtiyse işlem yap
  if (currentStatus != lastStatus || (millis() - lastSendTime >= sendInterval)) {
    lastStatus = currentStatus;
    lastSendTime = millis();

    // LED durumunu değiştir
    digitalWrite(ledRed, currentStatus ? HIGH : LOW);
    digitalWrite(ledGreen, currentStatus ? LOW : HIGH);

    // Mesaj oluştur
    String statusMessage = String("Park Yeri: ") + (currentStatus ? "Dolu" : "Boş") +
                           ", Tarih: " + String(now.day()) + "/" + String(now.month()) + "/" + String(now.year()) +
                           ", Saat: " + String(now.hour()) + ":" + String(now.minute()) + ":" + String(now.second());

    Serial.println(statusMessage);

    // Sunucuya mesaj gönder
    if (!client.connected()) {
      connectToServer(); // Bağlantı kopmuşsa yeniden bağlan
    }
    if (client.connected()) {
      client.println(statusMessage);
      Serial.println("Mesaj sunucuya gönderildi.");
      
      // Geri bildirim kontrolü
      if (client.available()) {
        String response = client.readString();
        Serial.println("Sunucudan gelen cevap: " + response);
      }
    } else {
      Serial.println("Sunucu bağlantısı hala başarısız.");
    }
  }
}
#include <WiFi.h>
#include <Wire.h>
#include "RTClib.h"

RTC_DS3231 rtc;

// Sensör ve LED pinleri
const int trigPin = 16;
const int echoPin = 4;
const int ledRed = 26;
const int ledGreen = 27;
const int pirPin = 14; // PIR sensör pin

// WiFi bilgileri
const char* ssid = "SUPERONLINE_Wi-Fi_1388";
const char* password = "3yDutU64TFFE";

// TCP sunucu bilgileri
const char* serverIP = "192.168.1.6";
const uint16_t serverPort = 12345;

WiFiClient client;

const float thresholdLower = 160.0; // "Dolu" için alt eşik (cm)
const float thresholdUpper = 175.0; // "Boş" için üst eşik (cm)
bool lastStatus = false; // Önceki durum (false: boş, true: dolu)
unsigned long lastSendTime = 0; // Son veri gönderim zamanı
const unsigned long sendInterval = 30000; // 30 saniye minimum gönderim süresi

void setup() {
  Serial.begin(115200);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(ledRed, OUTPUT);
  pinMode(ledGreen, OUTPUT);
  pinMode(pirPin, INPUT);

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

float getAverageDistance(int numMeasurements) {
  float total = 0;
  int validReadings = 0;
  for (int i = 0; i < numMeasurements; i++) {
    float distance = measureDistance();
    if (distance > 2 && distance < 400) { // Geçerli mesafeler
      total += distance;
      validReadings++;
    }
    delay(50); // Ölçümler arasında küçük bir bekleme
  }
  return validReadings > 0 ? total / validReadings : -1; // Geçerli ölçüm yoksa -1 döner
}

bool determineParkingStatus(float distance) {
  if (lastStatus && distance > thresholdUpper) {
    return false; // Boş
  } else if (!lastStatus && distance < thresholdLower) {
    return true; // Dolu
  }
  return lastStatus; // Durumu koru
}

void loop() {
  int pirValue = digitalRead(pirPin);

  if (pirValue == HIGH) { // Hareket algılandıysa ultrasonik sensör devreye girer
    Serial.println("Hareket algılandı. Ultrasonik sensör aktif...");

    float avgDistance = getAverageDistance(5); // 5 ölçümün ortalamasını al
    Serial.print("Ölçülen Mesafe: ");
    Serial.print(avgDistance);
    Serial.println(" cm");

    if (avgDistance == -1) {
      Serial.println("Geçersiz mesafe ölçümü.");
      return; // Geçersiz ölçüm, devam etme
    }

    bool currentStatus = determineParkingStatus(avgDistance);

    // Durum değişikliği veya belirli bir süre geçtiyse işlem yap
    if (currentStatus != lastStatus || (millis() - lastSendTime >= sendInterval)) {
      lastStatus = currentStatus;
      lastSendTime = millis();

      // LED durumunu değiştir
      digitalWrite(ledRed, currentStatus ? HIGH : LOW);
      digitalWrite(ledGreen, currentStatus ? LOW : HIGH);

      // Mesaj oluştur
      DateTime now = rtc.now();
      String statusMessage = String("Park Yeri: ") + (currentStatus ? "Dolu" : "Boş") +
                             ", Tarih: " + String(now.day()) + "/" + String(now.month()) + "/" + String(now.year()) +
                             ", Saat: " + String(now.hour()) + ":" + String(now.minute()) + ":" + String(now.second());

      Serial.println("Gönderilen Mesaj: " + statusMessage);

      // Sunucuya mesaj gönder
      if (!client.connected()) {
        connectToServer(); // Bağlantı kopmuşsa yeniden bağlan
      }
      if (client.connected()) {
        client.println(statusMessage);
        Serial.println("Mesaj sunucuya gönderildi.");
      } else {
        Serial.println("Sunucu bağlantısı başarısız.");
      }
    }
  } else {
    Serial.println("Hareket algılanmadı. Ultrasonik sensör beklemede...");
    delay(500); // PIR sensör tekrar kontrol edilecek
  }
}

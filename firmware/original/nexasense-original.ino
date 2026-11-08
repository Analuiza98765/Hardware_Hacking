
#include <WiFi.h>
#include <DHT.h>
#include <WebServer.h>

// Sensor
#define DHT_PIN 15
#define DHT_TYPE DHT22

DHT dht(DHT_PIN, DHT_TYPE);

// Wi-Fi
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// Servidor HTTP
WebServer server(80);

void handleRoot() {
  server.send(200, "text/plain",
              "NexaSense IoT - Servidor funcionando!");
}

void handleSensor() {
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  if (isnan(temperature) || isnan(humidity)) {
    server.send(500, "application/json",
                "{\"erro\":\"Falha na leitura do sensor\"}");
    return;
  }

  String json = "{";
  json += "\"dispositivo\":\"NexaSense\",";
  json += "\"temperatura\":";
  json += String(temperature, 2) + ",";
  json += "\"umidade\":";
  json += String(humidity, 2);
  json += "}";

  server.send(200, "application/json", json);

  Serial.println("Requisicao HTTP recebida!");
  Serial.println(json);
}

void setup() {
  Serial.begin(115200);

  dht.begin();

  Serial.println("========================");
  Serial.println("     NEXASENSE IoT");
  Serial.println("========================");

  Serial.println("Conectando ao Wi-Fi...");

  WiFi.begin(ssid, password, 6);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWi-Fi conectado!");
  Serial.print("Endereco IP: ");
  Serial.println(WiFi.localIP());

  // Rotas HTTP
  server.on("/", HTTP_GET, handleRoot);
  server.on("/api/sensor", HTTP_GET, handleSensor);

  server.begin();

  Serial.println("API sem autenticacao configurada para teste.");

  Serial.println("------------------------");
  Serial.println("Servidor HTTP iniciado!");
  Serial.println("Rota: /api/sensor");
}

void loop() {
  server.handleClient();
}

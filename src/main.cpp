#include <WiFi.h>
#include <DHT.h>

#include <HTTPSServer.hpp>
#include <SSLCert.hpp>
#include <HTTPRequest.hpp>
#include <HTTPResponse.hpp>
#include <ResourceNode.hpp>

#include "certificates.h"
#include "secrets.h"

#ifndef NEXASENSE_API_KEY
#error "Configure NEXASENSE_API_KEY in src/secrets.h"
#endif

using namespace httpsserver;

constexpr uint8_t DHT_PIN = 15;
constexpr uint8_t DHT_TYPE = DHT22;
constexpr uint8_t WIFI_CHANNEL = 6;
constexpr unsigned long WIFI_TIMEOUT_MS = 10000;
constexpr uint16_t HTTPS_PORT = 443;
constexpr char WIFI_SSID[] = "Wokwi-GUEST";
constexpr char WIFI_PASSWORD[] = "";

DHT dht(DHT_PIN, DHT_TYPE);
const char* const apiKey = NEXASENSE_API_KEY;

SSLCert cert(
    example_crt_DER,
    example_crt_DER_len,
    example_key_DER,
    example_key_DER_len
);
HTTPSServer* secureServer = nullptr;

void handleRoot(HTTPRequest*, HTTPResponse* response) {
    response->setHeader("Content-Type", "text/plain");
    response->println("NexaSense IoT - Servidor HTTPS funcionando!");
}

void handleSensor(HTTPRequest* request, HTTPResponse* response) {
    if (request->getHeader("X-API-Key") != apiKey) {
        response->setStatusCode(401);
        response->setStatusText("Unauthorized");
        response->setHeader("Content-Type", "application/json");
        response->println("{\"erro\":\"Acesso nao autorizado\"}");
        Serial.println("Acesso negado: API Key invalida.");
        return;
    }

    const float humidity = dht.readHumidity();
    const float temperature = dht.readTemperature();

    if (isnan(temperature) || isnan(humidity)) {
        response->setStatusCode(500);
        response->setStatusText("Internal Server Error");
        response->setHeader("Content-Type", "application/json");
        response->println("{\"erro\":\"Falha na leitura do sensor\"}");
        return;
    }

    String json = "{\"dispositivo\":\"NexaSense\",\"temperatura\":";
    json += String(temperature, 2);
    json += ",\"umidade\":";
    json += String(humidity, 2);
    json += "}";

    response->setHeader("Content-Type", "application/json");
    response->println(json.c_str());

    Serial.println("Requisicao HTTPS autenticada recebida!");
    Serial.println(json);
}

void handleNotFound(HTTPRequest*, HTTPResponse* response) {
    response->setStatusCode(404);
    response->setStatusText("Not Found");
    response->setHeader("Content-Type", "application/json");
    response->println("{\"erro\":\"Rota nao encontrada\"}");
}

bool connectToWifi() {
    Serial.println("Conectando ao Wi-Fi...");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD, WIFI_CHANNEL);

    const unsigned long startTime = millis();
    while (WiFi.status() != WL_CONNECTED &&
           millis() - startTime < WIFI_TIMEOUT_MS) {
        delay(500);
        Serial.print(".");
    }

    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("\nFalha ao conectar ao Wi-Fi!");
        Serial.println("Tempo limite de conexao atingido.");
        return false;
    }

    Serial.println("\nWi-Fi conectado!");
    Serial.print("Endereco IP: ");
    Serial.println(WiFi.localIP());
    return true;
}

void startHttpsServer() {
    secureServer = new HTTPSServer(&cert, HTTPS_PORT);

    static ResourceNode rootNode("/", "GET", &handleRoot);
    static ResourceNode sensorNode("/api/sensor", "GET", &handleSensor);
    static ResourceNode notFoundNode("", "", &handleNotFound);

    secureServer->registerNode(&rootNode);
    secureServer->registerNode(&sensorNode);
    secureServer->setDefaultNode(&notFoundNode);

    if (secureServer->start()) {
        Serial.println("Servidor HTTPS iniciado!");
        Serial.println("Porta: 443");
        Serial.println("Rotas: / e /api/sensor");
        Serial.println("Autenticacao por API Key habilitada.");
        return;
    }

    Serial.println("Falha ao iniciar o servidor HTTPS!");
    delete secureServer;
    secureServer = nullptr;
}

void setup() {
    Serial.begin(115200);
    dht.begin();
    Serial.println("NEXASENSE IoT");

    if (connectToWifi()) {
        startHttpsServer();
    }
}

void loop() {
    if (secureServer != nullptr) {
        secureServer->loop();
    }
    delay(1);
}

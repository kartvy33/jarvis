/*
  JARVIS ESP32 device controller
  - Connects to Wi-Fi
  - Provides small HTTP API for JARVIS on the laptop
  - Controls the built-in LED
  - Add your own motors, relays, servos or sensors to the routes.

  Endpoints:
    /on
    /off
    /status
    /restart

  The token is a simple local-network protection. Change it before use.
*/

#include <WiFi.h>
#include <WebServer.h>

const char* WIFI_SSID = "YOUR_WIFI_NAME";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* JARVIS_TOKEN = "change-me";

#ifndef LED_BUILTIN
#define LED_BUILTIN 2
#endif

WebServer server(80);

bool authorized() {
  if (!server.hasArg("token")) return false;
  return server.arg("token") == JARVIS_TOKEN;
}

bool requireAuth() {
  if (!authorized()) {
    server.send(401, "text/plain", "Unauthorized");
    return false;
  }
  return true;
}

void handleOn() {
  if (!requireAuth()) return;
  digitalWrite(LED_BUILTIN, HIGH);
  server.send(200, "text/plain", "ESP32 LED is ON.");
}

void handleOff() {
  if (!requireAuth()) return;
  digitalWrite(LED_BUILTIN, LOW);
  server.send(200, "text/plain", "ESP32 LED is OFF.");
}

void handleStatus() {
  if (!requireAuth()) return;
  String state = digitalRead(LED_BUILTIN) ? "ON" : "OFF";
  server.send(200, "text/plain", "ESP32 online. LED: " + state);
}

void handleRestart() {
  if (!requireAuth()) return;
  server.send(200, "text/plain", "ESP32 restarting.");
  delay(250);
  ESP.restart();
}

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  Serial.begin(115200);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());

  server.on("/on", HTTP_GET, handleOn);
  server.on("/off", HTTP_GET, handleOff);
  server.on("/status", HTTP_GET, handleStatus);
  server.on("/restart", HTTP_GET, handleRestart);
  server.begin();

  Serial.println("JARVIS ESP32 server started.");
}

void loop() {
  server.handleClient();
}

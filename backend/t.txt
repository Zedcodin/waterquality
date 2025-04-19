#include <WiFi.h>
#include <WebServer.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// Network Configuration
const char* ap_ssid = "WaterQualityAP";
const char* ap_password = "cleanwater123";

// Pin Configuration 
const int turbidityPin = 34;    // Analog input for turbidity sensor
const int statusLedPin = 25;    // LED indicator
const int oledSda = 33;         // GPIO33 for OLED SDA
const int oledScl = 26;         // GPIO26 for OLED SCL
const int oneWireBus = 14;      // GPIO14 for DS18B20 temperature sensor

// Turbidity Calibration
const int clearWaterValue = 1670;  // Adjust based on your sensor
const int murkyWaterValue = 400;

// OLED Display Setup
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 32
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// DS18B20 Setup
OneWire oneWire(oneWireBus);
DallasTemperature sensors(&oneWire);

// Web Server
WebServer server(80);
IPAddress apIP(192, 168, 4, 1);  // Static IP for AP mode

void setup() {
  pinMode(statusLedPin, OUTPUT);
  digitalWrite(statusLedPin, LOW);
  Serial.begin(115200);

  // Initialize DS18B20
  sensors.begin();

  // Initialize I2C for OLED
  Wire.begin(oledSda, oledScl);
  
  // Initialize OLED
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("OLED initialization failed!");
    while (1); // Halt if display fails
  }

  // Start Access Point with fixed IP
  WiFi.softAPConfig(apIP, apIP, IPAddress(255, 255, 255, 0));
  WiFi.softAP(ap_ssid, ap_password);

  // Display WiFi credentials
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  display.println("WiFi: " + String(ap_ssid));
  display.setCursor(0, 10);
  display.println("Pass: " + String(ap_password));
  display.setCursor(0, 20);
  display.println("IP: " + apIP.toString());
  display.display();

  // Setup server routes
  server.on("/", handleRoot);
  server.on("/data", handleData);
  server.begin();

  digitalWrite(statusLedPin, HIGH);
  Serial.println("System initialized");
  Serial.println("AP IP: " + apIP.toString());
}

void loop() {
  server.handleClient();
  delay(10);
}

void handleRoot() {
  String html = "<html><body>";
  html += "<h1>Water Quality Monitor</h1>";
  html += "<p>Turbidity: <span id='turbidity'>--</span>%</p>";
  html += "<p>Temperature: <span id='temperature'>--</span>°C</p>";
  html += "<script>setInterval(()=>fetch('/data').then(r=>r.json()).then(d=>{";
  html += "document.getElementById('turbidity').innerText=d.turbidity;";
  html += "document.getElementById('temperature').innerText=d.temperature;";
  html += "}),1000)</script>";
  html += "</body></html>";
  server.send(200, "text/html", html);
}

void handleData() {
  // Read turbidity
  int rawValue = analogRead(turbidityPin);
  float turbidityPercent = map(rawValue, murkyWaterValue, clearWaterValue, 100, 0);
  turbidityPercent = constrain(turbidityPercent, 0, 100);

  // Read temperature
  sensors.requestTemperatures();
  float temperatureC = sensors.getTempCByIndex(0);

  // JSON response
  String json = "{\"turbidity\":" + String(turbidityPercent, 1) +
                ",\"temperature\":" + String(temperatureC, 1) + "}";
  server.send(200, "application/json", json);

  // Debugging output
  Serial.print("Raw: ");
  Serial.print(rawValue);
  Serial.print(" | Turbidity: ");
  Serial.print(turbidityPercent);
  Serial.print("% | Temp: ");
  Serial.print(temperatureC);
  Serial.println("°C");
}




// #include <WiFi.h>
// #include <WebServer.h>
// #include <Wire.h>
// #include <Adafruit_GFX.h>
// #include <Adafruit_SSD1306.h>


// // Network Configuration
// const char* ap_ssid = "WaterQualityAP";
// const char* ap_password = "cleanwater123";

// // Pin Configuration
// const int turbidityPin = 34;    // Analog input for sensor
// const int statusLedPin = 25;    // LED indicator
// const int oledSda = 33;        // GPIO33 for OLED SDA
// const int oledScl = 26;        // GPIO26 for OLED SCL

// // Turbidity Calibration
// const int clearWaterValue = 1670;  // Adjust these based on your sensor
// const int murkyWaterValue = 400;   // in clean and murky water tests

// // OLED Display Setup (128x32 pixels)
// #define SCREEN_WIDTH 128
// #define SCREEN_HEIGHT 32
// Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// WebServer server(80);
// IPAddress apIP(192, 168, 4, 1);  // Fixed AP IP address

// void setup() {
//   // Initialize hardware
//   pinMode(statusLedPin, OUTPUT);
//   digitalWrite(statusLedPin, LOW);
//   Serial.begin(115200);
  
//   // Initialize I2C with custom pins
//   Wire.begin(oledSda, oledScl);
  
//   // Initialize OLED
//   if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
//     Serial.println("OLED initialization failed!");
//     while(1); // Halt if display fails
//   }
  
//   // Start Access Point with fixed IP
//   WiFi.softAPConfig(apIP, apIP, IPAddress(255, 255, 255, 0));
//   WiFi.softAP(ap_ssid, ap_password);
  
//   // Display WiFi credentials with confirmed IP
//   display.clearDisplay();
//   display.setTextSize(1);
//   display.setTextColor(WHITE);
//   display.setCursor(0, 0);
//   display.println("WiFi: " + String(ap_ssid));
//   display.setCursor(0, 10);
//   display.println("Pass: " + String(ap_password));
//   display.setCursor(0, 20);
//   display.println("IP: " + apIP.toString());
//   display.display();

//   // Setup server endpoints
//   server.on("/", handleRoot);
//   server.on("/data", handleData);
//   server.begin();
  
//   digitalWrite(statusLedPin, HIGH); // System ready
//   Serial.println("System initialized");
//   Serial.println("AP IP: " + apIP.toString());
// }

// void loop() {
//   server.handleClient();
//   // int rawValue = analogRead(turbidityPin);
//   // Serial.print(rawValue);
//   delay(10);
// }

// void handleRoot() {
//   String html = "<html><body>";
//   html += "<h1>Water Quality Monitor</h1>";
//   html += "<p>Turbidity: <span id='turbidity'>--</span>%</p>";
//   html += "<script>setInterval(()=>fetch('/data').then(r=>r.json()).then(d=>";
//   html += "document.getElementById('turbidity').innerText=d.turbidity),1000)</script>";
//   html += "</body></html>";
//   server.send(200, "text/html", html);
// }

// void handleData() {
//   // Read sensor and calculate calibrated turbidity (0-100%)
//   int rawValue = analogRead(turbidityPin);
//   float turbidityPercent = map(rawValue, murkyWaterValue, clearWaterValue, 100, 0);
//   turbidityPercent = constrain(turbidityPercent, 0, 100);
  
//   // Return JSON response
//   String json = "{\"turbidity\":" + String(turbidityPercent, 1) + "}";
//   server.send(200, "application/json", json);
  
//   // Serial monitor output for calibration
//   Serial.print("Raw: ");
//   Serial.print(rawValue);
//   Serial.print(" | Turbidity: ");
//   Serial.print(turbidityPercent);
//   Serial.println("%");
// }
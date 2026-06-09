#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <AccelStepper.h>
#include <Servo.h>

// ==========================================
// CONFIGURAÇÕES DA REDE WI-FI
// ==========================================
const char* ssid = "Robo_da_PUC";
const char* password = "12345678";
ESP8266WebServer server(80);

// ==========================================
// MAPEAMENTO DE PINOS VALIDADO
// ==========================================
#define EN_PIN    D8   
#define X_STEP    D2   
#define X_DIR     D5   
#define Y_STEP    D3
#define Y_DIR     D6
#define Z_STEP    D4
#define Z_DIR     D7
#define A_STEP    D12  
#define A_DIR     D13  

#define SERVO1_PIN D9  // Endstop X-
#define SERVO2_PIN D10 // Endstop Y+

// ==========================================
// OBJETOS DOS MOTORES
// ==========================================
AccelStepper motorX(AccelStepper::DRIVER, X_STEP, X_DIR);
AccelStepper motorY(AccelStepper::DRIVER, Y_STEP, Y_DIR);
AccelStepper motorZ(AccelStepper::DRIVER, Z_STEP, Z_DIR);
AccelStepper motorA(AccelStepper::DRIVER, A_STEP, A_DIR);

Servo servo1;
Servo servo2;

void setup() {
  Serial.begin(115200);
  
  pinMode(EN_PIN, OUTPUT);
  digitalWrite(EN_PIN, LOW); // Mantém motores energizados/travados

  // Configuração de aceleração de todos os motores
  motorX.setAcceleration(10000.0);
  motorY.setAcceleration(10000.0);
  motorZ.setAcceleration(10000.0);
  motorA.setAcceleration(10000.0);

  // Inicializa servos na posição zero
  servo1.attach(SERVO1_PIN); servo1.write(0);
  servo2.attach(SERVO2_PIN); servo2.write(0);

  // Inicia o Ponto de Acesso Wi-Fi

  WiFi.softAP(ssid, password);
  Serial.println("\n\n=== SISTEMA WI-FI 6 EIXOS PRONTO ===");
  Serial.print("Conecte no WiFi: "); Serial.println(ssid);
  Serial.print("IP da API: "); Serial.println(WiFi.softAPIP());

  // ==========================================
  // ROTA DE COMANDO (Recebe a URL do Python)
  // ==========================================
  server.on("/run", []() {
    
    // Verifica se recebemos TODOS os 10 dados na URL
    if (server.hasArg("vX") && server.hasArg("pX") && 
        server.hasArg("vY") && server.hasArg("pY") && 
        server.hasArg("vZ") && server.hasArg("pZ") && 
        server.hasArg("vA") && server.hasArg("pA") && 
        server.hasArg("s1") && server.hasArg("s2")) {
      
      // Lê e converte os valores diretos da URL
      float vX = server.arg("vX").toFloat(); long pX = server.arg("pX").toInt();
      float vY = server.arg("vY").toFloat(); long pY = server.arg("pY").toInt();
      float vZ = server.arg("vZ").toFloat(); long pZ = server.arg("pZ").toInt();
      float vA = server.arg("vA").toFloat(); long pA = server.arg("pA").toInt();
      int s1   = server.arg("s1").toInt();   int s2   = server.arg("s2").toInt();

      // Atalhos dos Servos (0 = Fecha, 1 = Abre)
      if (s1 == 1) s1 = 180;
      if (s2 == 1) s2 = 180;

      // Executa Motores
      if (abs(vX) > 0) { motorX.setMaxSpeed(abs(vX)); motorX.move(pX); } else { motorX.stop(); }
      if (abs(vY) > 0) { motorY.setMaxSpeed(abs(vY)); motorY.move(pY); } else { motorY.stop(); }
      if (abs(vZ) > 0) { motorZ.setMaxSpeed(abs(vZ)); motorZ.move(pZ); } else { motorZ.stop(); }
      if (abs(vA) > 0) { motorA.setMaxSpeed(abs(vA)); motorA.move(pA); } else { motorA.stop(); }
            
      // Executa Servos
      servo1.write(constrain(s1, 0, 180));
      servo2.write(constrain(s2, 0, 180));

      Serial.println("Comando API Executado!");
      server.send(200, "text/plain", "OK");
    } else {
      Serial.println("Erro na API: Parametros faltando.");
      server.send(400, "text/plain", "ERRO: Faltam Parametros na URL");
    }
  });

  server.begin();
}

void loop() {
  server.handleClient(); // Escuta o Python pela rede
  motorX.run();
  motorY.run();
  motorZ.run();
  motorA.run();
  yield(); // Mantém o Wi-Fi estável
}

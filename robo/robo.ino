#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <AccelStepper.h>
#include <Servo.h>

// ==========================================
// CONFIGURAÇÕES DA REDE
// ==========================================
const char* ssid = "Robo_da_PUC";
const char* password = "puc-campinas";
ESP8266WebServer server(80);

// ==========================================
// MAPEAMENTO DE PINOS (CNC SHIELD V3)
// ==========================================
#define EN_PIN    D8   
#define X_STEP    D2   
#define X_DIR     D5   
#define A_STEP    D12  
#define A_DIR     D13  
#define SERVO_PIN D11
  

// ==========================================
// OBJETOS DOS MOTORES
// ==========================================
AccelStepper motorA(AccelStepper::DRIVER, A_STEP, A_DIR);
AccelStepper motorX(AccelStepper::DRIVER, X_STEP, X_DIR);
Servo meuServo;

// ==========================================
// INTERFACE WEB DE TESTE (Para o Celular/PC)
// ==========================================
void handleRoot() {
  String html = "<html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'>";
  html += "<style>";
  html += "body { text-align:center; font-family: monospace; background-color: #1a1a1a; color: #00ff00; padding: 20px; }";
  html += "input { width: 90%; height: 50px; font-size: 20px; margin: 20px 0; background: #333; color: #0f0; border: 1px solid #0f0; text-align: center; }";
  html += "button { width: 90%; height: 60px; font-size: 18px; font-weight: bold; border-radius: 10px; cursor: pointer; border: none; }";
  html += ".btn-send { background: #00ff00; color: #000; margin-bottom: 10px; }";
  html += ".btn-stop { background: #ff0000; color: #fff; }";
  html += ".info { color: #888; font-size: 14px; text-align: left; display: inline-block; }";
  html += "</style></head><body>";
  
  html += "<h2>> CONSOLE API DO ROBO</h2>";
  html += "<div class='info'><b>Comando:</b> VelA PassA VelX PassX Servo<br>";
  html += "<b>Servo:</b> 0 = Fechar | 1 = Abrir (180&deg;)</div>";
  
  html += "<input type='text' id='c' placeholder='500 1000 500 -1000 1' onkeypress='if(event.keyCode==13) send()'>";
  html += "<button class='btn-send' onclick='send()'>EXECUTAR COMANDO</button>";
  html += "<button class='btn-stop' onclick=\"cmd('0 0 0 0 0')\">PARAR TUDO</button>";
  
  // O JavaScript agora fatiar o texto e monta a URL com os parâmetros (igual o Python fará)
  html += "<script>";
  html += "function send(){ cmd(document.getElementById('c').value); }";
  html += "function cmd(v){";
  html += "  var p = v.trim().split(/\\s+/);";
  html += "  if(p.length == 5) {";
  html += "    fetch('/run?vA='+p[0]+'&pA='+p[1]+'&vX='+p[2]+'&pX='+p[3]+'&sA='+p[4]);";
  html += "  } else { alert('Erro: Digite exatamente 5 valores!'); }";
  html += "}";
  html += "</script></body></html>";
  
  server.send(200, "text/html", html);
}

// ==========================================
// SETUP PRINCIPAL
// ==========================================
void setup() {
  Serial.begin(115200);
  
  // Ativa os motores (EN_PIN em LOW significa drivers ligados)
  pinMode(EN_PIN, OUTPUT);
  digitalWrite(EN_PIN, LOW);

  // Configuração de aceleração para movimentos precisos e sem tranco
  motorA.setAcceleration(1000.0);
  motorX.setAcceleration(1000.0);

  // Inicializa o Servo fechado
  meuServo.attach(SERVO_PIN);
  meuServo.write(0);

  // Inicia o Ponto de Acesso Wi-Fi
  WiFi.softAP(ssid, password);
  Serial.println("\n\n=== SISTEMA INICIADO ===");
  Serial.print("Conecte no WiFi: "); Serial.println(ssid);
  Serial.print("IP do Robo API: "); Serial.println(WiFi.softAPIP());

  // ----------------------------------------
  // ROTAS DO SERVIDOR WEB / API
  // ----------------------------------------
  
  // 1. Rota raiz abre o painel HTML
  server.on("/", handleRoot);
  
  // 2. Rota "/run" recebe os comandos (Onde o Python vai conectar)
  server.on("/run", []() {
    
    // Confirma se o Python/Site mandou todas as 5 variáveis
    if (server.hasArg("vA") && server.hasArg("pA") && server.hasArg("vX") && server.hasArg("pX") && server.hasArg("sA")) {
      
      // Lê e converte os valores diretos da URL
      float vA = server.arg("vA").toFloat();
      long pA = server.arg("pA").toInt();
      float vX = server.arg("vX").toFloat();
      long pX = server.arg("pX").toInt();
      int sA = server.arg("sA").toInt();

      // Regra do Atalho para o Servo
      if (sA == 1) sA = 180; 

      // Aplica as velocidades e passa o alvo pros motores
      motorA.setMaxSpeed(abs(vA));
      motorA.move(pA);
      
      motorX.setMaxSpeed(abs(vX));
      motorX.move(pX);
      
      // Move o servo com limite de segurança
      meuServo.write(constrain(sA, 0, 180));

      // Feedback no Monitor Serial para debugar o Python
      Serial.printf("API Recebeu -> Motor A[%ld] | Motor X[%ld] | Servo[%d]\n", pA, pX, sA);
      
      // Responde pro Python que deu tudo certo
      server.send(200, "text/plain", "Comando Aceito");
    } 
    else {
      // Responde pro Python caso falte algum parâmetro (Ex: erro no envio)
      Serial.println("API ERRO: URL Incompleta.");
      server.send(400, "text/plain", "Erro: Faltam Parametros (vA, pA, vX, pX, sA)");
    }
  });

  // Coloca o servidor no ar
  server.begin();
}

// ==========================================
// LOOP INFINITO
// ==========================================
void loop() {
  server.handleClient(); // Mantém o servidor HTTP "ouvindo" a rede
  motorA.run();          // Processa passo a passo do Motor A
  motorX.run();          // Processa passo a passo do Motor X
  yield();               // Previne que o chip do WiFi trave e resete
}

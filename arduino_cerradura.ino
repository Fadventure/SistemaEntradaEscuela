/*
  Sistema de Control de Acceso con Reconocimiento Facial
  Escuela - Proyecto Integrador
  
  Conexiones:
  - Pin 9: Control del relé (cerradura eléctrica)
  - GND: Tierra común
  - USB: Comunicación con la PC
*/

const int PIN_CERRADURA = 9;    // Pin donde conectas el relé
const int TIEMPO_ABIERTA = 3000; // 3 segundos abierta

void setup() {
  // Configurar pin de la cerradura
  pinMode(PIN_CERRADURA, OUTPUT);
  digitalWrite(PIN_CERRADURA, LOW);  // Cerradura cerrada (seguro)
  
  // Iniciar comunicación con la PC
  Serial.begin(9600);
  
  // Esperar 2 segundos para que la PC se conecte
  delay(2000);
  
  Serial.println("🔒 Sistema de Control de Acceso Iniciado");
  Serial.println("Esperando comandos...");
  Serial.println("Comandos: A = Abrir, C = Cerrar, S = Estado");
}

void loop() {
  // Verificar si hay comandos desde la PC
  if (Serial.available() > 0) {
    char comando = Serial.read();
    
    switch(comando) {
      case 'A':  // Abrir puerta
      case 'a':
        abrirCerradura();
        break;
        
      case 'C':  // Cerrar puerta (manual)
      case 'c':
        cerrarCerradura();
        break;
        
      case 'S':  // Consultar estado
      case 's':
        enviarEstado();
        break;
        
      default:
        // Ignorar otros comandos
        break;
    }
  }
}

void abrirCerradura() {
  digitalWrite(PIN_CERRADURA, HIGH);
  Serial.println("🔓 PUERTA ABIERTA");
  
  // Esperar el tiempo configurado
  delay(TIEMPO_ABIERTA);
  
  // Cerrar automáticamente
  digitalWrite(PIN_CERRADURA, LOW);
  Serial.println("🔒 PUERTA CERRADA");
}

void cerrarCerradura() {
  digitalWrite(PIN_CERRADURA, LOW);
  Serial.println("🔒 PUERTA CERRADA (manual)");
}

void enviarEstado() {
  if (digitalRead(PIN_CERRADURA) == HIGH) {
    Serial.println("🔓 Estado: ABIERTA");
  } else {
    Serial.println("🔒 Estado: CERRADA");
  }
}
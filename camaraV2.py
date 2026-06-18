# camara.py - Sistema de Reconocimiento Facial con Control de Acceso
# Versión: 2.0 - Integración con Arduino

import os
import cv2
import pickle
import time
import datetime
import serial
import sys

# ============================================
# CONFIGURACIÓN
# ============================================

UMBRAL = 0.50  # Distancia máxima para considerar misma persona
BASE_DATOS = "alumnos_db.pkl"
REGISTRO_INGRESOS = "registro_ingresos.txt"
TEMP_IMG = "temp_captura.jpg"

# Configuración del Arduino
# 🔧 CAMBIA ESTO SEGÚN TU PUERTO
# En Windows: COM3, COM4, COM5, etc.
# En Linux: /dev/ttyUSB0, /dev/ttyACM0
PUERTO_ARDUINO = "COM3"  # <--- CAMBIA AQUÍ EL PUERTO CORRECTO
BAUDRATE = 9600

# ============================================
# INICIALIZACIÓN
# ============================================

# Silenciar advertencias de TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Importar DeepFace después de configurar el entorno
from deepface import DeepFace

# ============================================
# CONEXIÓN CON ARDUINO
# ============================================

arduino = None
arduino_conectado = False

def conectar_arduino():
    """Intenta conectar con el Arduino"""
    global arduino, arduino_conectado
    
    try:
        arduino = serial.Serial(
            port=PUERTO_ARDUINO,
            baudrate=BAUDRATE,
            timeout=1
        )
        time.sleep(2)  # Esperar a que Arduino se inicie
        arduino_conectado = True
        print(f"✅ Arduino conectado en {PUERTO_ARDUINO}")
        return True
    except Exception as e:
        arduino_conectado = False
        print(f"⚠️ No se pudo conectar a Arduino: {e}")
        print("   El sistema funcionará en modo SIMULACIÓN")
        print("   Para conectar, verifica el puerto y la conexión USB")
        return False

def abrir_puerta():
    """Envía señal al Arduino para abrir la cerradura"""
    if arduino_conectado and arduino:
        try:
            arduino.write(b'A')  # Enviar comando 'A' (Abrir)
            print("🔓 Señal enviada a Arduino: Abrir puerta")
            
            # Leer respuesta del Arduino
            respuesta = arduino.readline().decode().strip()
            if respuesta:
                print(f"   📟 Arduino: {respuesta}")
                
        except Exception as e:
            print(f"❌ Error al comunicarse con Arduino: {e}")
    else:
        # Modo simulación
        print("🔓 [SIMULACIÓN] Puerta abierta por 3 segundos")
        time.sleep(3)
        print("🔒 [SIMULACIÓN] Puerta cerrada")

# ============================================
# BASE DE DATOS
# ============================================

def cargar_base_datos():
    """Carga los embeddings de alumnos registrados"""
    if not os.path.exists(BASE_DATOS):
        print(f"❌ Base de datos no encontrada: {BASE_DATOS}")
        print("   Ejecuta registrar_alumnos.py primero")
        return None
    
    with open(BASE_DATOS, 'rb') as f:
        return pickle.load(f)

def registrar_ingreso(alumno, estado="CONCEDIDO"):
    """Registra el ingreso en un archivo de texto"""
    try:
        with open(REGISTRO_INGRESOS, "a", encoding="utf-8") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp} - {alumno} - {estado}\n")
            print(f"📝 Registro guardado: {alumno} - {estado}")
    except Exception as e:
        print(f"⚠️ Error al registrar ingreso: {e}")

# ============================================
# RECONOCIMIENTO FACIAL
# ============================================

def reconocer_rostro(ruta_imagen, base_datos):
    """Compara una imagen contra todos los alumnos registrados"""
    mejor_alumno = None
    mejor_distancia = float('inf')
    
    for alumno, datos in base_datos.items():
        try:
            resultado = DeepFace.verify(
                img1_path=ruta_imagen,
                img2_path=datos['imagen_referencia'],
                model_name='ArcFace',
                enforce_detection=False,
                silent=True
            )
            distancia = resultado['distance']
            
            if distancia < mejor_distancia:
                mejor_distancia = distancia
                mejor_alumno = alumno
                
        except Exception:
            continue
    
    return mejor_alumno, mejor_distancia

# ============================================
# INTERFAZ DE USUARIO
# ============================================

def mostrar_controles():
    """Muestra los controles disponibles"""
    print("\n" + "=" * 50)
    print("🎮 CONTROLES:")
    print("   [ESPACIO] - Capturar y reconocer rostro")
    print("   [ESC]     - Salir")
    print("   [R]       - Reconectar Arduino")
    print("   [S]       - Ver estado de la puerta")
    print("=" * 50)

def consultar_estado_puerta():
    """Consulta el estado de la puerta al Arduino"""
    if arduino_conectado and arduino:
        try:
            arduino.write(b'S')
            respuesta = arduino.readline().decode().strip()
            if respuesta:
                print(f"📟 Estado: {respuesta}")
        except Exception as e:
            print(f"❌ Error al consultar estado: {e}")
    else:
        print("ℹ️ Modo simulación - Arduino no conectado")

# ============================================
# PROGRAMA PRINCIPAL
# ============================================

def main():
    print("=" * 50)
    print("🎓 SISTEMA DE RECONOCIMIENTO FACIAL")
    print("   Control de Acceso con Arduino")
    print("=" * 50)
    
    # Intentar conectar con Arduino
    conectar_arduino()
    
    # Cargar base de datos
    base_datos = cargar_base_datos()
    if not base_datos:
        print("❌ No se pudo cargar la base de datos")
        return
    
    print(f"📊 Alumnos registrados: {len(base_datos)}")
    print("📸 Iniciando cámara...")
    
    mostrar_controles()
    
    # Iniciar cámara
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Error: No se pudo acceder a la cámara")
        print("   Verifica que la cámara esté conectada")
        return
    
    print("\n✅ Sistema listo. Esperando captura...\n")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Error al capturar frame")
            break
        
        # Mostrar frame con información
        cv2.imshow('Sistema de Reconocimiento Facial - Escuela', frame)
        
        # Esperar tecla
        key = cv2.waitKey(1) & 0xFF
        
        if key == 32:  # ESPACIO - Capturar
            # Guardar imagen temporal
            cv2.imwrite(TEMP_IMG, frame)
            
            print("\n🔍 Reconociendo rostro...")
            inicio = time.time()
            
            alumno, distancia = reconocer_rostro(TEMP_IMG, base_datos)
            
            fin = time.time()
            
            # Mostrar resultado
            print("-" * 40)
            if alumno and distancia < UMBRAL:
                print(f"✅ ¡ACCESO CONCEDIDO!")
                print(f"   👤 Alumno: {alumno.upper()}")
                print(f"   📏 Distancia: {distancia:.4f}")
                print(f"   ⏱️ Tiempo: {fin - inicio:.2f} seg")
                
                # Registrar ingreso
                registrar_ingreso(alumno, "ACCESO CONCEDIDO")
                
                # Abrir puerta con Arduino
                abrir_puerta()
                
            else:
                print(f"❌ ¡ACCESO DENEGADO!")
                if alumno:
                    print(f"   👤 Coincidencia cercana: {alumno} ({distancia:.4f})")
                    registrar_ingreso(alumno, "ACCESO DENEGADO")
                else:
                    print("   👤 No se detectó ningún rostro registrado")
                    registrar_ingreso("DESCONOCIDO", "ACCESO DENEGADO")
                
                print(f"   ⏱️ Tiempo: {fin - inicio:.2f} seg")
            print("-" * 40)
            print("\n📸 Presiona ESPACIO para nueva captura")
            
            # Limpiar archivo temporal
            if os.path.exists(TEMP_IMG):
                os.remove(TEMP_IMG)
                
        elif key == 27:  # ESC - Salir
            print("\n👋 Saliendo del sistema...")
            break
            
        elif key == ord('r') or key == ord('R'):  # R - Reconectar Arduino
            print("\n🔄 Reconectando Arduino...")
            conectar_arduino()
            
        elif key == ord('s') or key == ord('S'):  # S - Estado puerta
            consultar_estado_puerta()
    
    # Liberar recursos
    cap.release()
    cv2.destroyAllWindows()
    
    if arduino_conectado and arduino:
        arduino.close()
        print("🔌 Conexión con Arduino cerrada")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Sistema interrumpido por el usuario")
        print("👋 Saliendo...")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        sys.exit(1)
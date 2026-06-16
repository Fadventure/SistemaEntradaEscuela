# camara.py - Sistema de reconocimiento facial con cámara web
from deepface import DeepFace
import cv2
import pickle
import time
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Configuración
UMBRAL = 0.50
BASE_DATOS = "alumnos_db.pkl"
TEMP_IMG = "temp_captura.jpg"

# Silenciar advertencias de TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

def cargar_base_datos():
    """Carga los embeddings de alumnos registrados"""
    if not os.path.exists(BASE_DATOS):
        print(f"❌ Base de datos no encontrada. Ejecuta registrar_alumnos.py primero.")
        return None
    with open(BASE_DATOS, 'rb') as f:
        return pickle.load(f)

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
                silent=True  # Reduce verbosidad
            )
            distancia = resultado['distance']
            
            if distancia < mejor_distancia:
                mejor_distancia = distancia
                mejor_alumno = alumno
                
        except Exception as e:
            continue
    
    return mejor_alumno, mejor_distancia

def main():
    print("=" * 50)
    print("🎓 SISTEMA DE RECONOCIMIENTO FACIAL")
    print("=" * 50)
    
    # Cargar base de datos
    base_datos = cargar_base_datos()
    if not base_datos:
        return
    
    print(f"📊 Alumnos registrados: {len(base_datos)}")
    print("📸 Iniciando cámara...")
    print("\n🎮 CONTROLES:")
    print("   [ESPACIO] - Capturar y reconocer rostro")
    print("   [ESC]     - Salir")
    print("   [R]       - Reintentar (si no detecta rostro)")
    print("-" * 50)
    
    # Iniciar cámara
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Error: No se pudo acceder a la cámara")
        return
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Error al capturar frame")
            break
        
        # Mostrar frame
        cv2.imshow('Sistema de Reconocimiento Facial - Escuela', frame)
        
        # Esperar tecla
        key = cv2.waitKey(1) & 0xFF
        
        if key == 32:  # ESPACIO
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
                
                # Aquí luego se conectará con MySQL para registrar ingreso
                # y con Arduino para abrir puerta
                
            else:
                print(f"❌ ¡ACCESO DENEGADO!")
                print(f"   👤 Persona no registrada")
                if alumno:
                    print(f"   📏 Coincidencia más cercana: {alumno} ({distancia:.4f})")
                print(f"   ⏱️ Tiempo: {fin - inicio:.2f} seg")
            print("-" * 40)
            print("\n📸 Presiona ESPACIO para nueva captura")
            
            # Limpiar archivo temporal
            if os.path.exists(TEMP_IMG):
                os.remove(TEMP_IMG)
                
        elif key == 27:  # ESC
            print("\n👋 Saliendo del sistema...")
            break
        elif key == ord('r') or key == ord('R'):  # R
            print("🔄 Reiniciando cámara...")
    
    # Liberar recursos
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
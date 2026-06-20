# reconocer.py
from deepface import DeepFace
import pickle
import os
import time

BASE_DATOS = "alumnos_db.pkl"
UMBRAL = 0.50  # Más bajo = más estricto (menos falsos positivos)

def cargar_base_datos():
    """Carga los embeddings guardados"""
    if not os.path.exists(BASE_DATOS):
        print(f"❌ Base de datos no encontrada. Ejecuta registrar_alumnos.py primero.")
        return None
    
    with open(BASE_DATOS, 'rb') as f:
        return pickle.load(f)

def buscar_alumno(ruta_imagen, base_datos):
    """Compara una imagen contra todos los alumnos registrados"""
    try:
        # Obtener embedding de la imagen a reconocer
        resultado = DeepFace.represent(
            img_path=ruta_imagen,
            model_name='ArcFace',
            enforce_detection=False
        )
        
        if not resultado:
            return None, float('inf')
        
        embedding_buscado = resultado[0]['embedding']
        
        # Comparar contra cada alumno
        mejor_coincidencia = None
        menor_distancia = float('inf')
        
        for alumno, datos in base_datos.items():
            # Calcular distancia entre embeddings
            # DeepFace puede calcular distancia directamente
            distancia = DeepFace.verify(
                img1_path=ruta_imagen,
                img2_path=datos['imagen_referencia'],
                model_name='ArcFace',
                enforce_detection=False
            )['distance']
            
            if distancia < menor_distancia:
                menor_distancia = distancia
                mejor_coincidencia = alumno
        
        return mejor_coincidencia, menor_distancia
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, float('inf')

def main():
    print("=" * 50)
    print("🔍 SISTEMA DE RECONOCIMIENTO")
    print("=" * 50)
    
    # Cargar base de datos
    base_datos = cargar_base_datos()
    if not base_datos:
        return
    
    print(f"📊 Alumnos registrados: {list(base_datos.keys())}")
    
    # Pedir imagen a reconocer
    ruta_imagen = input("\n📸 Ruta de la imagen a reconocer: ")
    
    if not os.path.exists(ruta_imagen):
        print(f"❌ No se encuentra: {ruta_imagen}")
        return
    
    print("\n🔍 Buscando coincidencia...")
    inicio = time.time()
    
    alumno, distancia = buscar_alumno(ruta_imagen, base_datos)
    
    fin = time.time()
    
    print("\n" + "=" * 50)
    print("📊 RESULTADO")
    print("=" * 50)
    
    if alumno and distancia < UMBRAL:
        print(f"✅ ¡RECONOCIDO! Alumno: {alumno}")
        print(f"📏 Distancia: {distancia:.4f}")
        print(f"🎯 Umbral usado: {UMBRAL}")
    else:
        print(f"❌ ACCESO DENEGADO - Persona no registrada")
        print(f"📏 Distancia: {distancia:.4f} (mayor al umbral {UMBRAL})")
    
    print(f"⏱️ Tiempo: {fin - inicio:.2f} segundos")

if __name__ == "__main__":
    main()
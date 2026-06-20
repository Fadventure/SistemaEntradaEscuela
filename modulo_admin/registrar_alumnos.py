# registrar_alumnos.py
from deepface import DeepFace
import os
import pickle  # Para guardar la base de datos

# Configuración
BASE_DATOS = "alumnos_db.pkl"
CARPETA_ALUMNOS = "rostros/alumnos_registrados"

def obtener_embedding(ruta_imagen):
    """Convierte una imagen en un vector numérico (embedding)"""
    try:
        # DeepFace puede extraer el embedding directamente
        embedding = DeepFace.represent(
            img_path=ruta_imagen,
            model_name='ArcFace',
            enforce_detection=False  # No falla si no detecta rostro
        )
        return embedding[0]['embedding']
    except Exception as e:
        print(f"❌ Error procesando {ruta_imagen}: {e}")
        return None

def registrar_alumnos():
    """Recorre la carpeta de alumnos y guarda sus embeddings"""
    base_datos = {}
    
    # Recorrer cada alumno (cada subcarpeta)
    for alumno in os.listdir(CARPETA_ALUMNOS):
        carpeta_alumno = os.path.join(CARPETA_ALUMNOS, alumno)
        if not os.path.isdir(carpeta_alumno):
            continue
            
        print(f"\n📝 Registrando a: {alumno}")
        
        # Buscar todas las imágenes del alumno
        imagenes = []
        for archivo in os.listdir(carpeta_alumno):
            if archivo.lower().endswith(('.png', '.jpg', '.jpeg')):
                imagenes.append(os.path.join(carpeta_alumno, archivo))
        
        if not imagenes:
            print(f"  ⚠️ No se encontraron imágenes para {alumno}")
            continue
        
        # Usar la primera imagen para registrar (idealmente la mejor foto)
        ruta_principal = imagenes[0]
        embedding = obtener_embedding(ruta_principal)
        
        if embedding:
            base_datos[alumno] = {
                'embedding': embedding,
                'imagen_referencia': ruta_principal,
                'total_imagenes': len(imagenes)
            }
            print(f"  ✅ {alumno} registrado correctamente")
            print(f"     Imagen: {os.path.basename(ruta_principal)}")
        else:
            print(f"  ❌ Falló el registro de {alumno}")
    
    # Guardar la base de datos
    with open(BASE_DATOS, 'wb') as f:
        pickle.dump(base_datos, f)
    
    print(f"\n💾 Base de datos guardada: {BASE_DATOS}")
    print(f"📊 Alumnos registrados: {len(base_datos)}")
    return base_datos

if __name__ == "__main__":
    print("=" * 50)
    print("📚 REGISTRO DE ALUMNOS")
    print("=" * 50)
    registrar_alumnos()
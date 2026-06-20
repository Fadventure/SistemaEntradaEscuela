# db_manager.py - Gestor centralizado de la base de datos
import os
import pickle
import datetime

# ============================================
# CONFIGURACIÓN DE RUTAS
# ============================================

# Obtener la ruta de la carpeta base_datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DATOS = os.path.join(BASE_DIR, "alumnos_db.pkl")

# La carpeta logs está al mismo nivel que base_datos
PROJECT_DIR = os.path.dirname(BASE_DIR)
REGISTRO_INGRESOS = os.path.join(PROJECT_DIR, "logs", "registro_ingresos.txt")

# ============================================
# FUNCIONES DE BASE DE DATOS
# ============================================

def cargar_db():
    """Carga la base de datos de alumnos"""
    try:
        if os.path.exists(BASE_DATOS):
            with open(BASE_DATOS, 'rb') as f:
                return pickle.load(f)
        else:
            return {}
    except Exception as e:
        print(f"❌ Error al cargar base de datos: {e}")
        return {}

def guardar_db(db):
    """Guarda la base de datos de alumnos"""
    try:
        with open(BASE_DATOS, 'wb') as f:
            pickle.dump(db, f)
        return True
    except Exception as e:
        print(f"❌ Error al guardar base de datos: {e}")
        return False

def agregar_alumno(nombre, embedding, ruta_foto, curso=""):
    """Agrega un nuevo alumno a la base de datos"""
    db = cargar_db()
    db[nombre] = {
        'embedding': embedding,
        'imagen_referencia': ruta_foto,
        'fecha_registro': datetime.datetime.now().strftime("%Y-%m-%d"),
        'curso': curso
    }
    return guardar_db(db)

def eliminar_alumno(nombre):
    """Elimina un alumno de la base de datos"""
    db = cargar_db()
    if nombre in db:
        del db[nombre]
        return guardar_db(db)
    return False

def listar_alumnos():
    """Retorna la lista de nombres de alumnos registrados"""
    db = cargar_db()
    return list(db.keys())

def obtener_alumno(nombre):
    """Retorna los datos de un alumno específico"""
    db = cargar_db()
    return db.get(nombre, None)

# ============================================
# FUNCIONES DE REGISTRO DE INGRESOS
# ============================================

def registrar_ingreso(alumno, estado):
    """Registra un ingreso en el archivo de logs"""
    try:
        # Asegurar que la carpeta logs existe
        os.makedirs(os.path.dirname(REGISTRO_INGRESOS), exist_ok=True)
        
        with open(REGISTRO_INGRESOS, "a", encoding="utf-8") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp} - {alumno} - {estado}\n")
        return True
    except Exception as e:
        print(f"⚠️ Error al registrar ingreso: {e}")
        return False

def obtener_registros_hoy():
    """Retorna los registros de ingreso del día de hoy"""
    try:
        if not os.path.exists(REGISTRO_INGRESOS):
            return []
        
        hoy = datetime.datetime.now().strftime("%Y-%m-%d")
        registros = []
        
        with open(REGISTRO_INGRESOS, "r", encoding="utf-8") as f:
            for linea in f:
                if hoy in linea:
                    registros.append(linea.strip())
        return registros
    except Exception as e:
        print(f"⚠️ Error al leer registros: {e}")
        return []

# ============================================
# FUNCIONES DE RESPALDO
# ============================================

def crear_respaldo():
    """Crea un respaldo de la base de datos"""
    try:
        import shutil
        respaldo_dir = os.path.join(os.path.dirname(BASE_DATOS), "backups")
        os.makedirs(respaldo_dir, exist_ok=True)
        
        fecha = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        respaldo_path = os.path.join(respaldo_dir, f"alumnos_db_backup_{fecha}.pkl")
        
        if os.path.exists(BASE_DATOS):
            shutil.copy2(BASE_DATOS, respaldo_path)
            print(f"✅ Respaldo creado: {respaldo_path}")
            return True
        return False
    except Exception as e:
        print(f"❌ Error al crear respaldo: {e}")
        return False

# ============================================
# PRUEBA DEL MÓDULO
# ============================================

if __name__ == "__main__":
    print("=" * 50)
    print("📚 DB MANAGER - Prueba de conexión")
    print("=" * 50)
    
    # Probar carga
    db = cargar_db()
    print(f"✅ Alumnos cargados: {len(db)}")
    
    # Probar listado
    alumnos = listar_alumnos()
    print(f"📋 Lista de alumnos: {alumnos}")
    
    # Probar registro de ingreso
    registrar_ingreso("TEST", "PRUEBA")
    print("✅ Registro de ingreso probado")
    
    print("=" * 50)
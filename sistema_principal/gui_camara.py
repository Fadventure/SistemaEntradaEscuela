# gui_camara.py - Sistema de Reconocimiento Facial con Interfaz Gráfica
# Versión 2.3 - Con db_manager centralizado

import os
import sys
import cv2
import time
import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk
import numpy as np

# ============================================
# CONFIGURACIÓN DE RUTAS
# ============================================

# Obtener la raíz del proyecto (un nivel arriba de sistema_principal/)
RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ_PROYECTO)

# ============================================
# CONFIGURACIÓN
# ============================================

UMBRAL = 0.50
TEMP_IMG = "temp_captura.jpg"

# Silenciar advertencias de TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from deepface import DeepFace
from base_datos.db_manager import cargar_db, registrar_ingreso

# ============================================
# CLASE PRINCIPAL DE LA GUI
# ============================================

class SistemaReconocimientoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎓 Sistema de Reconocimiento Facial - Escuela")
        self.root.geometry("900x600")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.cap = None
        self.running = False
        self.ultimo_alumno = ""
        self.ultima_distancia = 0.0
        self.base_datos = None
        self.frame_actual = None
        
        # Colores
        self.color_verde = "#27ae60"
        self.color_rojo = "#e74c3c"
        self.color_fondo = "#f0f0f0"
        
        # Cargar clasificador de rostros de OpenCV
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Crear widgets
        self.crear_widgets()
        
        # Cargar base de datos
        self.cargar_base_datos()
        
        # Iniciar cámara
        self.iniciar_camara()
        
        # Actualizar ventana
        self.actualizar_video()
        self.actualizar_reloj()
        
    def crear_widgets(self):
        """Crea todos los elementos de la interfaz"""
        
        # === TÍTULO ===
        titulo = tk.Label(
            self.root, 
            text="🎓 SISTEMA DE RECONOCIMIENTO FACIAL",
            font=("Arial", 18, "bold"),
            bg=self.color_fondo,
            fg="#2c3e50"
        )
        titulo.pack(pady=10)
        
        # === FRAME PRINCIPAL (2 columnas) ===
        frame_principal = tk.Frame(self.root, bg=self.color_fondo)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # ---- Columna Izquierda: Video ----
        frame_video = tk.LabelFrame(
            frame_principal, 
            text="📹 Cámara en vivo",
            font=("Arial", 11, "bold"),
            bg=self.color_fondo
        )
        frame_video.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.label_video = tk.Label(
            frame_video, 
            text="Esperando cámara...",
            bg="#2c3e50",
            fg="white",
            font=("Arial", 14)
        )
        self.label_video.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # ---- Columna Derecha: Información ----
        frame_info = tk.LabelFrame(
            frame_principal,
            text="📊 Información",
            font=("Arial", 11, "bold"),
            bg=self.color_fondo
        )
        frame_info.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Último reconocido
        tk.Label(
            frame_info,
            text="👤 ÚLTIMO RECONOCIDO",
            font=("Arial", 10, "bold"),
            bg=self.color_fondo,
            fg="#2c3e50"
        ).pack(pady=(10, 5))
        
        self.label_nombre = tk.Label(
            frame_info,
            text="---",
            font=("Arial", 16, "bold"),
            bg=self.color_fondo,
            fg="#2c3e50"
        )
        self.label_nombre.pack()
        
        self.label_distancia = tk.Label(
            frame_info,
            text="Distancia: ---",
            font=("Arial", 10),
            bg=self.color_fondo,
            fg="#7f8c8d"
        )
        self.label_distancia.pack()
        
        self.label_estado = tk.Label(
            frame_info,
            text="⏳ Esperando captura",
            font=("Arial", 11, "bold"),
            bg=self.color_fondo,
            fg="#f39c12"
        )
        self.label_estado.pack(pady=5)
        
        # Separador
        ttk.Separator(frame_info, orient='horizontal').pack(fill=tk.X, padx=10, pady=10)
        
        # Registro de hoy
        tk.Label(
            frame_info,
            text="📋 REGISTRO DE INGRESOS (hoy)",
            font=("Arial", 10, "bold"),
            bg=self.color_fondo,
            fg="#2c3e50"
        ).pack(pady=(10, 5))
        
        self.texto_registro = scrolledtext.ScrolledText(
            frame_info,
            height=10,
            width=35,
            font=("Consolas", 9),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        self.texto_registro.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.texto_registro.config(state=tk.DISABLED)
        
        # Botón para recargar base de datos
        btn_recargar = tk.Button(
            frame_info,
            text="🔄 Recargar Alumnos",
            command=self.recargar_base_datos,
            font=("Arial", 9),
            bg="#3498db",
            fg="white",
            padx=10,
            pady=5,
            cursor="hand2"
        )
        btn_recargar.pack(pady=5)
        
        # === FRAME INFERIOR: Controles ===
        frame_controles = tk.Frame(self.root, bg=self.color_fondo)
        frame_controles.pack(fill=tk.X, padx=10, pady=10)
        
        # Botones
        btn_capturar = tk.Button(
            frame_controles,
            text="📸 CAPTURAR (Espacio)",
            command=self.capturar_rostro,
            font=("Arial", 10, "bold"),
            bg=self.color_verde,
            fg="white",
            padx=20,
            pady=8,
            cursor="hand2"
        )
        btn_capturar.pack(side=tk.LEFT, padx=5)
        
        btn_reiniciar = tk.Button(
            frame_controles,
            text="🔄 Reiniciar (R)",
            command=self.reiniciar_sistema,
            font=("Arial", 10),
            bg="#3498db",
            fg="white",
            padx=15,
            pady=8,
            cursor="hand2"
        )
        btn_reiniciar.pack(side=tk.LEFT, padx=5)
        
        btn_estado = tk.Button(
            frame_controles,
            text="ℹ️ Estado",
            command=self.mostrar_estado,
            font=("Arial", 10),
            bg="#95a5a6",
            fg="white",
            padx=15,
            pady=8,
            cursor="hand2"
        )
        btn_estado.pack(side=tk.LEFT, padx=5)
        
        btn_salir = tk.Button(
            frame_controles,
            text="❌ Salir (ESC)",
            command=self.salir,
            font=("Arial", 10, "bold"),
            bg=self.color_rojo,
            fg="white",
            padx=20,
            pady=8,
            cursor="hand2"
        )
        btn_salir.pack(side=tk.RIGHT, padx=5)
        
        # Estado del sistema
        self.label_sistema = tk.Label(
            frame_controles,
            text="🟢 Sistema activo",
            font=("Arial", 9),
            bg=self.color_fondo,
            fg=self.color_verde
        )
        self.label_sistema.pack(side=tk.LEFT, padx=20)
        
        # Atajos de teclado
        self.root.bind('<space>', lambda e: self.capturar_rostro())
        self.root.bind('<Escape>', lambda e: self.salir())
        self.root.bind('<r>', lambda e: self.reiniciar_sistema())
        self.root.bind('<R>', lambda e: self.reiniciar_sistema())
    
    # ============================================
    # FUNCIONES DEL SISTEMA
    # ============================================
    
    def cargar_base_datos(self):
        """Carga la base de datos usando db_manager"""
        try:
            self.base_datos = cargar_db()
            if self.base_datos:
                print(f"✅ Base de datos cargada: {len(self.base_datos)} alumnos")
                self.agregar_registro(f"✅ Sistema iniciado. {len(self.base_datos)} alumnos registrados.")
            else:
                self.base_datos = {}
                self.agregar_registro("⚠️ No se encontró base de datos. Ejecuta modulo_admin/registrar_alumnos.py")
        except Exception as e:
            print(f"❌ Error al cargar base de datos: {e}")
            self.base_datos = {}
            self.agregar_registro(f"❌ Error al cargar base de datos: {e}")
    
    def recargar_base_datos(self):
        """Recarga la base de datos (útil después de agregar alumnos)"""
        self.agregar_registro("🔄 Recargando base de datos...")
        self.cargar_base_datos()
        if self.base_datos:
            self.agregar_registro(f"✅ Base de datos recargada. {len(self.base_datos)} alumnos.")
        self.mostrar_estado()
    
    def iniciar_camara(self):
        """Inicia la cámara"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("No se pudo acceder a la cámara")
            self.running = True
            self.agregar_registro("📹 Cámara iniciada correctamente")
        except Exception as e:
            self.agregar_registro(f"❌ Error con cámara: {e}")
            self.label_video.config(text="❌ No se pudo acceder a la cámara")
    
    def verificar_camara_activa(self):
        """Verifica que la cámara esté enviando imagen válida"""
        if not self.running or self.cap is None:
            return False
        
        try:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                return False
            if np.mean(frame) < 5:
                return False
            return True
        except:
            return False
    
    def actualizar_video(self):
        """Actualiza el video en tiempo real"""
        if self.running and self.cap:
            try:
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    self.frame_actual = frame.copy()
                    frame_display = cv2.resize(frame, (640, 480))
                    frame_rgb = cv2.cvtColor(frame_display, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    img_tk = ImageTk.PhotoImage(image=img)
                    self.label_video.config(image=img_tk)
                    self.label_video.image = img_tk
                    
                    if self.label_sistema.cget('text') == "⚠️ Sin imagen":
                        self.label_sistema.config(text="🟢 Sistema activo", fg=self.color_verde)
            except Exception:
                pass
        
        self.root.after(30, self.actualizar_video)
    
    def actualizar_reloj(self):
        ahora = datetime.datetime.now().strftime("%H:%M:%S")
        self.root.title(f"🎓 Sistema de Reconocimiento Facial - Escuela ({ahora})")
        self.root.after(1000, self.actualizar_reloj)
    
    def detectar_rostro(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        caras = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(60, 60)
        )
        return len(caras) > 0, caras
    
    def capturar_rostro(self):
        """Captura y reconoce el rostro usando db_manager"""
        if not self.running or self.cap is None:
            self.agregar_registro("⚠️ Sistema no listo para capturar")
            return
        
        if self.base_datos is None or len(self.base_datos) == 0:
            self.agregar_registro("⚠️ No hay alumnos registrados en la base de datos")
            self.label_nombre.config(text="SIN ALUMNOS", fg=self.color_rojo)
            self.label_estado.config(text="⚠️ Base de datos vacía", fg=self.color_rojo)
            return
        
        if not self.verificar_camara_activa():
            self.agregar_registro("⚠️ Cámara sin imagen")
            self.label_nombre.config(text="ERROR CÁMARA", fg=self.color_rojo)
            self.label_distancia.config(text="---")
            self.label_estado.config(text="❌ Cámara no disponible", fg=self.color_rojo)
            self.label_sistema.config(text="⚠️ Sin imagen", fg=self.color_rojo)
            return
        
        self.agregar_registro("🔍 Capturando rostro...")
        self.label_estado.config(text="🔍 Reconociendo...", fg="#f39c12")
        
        try:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                self.agregar_registro("❌ Error al capturar imagen")
                return
            
            hay_rostro, caras = self.detectar_rostro(frame)
            if not hay_rostro:
                self.agregar_registro("⚠️ No se detectó ningún rostro")
                self.label_nombre.config(text="NO HAY ROSTRO", fg=self.color_rojo)
                self.label_distancia.config(text="---")
                self.label_estado.config(text="⚠️ Sin rostro detectado", fg=self.color_rojo)
                self.label_sistema.config(text="⚠️ Sin rostro", fg=self.color_rojo)
                return
            
            self.agregar_registro(f"✅ Rostro detectado ({len(caras)} cara(s))")
            cv2.imwrite(TEMP_IMG, frame)
            
            inicio = time.time()
            mejor_alumno, mejor_distancia = self.reconocer_rostro(TEMP_IMG)
            fin = time.time()
            
            if mejor_alumno and mejor_distancia < UMBRAL:
                self.ultimo_alumno = mejor_alumno
                self.ultima_distancia = mejor_distancia
                
                self.label_nombre.config(text=mejor_alumno.upper(), fg=self.color_verde)
                self.label_distancia.config(text=f"Distancia: {mejor_distancia:.4f}")
                self.label_estado.config(text="✅ ACCESO CONCEDIDO", fg=self.color_verde)
                self.label_sistema.config(text="✅ Acceso concedido", fg=self.color_verde)
                
                registrar_ingreso(mejor_alumno, "CONCEDIDO")
                self.agregar_registro(f"✅ {mejor_alumno} - ACCESO CONCEDIDO (dist: {mejor_distancia:.4f})")
                print(f"\n✅ {mejor_alumno} - ACCESO CONCEDIDO (dist: {mejor_distancia:.4f})")
                
            else:
                self.label_nombre.config(text="ACCESO DENEGADO", fg=self.color_rojo)
                self.label_distancia.config(
                    text=f"Distancia: {mejor_distancia:.4f}" if mejor_alumno else "No detectado"
                )
                self.label_estado.config(text="❌ ACCESO DENEGADO", fg=self.color_rojo)
                self.label_sistema.config(text="❌ Acceso denegado", fg=self.color_rojo)
                
                nombre = mejor_alumno if mejor_alumno else "DESCONOCIDO"
                registrar_ingreso(nombre, "DENEGADO")
                self.agregar_registro(f"❌ {nombre} - ACCESO DENEGADO")
                print(f"\n❌ {nombre} - ACCESO DENEGADO")
            
            if os.path.exists(TEMP_IMG):
                os.remove(TEMP_IMG)
                
        except Exception as e:
            self.agregar_registro(f"❌ Error: {e}")
            print(f"❌ Error: {e}")
            self.label_estado.config(text="❌ Error", fg=self.color_rojo)
    
    def reconocer_rostro(self, ruta_imagen):
        """Reconoce un rostro comparando con la base de datos"""
        if not self.base_datos:
            return None, float('inf')
        
        mejor_alumno = None
        mejor_distancia = float('inf')
        
        for alumno, datos in self.base_datos.items():
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
    
    def agregar_registro(self, mensaje):
        """Agrega un mensaje al registro visual"""
        self.texto_registro.config(state=tk.NORMAL)
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.texto_registro.insert(tk.END, f"[{timestamp}] {mensaje}\n")
        self.texto_registro.see(tk.END)
        self.texto_registro.config(state=tk.DISABLED)
    
    def mostrar_estado(self):
        """Muestra información del sistema"""
        info = f"""
📊 ESTADO DEL SISTEMA

📁 Base de datos: {'✅ Cargada' if self.base_datos else '❌ No disponible'}
👥 Alumnos registrados: {len(self.base_datos) if self.base_datos else 0}
📹 Cámara: {'✅ Activa' if self.running else '❌ Inactiva'}
📏 Umbral: {UMBRAL}
👤 Último reconocido: {self.ultimo_alumno if self.ultimo_alumno else 'Ninguno'}
📐 Última distancia: {self.ultima_distancia:.4f if self.ultima_distancia else '---'}
"""
        self.agregar_registro("📊 " + info.replace('\n', ' | '))
    
    def reiniciar_sistema(self):
        """Reinicia el sistema"""
        self.agregar_registro("🔄 Reiniciando sistema...")
        self.label_nombre.config(text="---", fg="#2c3e50")
        self.label_distancia.config(text="Distancia: ---")
        self.label_estado.config(text="⏳ Esperando captura", fg="#f39c12")
        self.label_sistema.config(text="🟢 Sistema activo", fg=self.color_verde)
        self.ultimo_alumno = ""
        self.ultima_distancia = 0.0
        self.cargar_base_datos()
    
    def salir(self):
        """Cierra el sistema correctamente"""
        self.agregar_registro("👋 Cerrando sistema...")
        self.running = False
        
        if self.cap:
            self.cap.release()
        
        cv2.destroyAllWindows()
        self.root.quit()
        self.root.destroy()
        sys.exit(0)

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    try:
        from PIL import Image, ImageTk
    except ImportError:
        print("❌ Necesitas instalar Pillow: pip install Pillow")
        sys.exit(1)
    
    root = tk.Tk()
    app = SistemaReconocimientoGUI(root)
    
    def on_closing():
        app.salir()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.salir()
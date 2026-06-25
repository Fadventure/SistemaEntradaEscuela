# gui_camara.py - Sistema de Reconocimiento Facial
# Versión 2.7 - Estilo Oscuro con Cámara Grande SIN EFECTO ESPEJO

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
# CONFIGURACIÓN DE CÁMARA
# ============================================

CAMARA_INDICE = 0  # 0 = integrada, 1 o 2 = USB externa

# ============================================
# CONFIGURACIÓN DE RUTAS
# ============================================

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
# COLORES - ESTILO OSCURO
# ============================================

COLORS = {
    # Fondo principal
    'fondo': '#0d1117',          # Fondo general (oscuro)
    'fondo_card': '#161b22',     # Fondo de tarjetas
    'fondo_input': '#0d1117',    # Fondo de inputs
    'borde': '#30363d',          # Bordes sutiles
    
    # Colores institucionales (adaptados a oscuro)
    'azul_oscuro': '#0a1628',    # Banner superior
    'azul_medio': '#1a3a6a',     # Botones principales
    'azul_claro': '#2d6da8',     # Hover de botones
    
    # Textos
    'texto': '#e6edf3',          # Texto principal (blanco)
    'texto_secundario': '#8b949e', # Texto secundario (gris)
    'texto_oscuro': '#0d1117',   # Texto sobre fondos claros
    
    # Estados
    'verde': '#2ea043',          # Acceso concedido
    'rojo': '#f85149',           # Acceso denegado
    'amarillo': '#d29922',       # Advertencias
    'azul_info': '#58a6ff',      # Información
    
    # Video
    'video_bg': '#000000',       # Fondo del video (negro)
}

# ============================================
# CLASE PRINCIPAL
# ============================================

class SistemaReconocimientoGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("E.E.S.T. N°2 - Sistema de Reconocimiento Facial")
        self.root.geometry("1100x680")
        self.root.configure(bg=COLORS['fondo'])
        self.root.minsize(1000, 600)
        
        # Variables
        self.cap = None
        self.running = False
        self.ultimo_alumno = ""
        self.ultima_distancia = 0.0
        self.base_datos = None
        self.frame_actual = None
        
        # Configurar grid principal
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=3)  # Video más grande
        self.root.grid_columnconfigure(1, weight=1)  # Panel derecho más pequeño
        
        # Cargar clasificador de rostros
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
    
    # ============================================
    # FUNCIONES DE UTILIDAD
    # ============================================

    def cargar_logo(self, tamaño=(50, 50)):
        """Carga el logo de la escuela desde la carpeta recursos"""
        try:
            from PIL import Image
            ruta_logo = os.path.join(RAIZ_PROYECTO, "recursos", "logo_escuela.png")
            
            if os.path.exists(ruta_logo):
                img = Image.open(ruta_logo)
                img = img.resize(tamaño, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
            else:
                print(f"⚠️ Logo no encontrado en: {ruta_logo}")
                return None
        except Exception as e:
            print(f"❌ Error al cargar logo: {e}")
            return None

    def crear_widgets(self):
        """Crea todos los elementos con estilo oscuro"""
        
        # ============================================
        # BANNER SUPERIOR
        # ============================================

        banner = tk.Frame(self.root, bg=COLORS['azul_oscuro'], height=65)
        banner.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        banner.grid_propagate(False)
        
        # Contenido del banner (centrado)
        frame_banner_content = tk.Frame(banner, bg=COLORS['azul_oscuro'])
        frame_banner_content.pack(expand=True)

        # --- LOGO (agregar esto) ---
        logo_img = self.cargar_logo((45, 45))  # Tamaño del logo
        if logo_img:
            label_logo = tk.Label(
                frame_banner_content,
                image=logo_img,
                bg=COLORS['azul_oscuro']
            )
            label_logo.image = logo_img  # Guardar referencia para que no se borre
            label_logo.pack(side=tk.LEFT, padx=5)
        
        # Título
        titulo = tk.Label(
            frame_banner_content,
            text="E.E.S.T. N°2 - Sistema de Reconocimiento Facial",
            font=("Segoe UI", 16, "bold"),
            bg=COLORS['azul_oscuro'],
            fg=COLORS['texto']
        )
        titulo.pack(side=tk.LEFT, padx=10)
        
        # Separador visual
        tk.Label(
            frame_banner_content,
            text="|",
            font=("Segoe UI", 14),
            bg=COLORS['azul_oscuro'],
            fg=COLORS['azul_claro']
        ).pack(side=tk.LEFT, padx=10)
        
        # Subtítulo
        subtitulo = tk.Label(
            frame_banner_content,
            text="Ing. Emilio Rebuelto - Berisso",
            font=("Segoe UI", 10),
            bg=COLORS['azul_oscuro'],
            fg=COLORS['texto_secundario']
        )
        subtitulo.pack(side=tk.LEFT)
        
        # ============================================
        # FRAME PRINCIPAL (2 columnas)
        # ============================================
        frame_principal = tk.Frame(self.root, bg=COLORS['fondo'])
        frame_principal.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
        frame_principal.grid_rowconfigure(0, weight=1)
        frame_principal.grid_columnconfigure(0, weight=3)  # Video más grande
        frame_principal.grid_columnconfigure(1, weight=1)  # Panel derecho
        
        # ---- Columna Izquierda: Video (MÁS GRANDE) ----
        frame_video = tk.Frame(
            frame_principal,
            bg=COLORS['fondo_card'],
            bd=1,
            relief=tk.FLAT
        )
        frame_video.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        frame_video.grid_rowconfigure(0, weight=1)
        frame_video.grid_columnconfigure(0, weight=1)
        
        # Título del video
        tk.Label(
            frame_video,
            text=" Cámara en vivo",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS['fondo_card'],
            fg=COLORS['texto'],
            padx=10,
            pady=5
        ).grid(row=0, column=0, sticky="w")
        
        # Label del video (ocupa el espacio principal)
        self.label_video = tk.Label(
            frame_video,
            text="🔄 Iniciando cámara...",
            bg=COLORS['video_bg'],
            fg=COLORS['texto_secundario'],
            font=("Segoe UI", 16)
        )
        self.label_video.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.label_video.grid_rowconfigure(0, weight=1)
        self.label_video.grid_columnconfigure(0, weight=1)
        
        # Configurar el frame_video para que el label de video se expanda
        frame_video.grid_rowconfigure(1, weight=1)
        frame_video.grid_columnconfigure(0, weight=1)
        
        # ---- Columna Derecha: Información ----
        frame_info = tk.Frame(
            frame_principal,
            bg=COLORS['fondo_card'],
            bd=1,
            relief=tk.FLAT
        )
        frame_info.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        frame_info.grid_rowconfigure(0, weight=0)  # Título
        frame_info.grid_rowconfigure(1, weight=0)  # Último reconocido
        frame_info.grid_rowconfigure(2, weight=0)  # Separador
        frame_info.grid_rowconfigure(3, weight=1)  # Registro (expande)
        frame_info.grid_rowconfigure(4, weight=0)  # Botón recargar
        frame_info.grid_columnconfigure(0, weight=1)
        
        # Título del panel
        tk.Label(
            frame_info,
            text="📊 INFORMACIÓN",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS['fondo_card'],
            fg=COLORS['texto'],
            padx=10,
            pady=5
        ).grid(row=0, column=0, sticky="w")
        
        # ---- Último reconocido ----
        frame_reconocido = tk.Frame(frame_info, bg=COLORS['fondo_card'])
        frame_reconocido.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        tk.Label(
            frame_reconocido,
            text="👤 ÚLTIMO RECONOCIDO",
            font=("Segoe UI", 9, "bold"),
            bg=COLORS['fondo_card'],
            fg=COLORS['texto_secundario']
        ).pack(anchor="w")
        
        self.label_nombre = tk.Label(
            frame_reconocido,
            text="---",
            font=("Segoe UI", 20, "bold"),
            bg=COLORS['fondo_card'],
            fg=COLORS['texto']
        )
        self.label_nombre.pack(anchor="w", pady=(2, 0))
        
        self.label_distancia = tk.Label(
            frame_reconocido,
            text="Distancia: ---",
            font=("Segoe UI", 10),
            bg=COLORS['fondo_card'],
            fg=COLORS['texto_secundario']
        )
        self.label_distancia.pack(anchor="w")
        
        self.label_estado = tk.Label(
            frame_reconocido,
            text="⏳ Esperando captura",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS['fondo_card'],
            fg=COLORS['amarillo']
        )
        self.label_estado.pack(anchor="w", pady=(5, 0))
        
        # ---- Separador ----
        separador = tk.Frame(frame_info, bg=COLORS['borde'], height=1)
        separador.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        
        # ---- Registro de hoy ----
        tk.Label(
            frame_info,
            text="📋 REGISTRO DE INGRESOS",
            font=("Segoe UI", 9, "bold"),
            bg=COLORS['fondo_card'],
            fg=COLORS['texto_secundario']
        ).grid(row=3, column=0, sticky="w", padx=10, pady=(0, 5))
        
        self.texto_registro = scrolledtext.ScrolledText(
            frame_info,
            font=("Consolas", 9),
            bg=COLORS['fondo_input'],
            fg=COLORS['texto'],
            insertbackground=COLORS['texto'],
            relief=tk.FLAT,
            bd=1,
            highlightbackground=COLORS['borde'],
            highlightcolor=COLORS['azul_claro'],
            highlightthickness=1
        )
        self.texto_registro.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 5))
        self.texto_registro.config(state=tk.DISABLED)
        
        # ---- Botón recargar ----
        btn_recargar = tk.Button(
            frame_info,
            text=" Recargar Alumnos",
            command=self.recargar_base_datos,
            font=("Segoe UI", 9, "bold"),
            bg=COLORS['azul_medio'],
            fg=COLORS['texto'],
            activebackground=COLORS['azul_claro'],
            activeforeground=COLORS['texto'],
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
            pady=5
        )
        btn_recargar.grid(row=4, column=0, pady=10, padx=10, sticky="ew")
        
        # ============================================
        # FRAME INFERIOR: Controles
        # ============================================
        frame_controles = tk.Frame(self.root, bg=COLORS['fondo'])
        frame_controles.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        # Botón Capturar (Verde)
        btn_capturar = tk.Button(
            frame_controles,
            text=" CAPTURAR (Espacio)",
            command=self.capturar_rostro,
            font=("Segoe UI", 10, "bold"),
            bg=COLORS['verde'],
            fg=COLORS['texto_oscuro'],
            activebackground="#3fb950",
            activeforeground=COLORS['texto_oscuro'],
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8
        )
        btn_capturar.pack(side=tk.LEFT, padx=5)
        
        # Botón Reiniciar
        btn_reiniciar = tk.Button(
            frame_controles,
            text="🔄 Reiniciar (R)",
            command=self.reiniciar_sistema,
            font=("Segoe UI", 10),
            bg=COLORS['azul_medio'],
            fg=COLORS['texto'],
            activebackground=COLORS['azul_claro'],
            activeforeground=COLORS['texto'],
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=8
        )
        btn_reiniciar.pack(side=tk.LEFT, padx=5)
        
        # Botón Estado
        btn_estado = tk.Button(
            frame_controles,
            text="ℹ️ Estado",
            command=self.mostrar_estado,
            font=("Segoe UI", 10),
            bg=COLORS['fondo_card'],
            fg=COLORS['texto_secundario'],
            activebackground=COLORS['borde'],
            activeforeground=COLORS['texto'],
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=8
        )
        btn_estado.pack(side=tk.LEFT, padx=5)
        
        # Estado del sistema (a la derecha)
        self.label_sistema = tk.Label(
            frame_controles,
            text="🟢 Sistema activo",
            font=("Segoe UI", 10),
            bg=COLORS['fondo'],
            fg=COLORS['verde']
        )
        self.label_sistema.pack(side=tk.RIGHT, padx=10)
        
        # Botón Salir (Rojo, a la derecha)
        btn_salir = tk.Button(
            frame_controles,
            text="❌ Salir (ESC)",
            command=self.salir,
            font=("Segoe UI", 10, "bold"),
            bg=COLORS['rojo'],
            fg=COLORS['texto'],
            activebackground="#da3633",
            activeforeground=COLORS['texto'],
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8
        )
        btn_salir.pack(side=tk.RIGHT, padx=5)
        
        # Atajos de teclado
        self.root.bind('<space>', lambda e: self.capturar_rostro())
        self.root.bind('<Escape>', lambda e: self.salir())
        self.root.bind('<r>', lambda e: self.reiniciar_sistema())
        self.root.bind('<R>', lambda e: self.reiniciar_sistema())
    
    # ============================================
    # FUNCIONES DEL SISTEMA
    # ============================================
    
    def cargar_base_datos(self):
        try:
            self.base_datos = cargar_db()
            if self.base_datos:
                print(f"✅ Base de datos cargada: {len(self.base_datos)} alumnos")
                self.agregar_registro(f"✅ Sistema iniciado. {len(self.base_datos)} alumnos registrados.")
            else:
                self.base_datos = {}
                self.agregar_registro("⚠️ No se encontró base de datos.")
        except Exception as e:
            print(f"❌ Error: {e}")
            self.base_datos = {}
    
    def recargar_base_datos(self):
        self.agregar_registro("🔄 Recargando base de datos...")
        self.cargar_base_datos()
        if self.base_datos:
            self.agregar_registro(f"✅ Recargada. {len(self.base_datos)} alumnos.")
        self.mostrar_estado()
    
    def iniciar_camara(self):
        try:
            self.cap = cv2.VideoCapture(CAMARA_INDICE)
            if not self.cap.isOpened():
                raise Exception(f"No se pudo acceder a la cámara {CAMARA_INDICE}")
            self.running = True
            self.agregar_registro(f" Cámara {CAMARA_INDICE} iniciada")
        except Exception as e:
            self.agregar_registro(f"❌ Error: {e}")
            self.label_video.config(text="❌ No se pudo acceder a la cámara")
    
    def verificar_camara_activa(self):
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
        """Actualiza el video en tiempo real - SIN EFECTO ESPEJO"""
        if self.running and self.cap:
            try:
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    self.frame_actual = frame.copy()
                    # Redimensionar manteniendo proporción
                    h, w = frame.shape[:2]
                    aspect_ratio = w / h
                    new_w = 800
                    new_h = int(new_w / aspect_ratio)
                    
                    # === CAMBIO IMPORTANTE ===
                    # Mostrar la imagen NATURAL (sin efecto espejo)
                    # Si quieres efecto espejo, usa cv2.flip(frame, 1)
                    frame_display = cv2.resize(frame, (new_w, new_h))
                    # ===========================
                    
                    frame_rgb = cv2.cvtColor(frame_display, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    img_tk = ImageTk.PhotoImage(image=img)
                    self.label_video.config(image=img_tk)
                    self.label_video.image = img_tk
            except Exception:
                pass
        self.root.after(30, self.actualizar_video)
    
    def actualizar_reloj(self):
        ahora = datetime.datetime.now().strftime("%H:%M:%S")
        self.root.title(f"E.E.S.T. N°2 - Sistema de Reconocimiento Facial ({ahora})")
        self.root.after(1000, self.actualizar_reloj)
    
    def detectar_rostro(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        caras = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))
        return len(caras) > 0, caras
    
    def capturar_rostro(self):
        if not self.running or self.cap is None or self.base_datos is None:
            self.agregar_registro("⚠️ Sistema no listo")
            return
        
        if not self.verificar_camara_activa():
            self.agregar_registro("⚠️ Cámara sin imagen")
            self.label_nombre.config(text="ERROR CÁMARA", fg=COLORS['rojo'])
            self.label_estado.config(text="❌ Cámara no disponible", fg=COLORS['rojo'])
            return
        
        self.agregar_registro("🔍 Capturando...")
        self.label_estado.config(text="🔍 Reconociendo...", fg=COLORS['amarillo'])
        
        try:
            ret, frame = self.cap.read()
            if not ret:
                self.agregar_registro("❌ Error al capturar")
                return
            
            hay_rostro, caras = self.detectar_rostro(frame)
            if not hay_rostro:
                self.agregar_registro("⚠️ No se detectó rostro")
                self.label_nombre.config(text="NO HAY ROSTRO", fg=COLORS['rojo'])
                self.label_estado.config(text="⚠️ Sin rostro", fg=COLORS['rojo'])
                return
            
            cv2.imwrite(TEMP_IMG, frame)
            
            mejor_alumno, mejor_distancia = self.reconocer_rostro(TEMP_IMG)
            
            if mejor_alumno and mejor_distancia < UMBRAL:
                self.ultimo_alumno = mejor_alumno
                self.ultima_distancia = mejor_distancia
                
                self.label_nombre.config(text=mejor_alumno.upper(), fg=COLORS['verde'])
                self.label_distancia.config(text=f"Distancia: {mejor_distancia:.4f}")
                self.label_estado.config(text="✅ ACCESO CONCEDIDO", fg=COLORS['verde'])
                self.label_sistema.config(text="✅ Acceso concedido", fg=COLORS['verde'])
                
                registrar_ingreso(mejor_alumno, "CONCEDIDO")
                self.agregar_registro(f"✅ {mejor_alumno} - ACCESO CONCEDIDO (dist: {mejor_distancia:.4f})")
                print(f"\n✅ {mejor_alumno} - ACCESO CONCEDIDO (dist: {mejor_distancia:.4f})")
            else:
                self.label_nombre.config(text="ACCESO DENEGADO", fg=COLORS['rojo'])
                self.label_distancia.config(text=f"Distancia: {mejor_distancia:.4f}" if mejor_alumno else "No detectado")
                self.label_estado.config(text="❌ ACCESO DENEGADO", fg=COLORS['rojo'])
                self.label_sistema.config(text="❌ Acceso denegado", fg=COLORS['rojo'])
                
                nombre = mejor_alumno if mejor_alumno else "DESCONOCIDO"
                registrar_ingreso(nombre, "DENEGADO")
                self.agregar_registro(f"❌ {nombre} - ACCESO DENEGADO")
                print(f"\n❌ {nombre} - ACCESO DENEGADO")
            
            if os.path.exists(TEMP_IMG):
                os.remove(TEMP_IMG)
                
        except Exception as e:
            self.agregar_registro(f"❌ Error: {e}")
            print(f"❌ Error: {e}")
    
    def reconocer_rostro(self, ruta_imagen):
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
        self.texto_registro.config(state=tk.NORMAL)
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.texto_registro.insert(tk.END, f"[{timestamp}] {mensaje}\n")
        self.texto_registro.see(tk.END)
        self.texto_registro.config(state=tk.DISABLED)
    
    def mostrar_estado(self):
        info = f"""
📊 ESTADO DEL SISTEMA

📁 Base de datos: {'✅ Cargada' if self.base_datos else '❌ No disponible'}
👥 Alumnos: {len(self.base_datos) if self.base_datos else 0}
📹 Cámara: {'✅ Activa' if self.running else '❌ Inactiva'}
📏 Umbral: {UMBRAL}
👤 Último: {self.ultimo_alumno if self.ultimo_alumno else 'Ninguno'}
"""
        self.agregar_registro("📊 " + info.replace('\n', ' | '))
    
    def reiniciar_sistema(self):
        self.agregar_registro("🔄 Reiniciando...")
        self.label_nombre.config(text="---", fg=COLORS['texto'])
        self.label_distancia.config(text="Distancia: ---")
        self.label_estado.config(text="⏳ Esperando captura", fg=COLORS['amarillo'])
        self.label_sistema.config(text="🟢 Sistema activo", fg=COLORS['verde'])
        self.ultimo_alumno = ""
        self.ultima_distancia = 0.0
        self.cargar_base_datos()
    
    def salir(self):
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
    
    print("=" * 50)
    print("🏫 E.E.S.T. N°2 - Sistema de Reconocimiento Facial")
    print("   Ing. Emilio Rebuelto - Berisso")
    print("=" * 50)
    
    root = tk.Tk()
    app = SistemaReconocimientoGUI(root)
    
    def on_closing():
        app.salir()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.salir()
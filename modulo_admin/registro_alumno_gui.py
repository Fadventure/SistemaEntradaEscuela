# registro_alumno_gui.py - Registro de Alumnos con Cámara
# Versión 2.0 - Estilo Oscuro

import os
import sys
import cv2
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

# ============================================
# CONFIGURACIÓN DE RUTAS
# ============================================

RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ_PROYECTO)

from deepface import DeepFace
from base_datos.db_manager import cargar_db, guardar_db

# ============================================
# CONFIGURACIÓN
# ============================================

CARPETA_ALUMNOS = "rostros/alumnos_registrados"

# ============================================
# COLORES - ESTILO OSCURO
# ============================================

COLORS = {
    'fondo': '#0d1117',
    'fondo_card': '#161b22',
    'fondo_input': '#0d1117',
    'borde': '#30363d',
    'azul_oscuro': '#0a1628',
    'azul_medio': '#1a3a6a',
    'azul_claro': '#2d6da8',
    'texto': '#e6edf3',
    'texto_secundario': '#8b949e',
    'texto_oscuro': '#0d1117',
    'verde': '#2ea043',
    'rojo': '#f85149',
    'amarillo': '#d29922',
    'azul_info': '#58a6ff',
    'video_bg': '#000000',
}

# ============================================
# CLASE PRINCIPAL
# ============================================

class RegistroAlumnoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📝 Registrar Alumno - E.E.S.T. N°2")
        self.root.geometry("900x650")
        self.root.configure(bg=COLORS['fondo'])
        self.root.minsize(800, 550)
        
        # Variables
        self.cap = None
        self.running = False
        self.frame_actual = None
        self.foto_tomada = None
        self.ruta_foto = None
        
        # Configurar grid principal
        self.root.grid_rowconfigure(0, weight=0)  # Banner
        self.root.grid_rowconfigure(1, weight=1)  # Contenido
        self.root.grid_columnconfigure(0, weight=1)
        
        # Crear widgets
        self.crear_widgets()
        
        # Iniciar cámara
        self.iniciar_camara()
        
        # Actualizar video
        self.actualizar_video()
    
    def crear_widgets(self):
        """Crea todos los elementos con estilo oscuro"""
        
        # ============================================
        # BANNER SUPERIOR
        # ============================================
        banner = tk.Frame(self.root, bg=COLORS['azul_oscuro'], height=60)
        banner.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        banner.grid_propagate(False)
        
        frame_banner = tk.Frame(banner, bg=COLORS['azul_oscuro'])
        frame_banner.pack(expand=True)
        
        tk.Label(
            frame_banner,
            text="📝 Registrar Nuevo Alumno",
            font=("Segoe UI", 16, "bold"),
            bg=COLORS['azul_oscuro'],
            fg=COLORS['texto']
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Label(
            frame_banner,
            text="|",
            font=("Segoe UI", 14),
            bg=COLORS['azul_oscuro'],
            fg=COLORS['azul_claro']
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Label(
            frame_banner,
            text="E.E.S.T. N°2 - Ing. Emilio Rebuelto",
            font=("Segoe UI", 10),
            bg=COLORS['azul_oscuro'],
            fg=COLORS['texto_secundario']
        ).pack(side=tk.LEFT)
        
        # ============================================
        # FRAME PRINCIPAL (2 columnas)
        # ============================================
        frame_principal = tk.Frame(self.root, bg=COLORS['fondo'])
        frame_principal.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        frame_principal.grid_rowconfigure(0, weight=1)
        frame_principal.grid_columnconfigure(0, weight=2)  # Video más grande
        frame_principal.grid_columnconfigure(1, weight=1)  # Datos
        
        # ---- Columna Izquierda: Video ----
        frame_video = tk.Frame(
            frame_principal,
            bg=COLORS['fondo_card'],
            bd=1,
            relief=tk.FLAT
        )
        frame_video.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        frame_video.grid_rowconfigure(1, weight=1)
        frame_video.grid_columnconfigure(0, weight=1)
        
        tk.Label(
            frame_video,
            text="📹 Capturar Foto",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS['fondo_card'],
            fg=COLORS['texto'],
            padx=10,
            pady=5
        ).grid(row=0, column=0, sticky="w")
        
        self.label_video = tk.Label(
            frame_video,
            text="🔄 Iniciando cámara...",
            bg=COLORS['video_bg'],
            fg=COLORS['texto_secundario'],
            font=("Segoe UI", 14)
        )
        self.label_video.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        
        # ---- Columna Derecha: Datos ----
        frame_datos = tk.Frame(
            frame_principal,
            bg=COLORS['fondo_card'],
            bd=1,
            relief=tk.FLAT
        )
        frame_datos.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        frame_datos.grid_rowconfigure(0, weight=0)
        frame_datos.grid_rowconfigure(1, weight=0)
        frame_datos.grid_rowconfigure(2, weight=0)
        frame_datos.grid_rowconfigure(3, weight=0)
        frame_datos.grid_rowconfigure(4, weight=0)
        frame_datos.grid_rowconfigure(5, weight=1)  # Foto tomada (expande)
        frame_datos.grid_rowconfigure(6, weight=0)
        frame_datos.grid_columnconfigure(0, weight=1)
        
        # Título
        tk.Label(
            frame_datos,
            text="📋 DATOS DEL ALUMNO",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS['fondo_card'],
            fg=COLORS['texto'],
            padx=10,
            pady=5
        ).grid(row=0, column=0, sticky="w")
        
        # Nombre
        tk.Label(
            frame_datos,
            text="👤 Nombre:",
            font=("Segoe UI", 10),
            bg=COLORS['fondo_card'],
            fg=COLORS['texto_secundario']
        ).grid(row=1, column=0, sticky="w", padx=10, pady=(10, 2))
        
        self.entry_nombre = tk.Entry(
            frame_datos,
            font=("Segoe UI", 12),
            bg=COLORS['fondo_input'],
            fg=COLORS['texto'],
            insertbackground=COLORS['texto'],
            relief=tk.FLAT,
            bd=1,
            highlightbackground=COLORS['borde'],
            highlightcolor=COLORS['azul_claro'],
            highlightthickness=1
        )
        self.entry_nombre.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 5))
        
        # Curso
        tk.Label(
            frame_datos,
            text="📚 Curso:",
            font=("Segoe UI", 10),
            bg=COLORS['fondo_card'],
            fg=COLORS['texto_secundario']
        ).grid(row=3, column=0, sticky="w", padx=10, pady=(10, 2))
        
        self.entry_curso = tk.Entry(
            frame_datos,
            font=("Segoe UI", 12),
            bg=COLORS['fondo_input'],
            fg=COLORS['texto'],
            insertbackground=COLORS['texto'],
            relief=tk.FLAT,
            bd=1,
            highlightbackground=COLORS['borde'],
            highlightcolor=COLORS['azul_claro'],
            highlightthickness=1
        )
        self.entry_curso.grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 5))
        self.entry_curso.insert(0, "4°A")
        
        # Foto tomada (previsualización)
        tk.Label(
            frame_datos,
            text="📸 Foto tomada:",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS['fondo_card'],
            fg=COLORS['texto_secundario']
        ).grid(row=5, column=0, sticky="w", padx=10, pady=(10, 2))
        
        self.label_foto_tomada = tk.Label(
            frame_datos,
            text="(Sin foto)",
            bg=COLORS['fondo_input'],
            fg=COLORS['texto_secundario'],
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            bd=1,
            highlightbackground=COLORS['borde'],
            highlightthickness=1
        )
        self.label_foto_tomada.grid(row=5, column=0, sticky="nsew", padx=10, pady=(0, 5))
        
        # Botones
        frame_botones = tk.Frame(frame_datos, bg=COLORS['fondo_card'])
        frame_botones.grid(row=6, column=0, sticky="ew", padx=10, pady=10)
        
        btn_capturar = tk.Button(
            frame_botones,
            text="📸 Tomar Foto",
            command=self.tomar_foto,
            font=("Segoe UI", 10, "bold"),
            bg=COLORS['verde'],
            fg=COLORS['texto_oscuro'],
            activebackground="#3fb950",
            activeforeground=COLORS['texto_oscuro'],
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=8
        )
        btn_capturar.pack(side=tk.LEFT, padx=5)
        
        btn_registrar = tk.Button(
            frame_botones,
            text="💾 Registrar Alumno",
            command=self.registrar_alumno,
            font=("Segoe UI", 10, "bold"),
            bg=COLORS['azul_medio'],
            fg=COLORS['texto'],
            activebackground=COLORS['azul_claro'],
            activeforeground=COLORS['texto'],
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=8
        )
        btn_registrar.pack(side=tk.LEFT, padx=5)
        
        btn_salir = tk.Button(
            frame_botones,
            text="❌ Salir",
            command=self.salir,
            font=("Segoe UI", 10, "bold"),
            bg=COLORS['rojo'],
            fg=COLORS['texto'],
            activebackground="#da3633",
            activeforeground=COLORS['texto'],
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=8
        )
        btn_salir.pack(side=tk.RIGHT, padx=5)
        
        # Estado
        self.label_estado = tk.Label(
            frame_datos,
            text="✅ Listo para registrar",
            font=("Segoe UI", 9),
            bg=COLORS['fondo_card'],
            fg=COLORS['verde']
        )
        self.label_estado.grid(row=7, column=0, sticky="w", padx=10, pady=(0, 5))
    
    # ============================================
    # FUNCIONES DEL SISTEMA
    # ============================================
    
    def iniciar_camara(self):
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("No se pudo acceder a la cámara")
            self.running = True
            self.label_estado.config(text="✅ Cámara iniciada", fg=COLORS['verde'])
        except Exception as e:
            self.label_estado.config(text=f"❌ Error: {e}", fg=COLORS['rojo'])
    
    def actualizar_video(self):
        if self.running and self.cap:
            try:
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    self.frame_actual = frame.copy()
                    h, w = frame.shape[:2]
                    aspect = w / h
                    new_w = 500
                    new_h = int(new_w / aspect)
                    frame_display = cv2.resize(frame, (new_w, new_h))
                    frame_rgb = cv2.cvtColor(frame_display, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    img_tk = ImageTk.PhotoImage(image=img)
                    self.label_video.config(image=img_tk)
                    self.label_video.image = img_tk
            except Exception:
                pass
        self.root.after(30, self.actualizar_video)
    
    def tomar_foto(self):
        if self.frame_actual is None:
            messagebox.showwarning("⚠️", "No hay imagen de la cámara")
            return
        
        self.foto_tomada = self.frame_actual.copy()
        
        # Mostrar en el label
        img_rgb = cv2.cvtColor(self.foto_tomada, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img_rgb)
        img = img.resize((200, 150), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(image=img)
        self.label_foto_tomada.config(image=img_tk)
        self.label_foto_tomada.image = img_tk
        
        self.label_estado.config(text="📸 Foto tomada, completa los datos", fg=COLORS['amarillo'])
    
    def registrar_alumno(self):
        nombre = self.entry_nombre.get().strip().lower()
        curso = self.entry_curso.get().strip()
        
        if not nombre:
            messagebox.showwarning("⚠️", "Ingresa el nombre del alumno")
            return
        
        if not curso:
            messagebox.showwarning("⚠️", "Ingresa el curso del alumno")
            return
        
        if self.foto_tomada is None:
            messagebox.showwarning("⚠️", "Toma una foto del alumno primero")
            return
        
        try:
            carpeta_alumno = os.path.join(CARPETA_ALUMNOS, nombre)
            os.makedirs(carpeta_alumno, exist_ok=True)
            
            ruta_foto = os.path.join(carpeta_alumno, f"{nombre}_1.png")
            cv2.imwrite(ruta_foto, self.foto_tomada)
            
            self.label_estado.config(text="🔄 Generando embedding...", fg=COLORS['amarillo'])
            self.root.update()
            
            embedding = DeepFace.represent(
                img_path=ruta_foto,
                model_name='ArcFace',
                enforce_detection=False
            )[0]['embedding']
            
            db = cargar_db()
            db[nombre] = {
                'embedding': embedding,
                'imagen_referencia': ruta_foto,
                'fecha_registro': datetime.datetime.now().strftime("%Y-%m-%d"),
                'curso': curso,
                'nombre_completo': nombre.title()
            }
            guardar_db(db)
            
            self.entry_nombre.delete(0, tk.END)
            self.foto_tomada = None
            self.label_foto_tomada.config(image='', text="(Sin foto)")
            self.label_foto_tomada.image = None
            
            messagebox.showinfo(
                "✅ Éxito",
                f"Alumno '{nombre.title()}' registrado correctamente\n"
                f"Curso: {curso}\n"
                f"Foto guardada en: {ruta_foto}"
            )
            
            self.label_estado.config(text=f"✅ Alumno '{nombre.title()}' registrado", fg=COLORS['verde'])
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al registrar:\n{e}")
            self.label_estado.config(text=f"❌ Error: {e}", fg=COLORS['rojo'])
    
    def salir(self):
        self.running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        self.root.quit()
        self.root.destroy()

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    root = tk.Tk()
    app = RegistroAlumnoGUI(root)
    root.mainloop()
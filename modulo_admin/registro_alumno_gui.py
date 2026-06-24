# modulo_admin/registro_alumno_gui.py
# Interfaz para que los maestros registren alumnos

import os
import sys
import cv2
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

# Configurar rutas
RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ_PROYECTO)

from deepface import DeepFace
from base_datos.db_manager import cargar_db, guardar_db

# ============================================
# CONFIGURACIÓN
# ============================================

CARPETA_ALUMNOS = "rostros/alumnos_registrados"

# ============================================
# CLASE PRINCIPAL
# ============================================

class RegistroAlumnoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📝 Registrar Alumno - Sistema de Reconocimiento")
        self.root.geometry("700x550")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.cap = None
        self.running = False
        self.frame_actual = None
        self.foto_tomada = None
        self.ruta_foto = None
        
        # Crear widgets
        self.crear_widgets()
        
        # Iniciar cámara
        self.iniciar_camara()
        
        # Actualizar video
        self.actualizar_video()
    
    def crear_widgets(self):
        """Crea todos los elementos de la interfaz"""
        
        # Título
        titulo = tk.Label(
            self.root,
            text="📝 REGISTRO DE NUEVO ALUMNO",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        titulo.pack(pady=10)
        
        # Frame principal (2 columnas)
        frame_principal = tk.Frame(self.root, bg="#f0f0f0")
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # ---- Columna Izquierda: Video ----
        frame_video = tk.LabelFrame(
            frame_principal,
            text="📹 Capturar Foto",
            font=("Arial", 10, "bold"),
            bg="#f0f0f0"
        )
        frame_video.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.label_video = tk.Label(
            frame_video,
            text="Esperando cámara...",
            bg="#2c3e50",
            fg="white",
            font=("Arial", 12)
        )
        self.label_video.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Botón capturar
        btn_capturar = tk.Button(
            frame_video,
            text="📸 Tomar Foto",
            command=self.tomar_foto,
            font=("Arial", 10, "bold"),
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=8,
            cursor="hand2"
        )
        btn_capturar.pack(pady=10)
        
        # ---- Columna Derecha: Datos ----
        frame_datos = tk.LabelFrame(
            frame_principal,
            text="📋 Datos del Alumno",
            font=("Arial", 10, "bold"),
            bg="#f0f0f0"
        )
        frame_datos.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Nombre
        tk.Label(
            frame_datos,
            text="👤 Nombre:",
            font=("Arial", 10),
            bg="#f0f0f0"
        ).pack(anchor=tk.W, padx=10, pady=(10, 2))
        
        self.entry_nombre = tk.Entry(
            frame_datos,
            font=("Arial", 12),
            width=25
        )
        self.entry_nombre.pack(padx=10, pady=5)
        
        # Curso
        tk.Label(
            frame_datos,
            text="📚 Curso:",
            font=("Arial", 10),
            bg="#f0f0f0"
        ).pack(anchor=tk.W, padx=10, pady=(10, 2))
        
        self.entry_curso = tk.Entry(
            frame_datos,
            font=("Arial", 12),
            width=25
        )
        self.entry_curso.pack(padx=10, pady=5)
        self.entry_curso.insert(0, "4°A")  # Valor por defecto
        
        # Espacio
        tk.Label(frame_datos, text="", bg="#f0f0f0").pack(pady=5)
        
        # Previsualización de la foto tomada
        tk.Label(
            frame_datos,
            text="📸 Foto tomada:",
            font=("Arial", 10, "bold"),
            bg="#f0f0f0"
        ).pack(anchor=tk.W, padx=10)
        
        self.label_foto_tomada = tk.Label(
            frame_datos,
            text="(Sin foto)",
            bg="#ecf0f1",
            width=30,
            height=8,
            relief=tk.SUNKEN
        )
        self.label_foto_tomada.pack(padx=10, pady=5)
        
        # Botón registrar
        btn_registrar = tk.Button(
            frame_datos,
            text="💾 Registrar Alumno",
            command=self.registrar_alumno,
            font=("Arial", 10, "bold"),
            bg="#3498db",
            fg="white",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        btn_registrar.pack(pady=10)
        
        # Estado
        self.label_estado = tk.Label(
            frame_datos,
            text="✅ Listo para registrar",
            font=("Arial", 9),
            bg="#f0f0f0",
            fg="#27ae60"
        )
        self.label_estado.pack(pady=5)
    
    def iniciar_camara(self):
        """Inicia la cámara"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("No se pudo acceder a la cámara")
            self.running = True
            self.label_estado.config(text="✅ Cámara iniciada", fg="#27ae60")
        except Exception as e:
            self.label_estado.config(text=f"❌ Error: {e}", fg="#e74c3c")
    
    def actualizar_video(self):
        """Actualiza el video en tiempo real"""
        if self.running and self.cap:
            try:
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    self.frame_actual = frame.copy()
                    frame_display = cv2.resize(frame, (400, 300))
                    frame_rgb = cv2.cvtColor(frame_display, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    img_tk = ImageTk.PhotoImage(image=img)
                    self.label_video.config(image=img_tk)
                    self.label_video.image = img_tk
            except Exception:
                pass
        
        self.root.after(30, self.actualizar_video)
    
    def tomar_foto(self):
        """Toma una foto de la cámara"""
        if self.frame_actual is None:
            messagebox.showwarning("⚠️", "No hay imagen de la cámara")
            return
        
        # Guardar la foto
        self.foto_tomada = self.frame_actual.copy()
        
        # Mostrar en el label
        img_rgb = cv2.cvtColor(self.foto_tomada, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img_rgb)
        img = img.resize((200, 150), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(image=img)
        self.label_foto_tomada.config(image=img_tk)
        self.label_foto_tomada.image = img_tk
        
        self.label_estado.config(text="📸 Foto tomada, completa los datos", fg="#f39c12")
    
    def registrar_alumno(self):
        """Registra al alumno en la base de datos"""
        nombre = self.entry_nombre.get().strip().lower()
        curso = self.entry_curso.get().strip()
        
        # Validaciones
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
            # Guardar foto en la carpeta del alumno
            carpeta_alumno = os.path.join(CARPETA_ALUMNOS, nombre)
            os.makedirs(carpeta_alumno, exist_ok=True)
            
            # Nombre del archivo: nombre_1.png
            ruta_foto = os.path.join(carpeta_alumno, f"{nombre}_1.png")
            cv2.imwrite(ruta_foto, self.foto_tomada)
            
            # Generar embedding
            self.label_estado.config(text="🔄 Generando embedding...", fg="#f39c12")
            self.root.update()
            
            embedding = DeepFace.represent(
                img_path=ruta_foto,
                model_name='ArcFace',
                enforce_detection=False
            )[0]['embedding']
            
            # Guardar en la base de datos
            db = cargar_db()
            
            db[nombre] = {
                'embedding': embedding,
                'imagen_referencia': ruta_foto,
                'fecha_registro': datetime.datetime.now().strftime("%Y-%m-%d"),
                'curso': curso,
                'nombre_completo': nombre.title()
            }
            
            guardar_db(db)
            
            # Limpiar campos
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
            
            self.label_estado.config(text=f"✅ Alumno '{nombre.title()}' registrado", fg="#27ae60")
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al registrar:\n{e}")
            self.label_estado.config(text=f"❌ Error: {e}", fg="#e74c3c")
    
    def salir(self):
        """Cierra la aplicación"""
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
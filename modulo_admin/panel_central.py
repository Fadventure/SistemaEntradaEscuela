# panel_central.py - Panel de Administración Unificado
# Versión 3.2 - Cámara Grande SIN EFECTO ESPEJO

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
from base_datos.db_manager import cargar_db, guardar_db, listar_alumnos, eliminar_alumno

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
# CLASE PRINCIPAL - PANEL CENTRAL
# ============================================

class PanelCentral:
    def __init__(self, root):
        self.root = root
        self.root.title("🏫 E.E.S.T. N°2 - Panel de Administración")
        self.root.geometry("1100x720")
        self.root.configure(bg=COLORS['fondo'])
        self.root.minsize(1000, 650)
        
        # Variables para el registro
        self.cap = None
        self.running = False
        self.frame_actual = None
        self.foto_tomada = None
        self.ruta_foto = None
        
        # Variables para el admin
        self.base_datos = None
        
        # Configurar grid principal
        self.root.grid_rowconfigure(0, weight=0)  # Banner
        self.root.grid_rowconfigure(1, weight=0)  # Barra de navegación
        self.root.grid_rowconfigure(2, weight=1)  # Contenido
        self.root.grid_columnconfigure(0, weight=1)
        
        # Crear widgets
        self.crear_banner()
        self.crear_navegacion()
        self.crear_contenido()
        
        # Cargar datos del admin
        self.actualizar_lista_alumnos()
        
        # Iniciar cámara del registro
        self.iniciar_camara()
        self.actualizar_video()
        
        # Mostrar vista por defecto (Registro)
        self.mostrar_vista("registro")
    
    # ============================================
    # BANNER SUPERIOR
    # ============================================
    
    def crear_banner(self):
        banner = tk.Frame(self.root, bg=COLORS['azul_oscuro'], height=60)
        banner.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        banner.grid_propagate(False)
        
        frame_banner = tk.Frame(banner, bg=COLORS['azul_oscuro'])
        frame_banner.pack(expand=True)
        
        tk.Label(
            frame_banner,
            text="🏫 E.E.S.T. N°2 - Panel de Administración",
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
            text="Ing. Emilio Rebuelto - Berisso",
            font=("Segoe UI", 10),
            bg=COLORS['azul_oscuro'],
            fg=COLORS['texto_secundario']
        ).pack(side=tk.LEFT)
    
    # ============================================
    # BARRA DE NAVEGACIÓN (Pestañas)
    # ============================================
    
    def crear_navegacion(self):
        nav = tk.Frame(self.root, bg=COLORS['fondo_card'], height=40)
        nav.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        nav.grid_propagate(False)
        
        self.btn_registro = tk.Button(
            nav,
            text="📝 Registrar Alumno",
            command=lambda: self.mostrar_vista("registro"),
            font=("Segoe UI", 10, "bold"),
            bg=COLORS['azul_medio'],
            fg=COLORS['texto'],
            activebackground=COLORS['azul_claro'],
            activeforeground=COLORS['texto'],
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=5
        )
        self.btn_registro.pack(side=tk.LEFT, padx=5)
        
        self.btn_admin = tk.Button(
            nav,
            text="👨‍🏫 Gestionar Alumnos",
            command=lambda: self.mostrar_vista("admin"),
            font=("Segoe UI", 10, "bold"),
            bg=COLORS['fondo_card'],
            fg=COLORS['texto_secundario'],
            activebackground=COLORS['borde'],
            activeforeground=COLORS['texto'],
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=5
        )
        self.btn_admin.pack(side=tk.LEFT, padx=5)
        
        btn_salir = tk.Button(
            nav,
            text="❌ Salir",
            command=self.salir,
            font=("Segoe UI", 10, "bold"),
            bg=COLORS['rojo'],
            fg=COLORS['texto'],
            activebackground="#da3633",
            activeforeground=COLORS['texto'],
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=5
        )
        btn_salir.pack(side=tk.RIGHT, padx=5)
    
    # ============================================
    # CONTENIDO (cambia según la vista)
    # ============================================
    
    def crear_contenido(self):
        # Frame contenedor
        self.frame_contenido = tk.Frame(self.root, bg=COLORS['fondo'])
        self.frame_contenido.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.frame_contenido.grid_rowconfigure(0, weight=1)
        self.frame_contenido.grid_columnconfigure(0, weight=1)
        
        # === VISTA REGISTRO (Cámara Grande) ===
        self.frame_registro = tk.Frame(self.frame_contenido, bg=COLORS['fondo'])
        self.frame_registro.grid(row=0, column=0, sticky="nsew")
        self.frame_registro.grid_rowconfigure(0, weight=1)
        self.frame_registro.grid_columnconfigure(0, weight=3)  # Video más grande
        self.frame_registro.grid_columnconfigure(1, weight=1)  # Datos más pequeños
        
        # ---- Video (Cámara Grande) ----
        frame_video = tk.Frame(
            self.frame_registro,
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
        
        # ---- Datos del registro ----
        frame_datos = tk.Frame(
            self.frame_registro,
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
        frame_datos.grid_rowconfigure(7, weight=0)
        frame_datos.grid_columnconfigure(0, weight=1)
        
        tk.Label(
            frame_datos,
            text="📋 DATOS DEL ALUMNO",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS['fondo_card'],
            fg=COLORS['texto'],
            padx=10,
            pady=5
        ).grid(row=0, column=0, sticky="w")
        
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
        
        tk.Label(
            frame_datos,
            text="📸 Foto:",
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
        
        btn_tomar = tk.Button(
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
        btn_tomar.pack(side=tk.LEFT, padx=5)
        
        btn_registrar = tk.Button(
            frame_botones,
            text="💾 Registrar",
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
        
        self.label_estado_registro = tk.Label(
            frame_datos,
            text="✅ Listo para registrar",
            font=("Segoe UI", 9),
            bg=COLORS['fondo_card'],
            fg=COLORS['verde']
        )
        self.label_estado_registro.grid(row=7, column=0, sticky="w", padx=10, pady=(0, 5))
        
        # === VISTA ADMIN ===
        self.frame_admin = tk.Frame(self.frame_contenido, bg=COLORS['fondo'])
        self.frame_admin.grid(row=0, column=0, sticky="nsew")
        self.frame_admin.grid_rowconfigure(0, weight=0)
        self.frame_admin.grid_rowconfigure(1, weight=1)
        self.frame_admin.grid_rowconfigure(2, weight=0)
        self.frame_admin.grid_columnconfigure(0, weight=1)
        
        # Botones del admin
        frame_admin_botones = tk.Frame(self.frame_admin, bg=COLORS['fondo'])
        frame_admin_botones.grid(row=0, column=0, sticky="ew", pady=10)
        
        btn_eliminar = tk.Button(
            frame_admin_botones,
            text="🗑️ Eliminar Alumno",
            command=self.eliminar_alumno,
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
        btn_eliminar.pack(side=tk.LEFT, padx=5)
        
        btn_actualizar = tk.Button(
            frame_admin_botones,
            text="🔄 Actualizar Lista",
            command=self.actualizar_lista_alumnos,
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
        btn_actualizar.pack(side=tk.LEFT, padx=5)
        
        # Lista de alumnos
        tk.Label(
            self.frame_admin,
            text="📋 Alumnos Registrados:",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS['fondo'],
            fg=COLORS['texto_secundario']
        ).grid(row=1, column=0, sticky="w", pady=(10, 5))
        
        frame_lista = tk.Frame(self.frame_admin, bg=COLORS['fondo'])
        frame_lista.grid(row=2, column=0, sticky="nsew")
        frame_lista.grid_rowconfigure(0, weight=1)
        frame_lista.grid_columnconfigure(0, weight=1)
        
        scrollbar = tk.Scrollbar(frame_lista, bg=COLORS['fondo_card'])
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.lista_alumnos = tk.Listbox(
            frame_lista,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 10),
            bg=COLORS['fondo_input'],
            fg=COLORS['texto'],
            selectmode=tk.SINGLE,
            relief=tk.FLAT,
            bd=1,
            highlightbackground=COLORS['borde'],
            highlightcolor=COLORS['azul_claro'],
            highlightthickness=1,
            activestyle='none'
        )
        self.lista_alumnos.grid(row=0, column=0, sticky="nsew")
        scrollbar.config(command=self.lista_alumnos.yview)
        
        self.label_estado_admin = tk.Label(
            self.frame_admin,
            text="✅ Sistema listo",
            font=("Segoe UI", 9),
            bg=COLORS['fondo'],
            fg=COLORS['verde']
        )
        self.label_estado_admin.grid(row=3, column=0, sticky="w", pady=10)
    
    # ============================================
    # NAVEGACIÓN
    # ============================================
    
    def mostrar_vista(self, vista):
        """Cambia entre las vistas de Registro y Admin"""
        if vista == "registro":
            self.frame_registro.tkraise()
            self.btn_registro.config(bg=COLORS['azul_medio'], fg=COLORS['texto'])
            self.btn_admin.config(bg=COLORS['fondo_card'], fg=COLORS['texto_secundario'])
            self.root.title("📝 Registrar Alumno - E.E.S.T. N°2")
        else:
            self.frame_admin.tkraise()
            self.btn_admin.config(bg=COLORS['azul_medio'], fg=COLORS['texto'])
            self.btn_registro.config(bg=COLORS['fondo_card'], fg=COLORS['texto_secundario'])
            self.root.title("👨‍🏫 Gestionar Alumnos - E.E.S.T. N°2")
            self.actualizar_lista_alumnos()
    
    # ============================================
    # FUNCIONES DEL REGISTRO
    # ============================================
    
    def iniciar_camara(self):
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("No se pudo acceder a la cámara")
            self.running = True
            self.label_estado_registro.config(text="✅ Cámara iniciada", fg=COLORS['verde'])
        except Exception as e:
            self.label_estado_registro.config(text=f"❌ Error: {e}", fg=COLORS['rojo'])
    
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
                    new_w = 600
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
    
    def tomar_foto(self):
        if self.frame_actual is None:
            messagebox.showwarning("⚠️", "No hay imagen de la cámara")
            return
        
        self.foto_tomada = self.frame_actual.copy()
        
        img_rgb = cv2.cvtColor(self.foto_tomada, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img_rgb)
        img = img.resize((200, 150), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(image=img)
        self.label_foto_tomada.config(image=img_tk)
        self.label_foto_tomada.image = img_tk
        
        self.label_estado_registro.config(text="📸 Foto tomada, completa los datos", fg=COLORS['amarillo'])
    
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
            
            self.label_estado_registro.config(text="🔄 Generando embedding...", fg=COLORS['amarillo'])
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
                f"Curso: {curso}"
            )
            
            self.label_estado_registro.config(text=f"✅ Alumno '{nombre.title()}' registrado", fg=COLORS['verde'])
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al registrar:\n{e}")
            self.label_estado_registro.config(text=f"❌ Error: {e}", fg=COLORS['rojo'])
    
    # ============================================
    # FUNCIONES DEL ADMIN
    # ============================================
    
    def actualizar_lista_alumnos(self):
        self.lista_alumnos.delete(0, tk.END)
        
        try:
            alumnos = listar_alumnos()
            if alumnos:
                for alumno in sorted(alumnos):
                    self.lista_alumnos.insert(tk.END, alumno)
                self.label_estado_admin.config(
                    text=f"✅ {len(alumnos)} alumnos cargados",
                    fg=COLORS['verde']
                )
            else:
                self.lista_alumnos.insert(tk.END, "⚠️ No hay alumnos registrados")
                self.label_estado_admin.config(
                    text="⚠️ Base de datos vacía",
                    fg=COLORS['amarillo']
                )
        except Exception as e:
            self.lista_alumnos.insert(tk.END, f"❌ Error: {e}")
            self.label_estado_admin.config(
                text=f"❌ Error al cargar datos",
                fg=COLORS['rojo']
            )
    
    def eliminar_alumno(self):
        seleccionado = self.lista_alumnos.curselection()
        if not seleccionado:
            messagebox.showwarning("⚠️", "Primero selecciona un alumno de la lista")
            return
        
        alumno = self.lista_alumnos.get(seleccionado[0])
        
        if alumno.startswith(("⚠️", "❌")):
            return
        
        if messagebox.askyesno(
            "🗑️ Confirmar Eliminación",
            f"¿Estás seguro de eliminar a '{alumno}'?\n\n"
            "Esta acción no se puede deshacer."
        ):
            try:
                if eliminar_alumno(alumno):
                    messagebox.showinfo(
                        "✅ Eliminado",
                        f"El alumno '{alumno}' fue eliminado correctamente"
                    )
                    self.actualizar_lista_alumnos()
                    self.label_estado_admin.config(
                        text=f"✅ Alumno '{alumno}' eliminado",
                        fg=COLORS['verde']
                    )
                else:
                    messagebox.showerror(
                        "❌ Error",
                        f"No se pudo eliminar a '{alumno}'"
                    )
            except Exception as e:
                messagebox.showerror("❌ Error", f"Error al eliminar: {e}")
    
    # ============================================
    # SALIR
    # ============================================
    
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
    app = PanelCentral(root)
    root.mainloop()
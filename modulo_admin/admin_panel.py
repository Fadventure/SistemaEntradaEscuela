# admin_panel.py - Panel de Administración
# Versión 2.0 - Estilo Oscuro

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# ============================================
# CONFIGURACIÓN DE RUTAS
# ============================================

RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ_PROYECTO)

from base_datos.db_manager import cargar_db, guardar_db, listar_alumnos, eliminar_alumno

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
}

# ============================================
# CLASE PRINCIPAL
# ============================================

class PanelAdmin:
    def __init__(self, root):
        self.root = root
        self.root.title("👨‍🏫 Panel de Administración - E.E.S.T. N°2")
        self.root.geometry("700x550")
        self.root.configure(bg=COLORS['fondo'])
        self.root.minsize(600, 400)
        
        # Variables
        self.base_datos = None
        
        # Crear widgets
        self.crear_widgets()
        
        # Cargar datos
        self.actualizar_lista()
    
    def crear_widgets(self):
        """Crea todos los elementos con estilo oscuro"""
        
        # ============================================
        # BANNER SUPERIOR
        # ============================================
        banner = tk.Frame(self.root, bg=COLORS['azul_oscuro'], height=55)
        banner.pack(fill=tk.X, pady=(0, 10))
        banner.pack_propagate(False)
        
        frame_banner = tk.Frame(banner, bg=COLORS['azul_oscuro'])
        frame_banner.pack(expand=True)
        
        tk.Label(
            frame_banner,
            text="👨‍🏫 Panel de Administración",
            font=("Segoe UI", 14, "bold"),
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
            text="E.E.S.T. N°2 - Gestión de Alumnos",
            font=("Segoe UI", 10),
            bg=COLORS['azul_oscuro'],
            fg=COLORS['texto_secundario']
        ).pack(side=tk.LEFT)
        
        # ============================================
        # FRAME PRINCIPAL
        # ============================================
        frame_principal = tk.Frame(self.root, bg=COLORS['fondo'])
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # ---- Botones ----
        frame_botones = tk.Frame(frame_principal, bg=COLORS['fondo'])
        frame_botones.pack(fill=tk.X, pady=10)
        
        btn_registrar = tk.Button(
            frame_botones,
            text="➕ Registrar Alumno",
            command=self.registrar_alumno,
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
        btn_registrar.pack(side=tk.LEFT, padx=5)
        
        btn_eliminar = tk.Button(
            frame_botones,
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
            frame_botones,
            text="🔄 Actualizar Lista",
            command=self.actualizar_lista,
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
        
        # ---- Lista de alumnos ----
        tk.Label(
            frame_principal,
            text="📋 Alumnos Registrados:",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS['fondo'],
            fg=COLORS['texto_secundario']
        ).pack(anchor=tk.W, pady=(10, 5))
        
        frame_lista = tk.Frame(frame_principal, bg=COLORS['fondo'])
        frame_lista.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(frame_lista, bg=COLORS['fondo_card'])
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
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
        self.lista_alumnos.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.lista_alumnos.yview)
        
        # ---- Estado ----
        self.label_estado = tk.Label(
            frame_principal,
            text="✅ Sistema listo",
            font=("Segoe UI", 9),
            bg=COLORS['fondo'],
            fg=COLORS['verde']
        )
        self.label_estado.pack(pady=10)
    
    def actualizar_lista(self):
        self.lista_alumnos.delete(0, tk.END)
        
        try:
            alumnos = listar_alumnos()
            if alumnos:
                for alumno in sorted(alumnos):
                    self.lista_alumnos.insert(tk.END, alumno)
                self.label_estado.config(
                    text=f"✅ {len(alumnos)} alumnos cargados",
                    fg=COLORS['verde']
                )
            else:
                self.lista_alumnos.insert(tk.END, "⚠️ No hay alumnos registrados")
                self.label_estado.config(
                    text="⚠️ Base de datos vacía",
                    fg=COLORS['amarillo']
                )
        except Exception as e:
            self.lista_alumnos.insert(tk.END, f"❌ Error: {e}")
            self.label_estado.config(
                text=f"❌ Error al cargar datos",
                fg=COLORS['rojo']
            )
    
    def registrar_alumno(self):
        import subprocess
        script_path = os.path.join("modulo_admin", "registro_alumno_gui.py")
        
        try:
            subprocess.Popen(
                ["python", script_path],
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            self.label_estado.config(
                text="📝 Registro abierto en nueva ventana",
                fg=COLORS['azul_info']
            )
        except Exception as e:
            messagebox.showerror(
                "❌ Error",
                f"No se pudo abrir el registro:\n{e}\n\n"
                "Ejecuta manualmente: python modulo_admin/registro_alumno_gui.py"
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
                    self.actualizar_lista()
                    self.label_estado.config(
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
    
    def salir(self):
        self.root.quit()
        self.root.destroy()

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    root = tk.Tk()
    app = PanelAdmin(root)
    root.mainloop()
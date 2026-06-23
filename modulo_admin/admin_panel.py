# admin_panel.py - Panel de Administración para profesores
import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# ============================================
# CONFIGURACIÓN DE RUTAS
# ============================================

# Agregar la raíz del proyecto al path
RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ_PROYECTO)

# Ahora importar desde base_datos
from base_datos.db_manager import cargar_db, guardar_db, listar_alumnos, eliminar_alumno

# ============================================
# CLASE PRINCIPAL
# ============================================

class PanelAdmin:
    def __init__(self, root):
        self.root = root
        self.root.title("👨‍🏫 Panel de Administración - Alumnos")
        self.root.geometry("600x450")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.base_datos = None
        
        # Crear widgets
        self.crear_widgets()
        
        # Cargar datos
        self.actualizar_lista()
    
    def crear_widgets(self):
        """Crea todos los elementos de la interfaz"""
        
        # Título
        titulo = tk.Label(
            self.root, 
            text="📚 GESTIÓN DE ALUMNOS",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        titulo.pack(pady=10)
        
        # Frame de botones
        frame_botones = tk.Frame(self.root, bg="#f0f0f0")
        frame_botones.pack(pady=10)
        
        # Botones
        btn_registrar = tk.Button(
            frame_botones,
            text="➕ Registrar Alumno",
            command=self.registrar_alumno,
            font=("Arial", 10),
            bg="#27ae60",
            fg="white",
            padx=15,
            pady=8,
            cursor="hand2"
        )
        btn_registrar.pack(side=tk.LEFT, padx=5)
        
        btn_eliminar = tk.Button(
            frame_botones,
            text="🗑️ Eliminar Alumno",
            command=self.eliminar_alumno,
            font=("Arial", 10),
            bg="#e74c3c",
            fg="white",
            padx=15,
            pady=8,
            cursor="hand2"
        )
        btn_eliminar.pack(side=tk.LEFT, padx=5)
        
        btn_actualizar = tk.Button(
            frame_botones,
            text="🔄 Actualizar Lista",
            command=self.actualizar_lista,
            font=("Arial", 10),
            bg="#3498db",
            fg="white",
            padx=15,
            pady=8,
            cursor="hand2"
        )
        btn_actualizar.pack(side=tk.LEFT, padx=5)
        
        btn_salir = tk.Button(
            frame_botones,
            text="❌ Salir",
            command=self.salir,
            font=("Arial", 10),
            bg="#95a5a6",
            fg="white",
            padx=15,
            pady=8,
            cursor="hand2"
        )
        btn_salir.pack(side=tk.RIGHT, padx=5)
        
        # Lista de alumnos
        tk.Label(
            self.root,
            text="📋 Alumnos Registrados:",
            font=("Arial", 10, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        ).pack(anchor=tk.W, padx=20, pady=(10, 5))
        
        # Frame para la lista con scroll
        frame_lista = tk.Frame(self.root, bg="#f0f0f0")
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.lista_alumnos = tk.Listbox(
            frame_lista,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 10),
            bg="#ffffff",
            fg="#2c3e50",
            selectmode=tk.SINGLE
        )
        self.lista_alumnos.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.lista_alumnos.yview)
        
        # Estado
        self.label_estado = tk.Label(
            self.root,
            text="✅ Sistema listo",
            font=("Arial", 9),
            bg="#f0f0f0",
            fg="#27ae60"
        )
        self.label_estado.pack(pady=10)
    
    def actualizar_lista(self):
        """Actualiza la lista de alumnos desde la base de datos"""
        self.lista_alumnos.delete(0, tk.END)
        
        try:
            alumnos = listar_alumnos()
            if alumnos:
                for alumno in sorted(alumnos):
                    self.lista_alumnos.insert(tk.END, alumno)
                self.label_estado.config(text=f"✅ {len(alumnos)} alumnos cargados", fg="#27ae60")
            else:
                self.lista_alumnos.insert(tk.END, "⚠️ No hay alumnos registrados")
                self.label_estado.config(text="⚠️ Base de datos vacía", fg="#f39c12")
        except Exception as e:
            self.lista_alumnos.insert(tk.END, f"❌ Error: {e}")
            self.label_estado.config(text=f"❌ Error al cargar datos", fg="#e74c3c")
    
    def registrar_alumno(self):
        """Abre el registro de un nuevo alumno"""
        import subprocess
        import os
        
        # Ruta al script de registro
        script_path = os.path.join("modulo_admin", "registrar_alumnos.py")
        
        try:
            # Abrir el script en una nueva terminal
            subprocess.Popen(
                ["python", script_path],
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            self.label_estado.config(text="📝 Registro abierto en nueva ventana", fg="#3498db")
        except Exception as e:
            messagebox.showerror(
                "❌ Error",
                f"No se pudo abrir el registro:\n{e}\n\n"
                "Ejecuta manualmente: python modulo_admin/registrar_alumnos.py"
            )
    
    def eliminar_alumno(self):
        """Elimina el alumno seleccionado"""
        seleccionado = self.lista_alumnos.curselection()
        if not seleccionado:
            messagebox.showwarning(
                "⚠️ Seleccionar",
                "Primero selecciona un alumno de la lista"
            )
            return
        
        alumno = self.lista_alumnos.get(seleccionado[0])
        
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
                    self.label_estado.config(text=f"✅ Alumno '{alumno}' eliminado", fg="#27ae60")
                else:
                    messagebox.showerror(
                        "❌ Error",
                        f"No se pudo eliminar a '{alumno}'"
                    )
            except Exception as e:
                messagebox.showerror("❌ Error", f"Error al eliminar: {e}")
    
    def salir(self):
        """Cierra el panel"""
        self.root.quit()
        self.root.destroy()

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    root = tk.Tk()
    app = PanelAdmin(root)
    root.mainloop()
# admin_panel.py - Panel para profesores (NUEVO)
import tkinter as tk
from tkinter import ttk, messagebox
from db_manager import cargar_db, guardar_db, listar_alumnos

class PanelAdmin:
    def __init__(self, root):
        self.root = root
        self.root.title("👨‍🏫 Panel de Administración - Alumnos")
        self.root.geometry("600x400")
        
        # Crear widgets
        self.crear_widgets()
        self.actualizar_lista()
    
    def crear_widgets(self):
        # Título
        tk.Label(self.root, text="📚 GESTIÓN DE ALUMNOS", 
                 font=("Arial", 16, "bold")).pack(pady=10)
        
        # Botones
        frame_botones = tk.Frame(self.root)
        frame_botones.pack(pady=10)
        
        tk.Button(frame_botones, text="➕ Registrar Alumno", 
                  command=self.registrar_alumno).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_botones, text="🗑️ Eliminar Alumno", 
                  command=self.eliminar_alumno).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_botones, text="🔄 Actualizar Lista", 
                  command=self.actualizar_lista).pack(side=tk.LEFT, padx=5)
        
        # Lista de alumnos
        self.lista_alumnos = tk.Listbox(self.root, height=15)
        self.lista_alumnos.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def actualizar_lista(self):
        self.lista_alumnos.delete(0, tk.END)
        for alumno in listar_alumnos():
            self.lista_alumnos.insert(tk.END, alumno)
    
    def registrar_alumno(self):
        # Aquí abrirías tu registrar_alumnos.py
        messagebox.showinfo("Info", "Abrir registro de alumnos")
    
    def eliminar_alumno(self):
        seleccionado = self.lista_alumnos.curselection()
        if seleccionado:
            alumno = self.lista_alumnos.get(seleccionado[0])
            if messagebox.askyesno("Confirmar", f"¿Eliminar a {alumno}?"):
                # Aquí iría la eliminación
                messagebox.showinfo("Info", f"Alumno {alumno} eliminado")
                self.actualizar_lista()

# Ejecutar
if __name__ == "__main__":
    root = tk.Tk()
    app = PanelAdmin(root)
    root.mainloop()
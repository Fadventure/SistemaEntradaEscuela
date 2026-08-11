# 🎓 Sistema de Reconocimiento Facial para Control de Ingreso Escolar

Sistema de control de acceso mediante reconocimiento facial, desarrollado como proyecto para la E.E.S.T. N°2 "Ing. Emilio Rebuelto" de Berisso. Permite registrar alumnos, identificar rostros en tiempo real y llevar un registro de ingresos.

---

## 📋 Descripción

Sistema que utiliza reconocimiento facial con **ArcFace** para controlar el ingreso de alumnos a la escuela. Registra la entrada con fecha y hora, y está diseñado para ser escalable, pudiendo integrar en el futuro una cerradura eléctrica controlada por **Arduino**.

---

## 🛠️ Tecnologías utilizadas

| Tecnología | Versión | Uso |
|------------|---------|-----|
| Python | 3.12 | Lenguaje principal |
| DeepFace | 0.0.79 | Reconocimiento facial |
| ArcFace | - | Modelo de reconocimiento |
| OpenCV | 4.10.0 | Captura y procesamiento de imágenes |
| Tkinter | - | Interfaz gráfica |
| Pillow | - | Procesamiento de imágenes en GUI |
| MySQL | (Pendiente) | Base de datos para producción |
| Arduino | (Pendiente) | Control de cerradura eléctrica |

---

## 📂 Estructura del proyecto
SistemaEntradaEscuela/
├── base_datos/
│ ├── alumnos_db.pkl # Base de datos de alumnos
│ └── db_manager.py # Gestor de la base de datos
├── logs/
│ └── registro_ingresos.txt # Registro de ingresos
├── modulo_admin/
│ └── panel_central.py # Panel de administración
├── recursos/
│ └── logo_escuela.png # Logo de la escuela
├── rostros/
│ └── alumnos_registrados/ # Fotos de los alumnos
├── sistema_principal/
│ └── gui_camara.py # Sistema de reconocimiento
├── venv/ # Entorno virtual
├── README.md # Este archivo
└── requirements.txt # Dependencias

---

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Fadventure/SistemaEntradaEscuela.git
cd SistemaEntradaEscuela

---

## Crear y activar entorno virtual

python -m venv venv
venv\Scripts\activate      # En Windows
# source venv/bin/activate  # En Linux/Mac

## Instalar dependencias
pip install -r requirements.txt

## 1. Panel de Administración (Registro de alumnos)
python modulo_admin/panel_central.py

## Funcionalidades:

📝 Registrar nuevos alumnos (con cámara)

👨‍🏫 Gestionar lista de alumnos

🗑️ Eliminar alumnos

🔍 Buscar alumnos por nombre

## Recomendaciones para el registro:

✅ Usar luz natural (frente a una ventana)

✅ Rostro bien centrado y sin sombras

✅ Expresión neutra

❌ No usar flash

## 2. Sistema de Reconocimiento (Control de acceso)
python sistema_principal/gui_camara.py

## Controles:

Tecla	    Acción
ESPACIO	    Capturar y reconocer rostro
R	        Reiniciar sistema
ESC	        Salir

## Indicadores:

🟢 Acceso concedido

🔴 Acceso denegado

📏 Distancia de coincidencia (umbral: 0.65)


⚙️ Configuración
Cambiar cámara
## Edita el archivo sistema_principal/gui_camara.py:
CAMARA_INDICE = 0  # 0 = integrada, 1 = USB externa, 2 = segunda USB


## Ajustar umbral de reconocimiento
UMBRAL = 0.65  # Valor entre 0.0 y 1.0 (menor = más estricto)

📊 Registro de ingresos
## Los ingresos se guardan en logs/registro_ingresos.txt con el formato:
2026-08-11 01:16:00 - fernando - CONCEDIDO
2026-08-11 01:16:17 - fernando - CONCEDIDO
2026-08-11 01:16:30 - DESCONOCIDO - DENEGADO


🔧 Solución de problemas
Problema	                                    Posible solución
No se detecta rostro	            Asegurar buena iluminación y rostro centrado
Reconocimiento falla	            Verificar umbral, re-registrar con mejor luz
Cámara no funciona	                    Cambiar CAMARA_INDICE a 0, 1 o 2
Error de importación	            Activar entorno virtual (venv\Scripts\activate)
Distancia de reconocimiento alta	Mejorar condiciones de luz al registrar y al capturar
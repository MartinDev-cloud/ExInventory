import sys
import os
import tkinter as tk
import threading

# --- Ruta base del proyecto (independiente del lugar donde esté) ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Detectar y añadir la carpeta del entorno virtual (.venv) multiplataforma ---
if os.name == "nt":  # Windows
    venv_path = os.path.join(BASE_DIR, ".venv", "Lib", "site-packages")
else:  # Linux / macOS
    py_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
    venv_path = os.path.join(BASE_DIR, ".venv", "lib", py_version, "site-packages")

if os.path.exists(venv_path) and venv_path not in sys.path:
    sys.path.insert(0, venv_path)

# --- Añadir también la carpeta raíz del proyecto al path ---
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# --- Importar backend Flask ---
from backend.main_documentos import app as flask_app

# --- Importar las páginas ---
from frontend.pages.inicio import Inicio
from frontend.pages.productos import Productos
from frontend.pages.inventarios import Inventarios
from frontend.pages.servicios import Servicios
from frontend.pages.platillos import Platillos
from frontend.pages.generarFactura import GenerarFactura
from frontend.pages.verDocumentos import VerDocumentos
from frontend.pages.generarCotizacion import GenerarCotizacion
from frontend.pages.documentos import Documentos
from frontend.pages.entradasYSalidas import EntradasYSalidas

# --- Componentes globales ---
from frontend.components.footer import Footer
from frontend.components.header import Header
from frontend.components.sidebar import Sidebar

def run_flask():
    flask_app.run(port=5000, debug=False, use_reloader=False)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ExInventory - Gestión de Inventarios y Facturación")
        self.geometry("1200x900")
        self.resizable(True, True)  # ✅ Permite redimensionar horizontal y verticalmente

        self.center_window()

        # Estructura principal del grid
        self.grid_rowconfigure(1, weight=1)    
        self.grid_columnconfigure(1, weight=1) 

        # Header global
        self.header = Header(self, controller=self)
        self.header.grid(row=0, column=0, columnspan=2, sticky="ew")

        # Sidebar global
        self.sidebar = Sidebar(self, controller=self)
        self.sidebar.grid(row=1, column=0, sticky="ns")
        self.grid_rowconfigure(1, weight=1)  

        # Contenedor principal
        self.container = tk.Frame(self, bg="white")
        self.container.grid(row=1, column=1, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Diccionario de páginas
        self.pages = {}
        for PageClass in (
            Inicio, Inventarios, Productos, Servicios, Platillos, EntradasYSalidas,
            GenerarFactura, GenerarCotizacion, VerDocumentos, Documentos
        ):
            page_name = PageClass.__name__
            frame = PageClass(parent=self.container, controller=self)
            self.pages[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")  

        self.show_page("Inicio")

        # Footer global
        self.footer = Footer(self)
        self.footer.grid(row=2, column=0, columnspan=2, sticky="ew")

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def show_page(self, page_name):
        # Guardar la página anterior
        if hasattr(self.header, "set_previous_page"):
            current = getattr(self, "current_page", None)
            if current:
                self.header.set_previous_page(current)
            self.current_page = page_name

        page = self.pages[page_name]
        page.tkraise()
        if hasattr(page, "on_show"):
            page.on_show()


if __name__ == "__main__":
    # 🚀 Levantar Flask en segundo plano
    threading.Thread(target=run_flask, daemon=True).start()

    app = App()
    app.mainloop()

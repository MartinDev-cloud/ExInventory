import tkinter as tk
from PIL import Image, ImageTk
import os

def format_time(time_str):
    """Convierte un string 'HH:MM' a formato 'hh:mm AM/PM'."""
    if not time_str:
        return ""
    try:
        hour, minute = map(int, time_str.split(":"))
        suffix = "AM" if hour < 12 else "PM"
        hour12 = hour % 12
        if hour12 == 0:
            hour12 = 12
        return f"{hour12}:{minute:02d} {suffix}"
    except Exception as e:
        print("Error al formatear hora:", e)
        return time_str

# Ruta compartida en la raíz del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR)))
ASSETS_ROOT = os.path.join(PROJECT_ROOT, "assets")

class DetailModal:
    _modal_open = False  # Variable de clase para evitar múltiples modales

    def __init__(self, parent, item, fields, on_edit=None, on_delete=None, title="Detalle"):
        if DetailModal._modal_open:
            return  # Si ya hay un modal abierto, no hacer nada
        DetailModal._modal_open = True

        self.parent = parent
        self.item = item
        self.fields = fields
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.title = title
        self.detail_window = None
        self.show_modal()

    def show_modal(self):
        self.detail_window = tk.Toplevel(self.parent)
        detail = self.detail_window
        detail.title(self.title)
        detail.configure(bg="white")
        width, height = 320, 700
        detail.geometry(f"{width}x{height}")
        detail.resizable(False, False)

        # --- Centrar ventana ---
        x = (detail.winfo_screenwidth() // 2) - (width // 2)
        y = (detail.winfo_screenheight() // 2) - (height // 2)
        detail.geometry(f"{width}x{height}+{x}+{y}")

        # --- Bloquear interacción con la ventana principal ---
        detail.transient(self.parent)
        detail.grab_set()
        detail.protocol("WM_DELETE_WINDOW", self.close_modal)  # cerrar correctamente

        # --- Título principal ---
        if "numeroHabitacion" in self.item:
            title_text = f"{self.item['numeroHabitacion']}"
        elif "nombrePlato" in self.item:
            title_text = self.item["nombrePlato"]
        elif "nombre" in self.item:
            title_text = self.item["nombre"]
        else:
            title_text = "Sin nombre"
        tk.Label(detail, text=title_text, font=("Arial", 16, "bold"), bg="white").pack(pady=10)

        # --- Imagen ---
        folder_map = {
            "productos": "productosIMG",
            "servicios": "serviciosIMG",
            "platillos": "platillosIMG",
            "inventarioS": "inventariosIMG"
        }
        item_type = self.item.get("item_type")
        if not item_type:
            if "numeroHabitacion" in self.item:
                item_type = "servicios"
            elif "nombrePlato" in self.item:
                item_type = "platillos"
            elif "nombre" in self.item:
                item_type = "productos"
            else:
                item_type = "inventarioS"

        folder = folder_map.get(item_type, "productosIMG")
        image_file = self.item.get("imagen")
        if image_file:
            image_path = os.path.join(ASSETS_ROOT, folder, image_file)
            image_path = os.path.normpath(image_path)
            if os.path.exists(image_path):
                try:
                    img = Image.open(image_path).resize((170, 170), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    lbl_img = tk.Label(detail, image=photo, bg="white")
                    lbl_img.image = photo
                    lbl_img.pack(pady=10)
                except Exception as e:
                    tk.Label(detail, text=f"❌ Error al cargar imagen: {e}", bg="white", fg="red").pack(pady=10)
            else:
                tk.Label(detail, text="❌ Imagen no encontrada", bg="white", fg="red").pack(pady=10)
        else:
            tk.Label(detail, text="📦 Sin imagen", bg="white").pack(pady=10)

        # --- Contenedor con scroll ---
        container = tk.Frame(detail, bg="white")
        container.pack(padx=20, pady=10, fill="both", expand=True)

        canvas = tk.Canvas(container, bg="white", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        info_frame = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=info_frame, anchor="nw")
        info_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        def _on_mouse_wheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mouse_wheel)
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

        # --- Campos ---
        for idx, (label, key) in enumerate(self.fields):
            value = self.item.get(key, "No especificado")
            if key in ["horaEntrada", "horaSalida"] and value != "No especificado":
                value = format_time(value)
            tk.Label(info_frame, text=label, font=("Arial", 10, "bold"), bg="white", anchor="w").grid(row=idx, column=0, sticky="w", pady=4)
            tk.Label(info_frame, text=value, bg="white", anchor="w").grid(row=idx, column=1, sticky="w", pady=4)

        # --- Botones ---
        action_frame = tk.Frame(detail, bg="white")
        action_frame.pack(pady=20)

        if self.on_edit:
            tk.Button(action_frame, text="Actualizar", bg="#28a745", fg="white",
                      padx=12, pady=6, relief="flat", cursor="hand2",
                      command=lambda: [self.close_modal(), self.on_edit(self.item)]).grid(row=0, column=0, padx=10)
        if self.on_delete:
            tk.Button(action_frame, text="Eliminar", bg="#dc3545", fg="white",
                      padx=12, pady=6, relief="flat", cursor="hand2",
                      command=lambda: [self.close_modal(), self.on_delete(self.item.get("_id"))]).grid(row=0, column=1, padx=10)

        # --- Esperar que se cierre ---
        self.detail_window.wait_window()

    def close_modal(self):
        if self.detail_window:
            self.detail_window.destroy()
        DetailModal._modal_open = False

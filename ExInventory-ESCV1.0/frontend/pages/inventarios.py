import tkinter as tk
from PIL import Image, ImageTk
import os

class Inventarios(tk.Frame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, bg="#f5f7fa", *args, **kwargs)
        self.controller = controller

        # --- Título y subtítulo ---
        tk.Label(
            self, text="Gestión de Inventarios",
            font=("Arial", 18, "bold"), bg="#f5f7fa"
        ).pack(pady=(20, 5))  # menos separación abajo

        tk.Label(
            self, text="Selecciona el inventario que deseas administrar",
            font=("Arial", 11), bg="#f5f7fa"
        ).pack(pady=(0, 20))  # separación mínima

        # --- Contenedor principal (sin expand) ---
        container = tk.Frame(self, bg="#f5f7fa")
        container.pack()  # quitar expand=True

        # --- Ruta de imágenes ---
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        assets_path = os.path.join(BASE_DIR, "frontend", "assets")

        # Diccionario de cards
        cards_info = [
            {"title": "Productos", "image": "productos.webp", "color": "#28a745", "page": "Productos"},
            {"title": "Servicios", "image": "servicios.webp", "color": "#17a2b8", "page": "Servicios"},
            {"title": "Platillos", "image": "platillos.webp", "color": "#ffc107", "page": "Platillos"},
        ]

        # --- Contenedor de tarjetas ---
        frame_cards = tk.Frame(container, bg="#f5f7fa")
        frame_cards.pack(pady=45, anchor="n")  # ajustar anchor y quitar padding extra

        self.cards_images = []

        for info in cards_info:
            img_path = os.path.join(assets_path, info["image"])
            image = self.load_image(img_path)
            self.cards_images.append(image)

            card = self.create_card(
                frame_cards,
                title=info["title"],
                image=image,
                bg=info["color"],
                command=lambda page=info["page"]: self.controller.show_page(page)
            )
            card.pack(side="left", padx=30, pady=5)  # menos padding lateral y vertical

    def load_image(self, path, size=(120, 120)):
        try:
            img = Image.open(path)
            img = img.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            fallback = Image.new("RGB", size, "#ddd")
            return ImageTk.PhotoImage(fallback)

    def create_card(self, parent, title, image, bg, command):
        frame = tk.Frame(parent, bg="white", relief="raised", bd=2)
        frame.configure(width=250, height=300)
        frame.pack_propagate(False)

        img_label = tk.Label(frame, image=image, bg="white")
        img_label.pack(pady=(20, 10))

        title_label = tk.Label(
            frame, text=title, bg="white",
            font=("Arial", 11, "bold"), wraplength=200
        )
        title_label.pack(pady=(0, 10))  # menos separación

        btn = tk.Button(
            frame, text="Seleccionar", bg=bg, fg="white",
            font=("Arial", 10, "bold"), width=18, height=1,
            activebackground="#333", relief="flat",
            command=command
        )
        btn.pack()

        def on_enter(e): frame.config(bd=4)
        def on_leave(e): frame.config(bd=2)

        for widget in (frame, img_label, title_label):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

        return frame

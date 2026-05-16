import tkinter as tk
from PIL import Image, ImageTk
import os

# Ruta compartida en la raíz del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR)))

class CardItem(tk.Frame):
    def __init__(self, parent, title, description="", image_filename=None,
                 onClick=None, width=210, height=210, image_type="productosIMG"):
        super().__init__(parent, bg=parent["bg"], width=width, height=height)
        self.onClick = onClick
        self.width = width
        self.height = height
        self.grid_propagate(False)
        
        # Construir ruta correcta según tipo de imagen
        self.assets_dir = os.path.normpath(os.path.join(PROJECT_ROOT, "assets", image_type))

        # --- Sombra suave ---
        self.shadow = tk.Frame(self, bg="#e5e7eb", width=width, height=height)
        self.shadow.place(x=3, y=3)

        # --- Card principal ---
        self.card_frame = tk.Frame(
            self, bg="white", width=width, height=height,
            bd=0, relief="flat", highlightthickness=1, highlightbackground="#e5e7eb"
        )
        self.card_frame.place(x=0, y=0)
        self.card_frame.pack_propagate(False)
        self.card_frame.configure(cursor="hand2")

        # --- Nombre del producto ---
        self.title_label = tk.Label(
            self.card_frame,
            text=title,
            bg="white",
            fg="#111827",
            font=("Arial", 13, "bold"),
            wraplength=width - 20,
            justify="center"
        )
        self.title_label.pack(pady=(10, 5))
        self.title_label.bind("<Button-1>", self.handle_click)

        # --- Imagen ---
        if image_filename:
            image_path = os.path.join(self.assets_dir, image_filename)
            if os.path.exists(image_path):
                img = Image.open(image_path).resize((120, 120), Image.Resampling.LANCZOS)
                self.photo = ImageTk.PhotoImage(img)
                lbl_img = tk.Label(self.card_frame, image=self.photo, bg="white")
                lbl_img.pack(pady=(5, 5))
                lbl_img.bind("<Button-1>", self.handle_click)
            else:
                # Si no existe el archivo, placeholder
                lbl_img = tk.Label(self.card_frame, text="❌ Img", font=("Arial", 12), bg="white", fg="red")
                lbl_img.pack(pady=(5, 5))
                lbl_img.bind("<Button-1>", self.handle_click)
        else:
            lbl_img = tk.Label(self.card_frame, text="📦", font=("Arial", 40), bg="white")
            lbl_img.pack(pady=(5, 5))
            lbl_img.bind("<Button-1>", self.handle_click)

        # --- Precio / descripción ---
        self.price_label = tk.Label(
            self.card_frame,
            text=description,
            bg="white",
            fg="#16a34a",  # Verde para precios
            font=("Arial", 12, "bold"),
            wraplength=width - 20,
            justify="center"
        )
        self.price_label.pack(pady=(5, 10))
        self.price_label.bind("<Button-1>", self.handle_click)

        # --- Hover effect ---
        self.card_frame.bind("<Enter>", self.on_hover)
        self.card_frame.bind("<Leave>", self.on_leave)
        self.card_frame.bind("<Button-1>", self.handle_click)

    # --- Eventos ---
    def handle_click(self, event=None):
        if self.onClick:
            self.onClick()

    def on_hover(self, event):
        self.card_frame.configure(bg="#f9fafb", highlightbackground="#d1d5db")
        self.shadow.configure(bg="#d1d5db")

    def on_leave(self, event):
        self.card_frame.configure(bg="white", highlightbackground="#e5e7eb")
        self.shadow.configure(bg="#e5e7eb")

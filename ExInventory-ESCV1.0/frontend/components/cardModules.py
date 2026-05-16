import tkinter as tk
from PIL import Image, ImageTk
import os

# Ruta absoluta a la carpeta de assets
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # carpeta /components
ASSETS_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "assets"))

class Card(tk.Frame):
    def __init__(self, parent, title, image_filename=None, bgColor="#0039e6", onClick=None):
        super().__init__(parent, bg=bgColor, width=250, height=200, highlightthickness=0)

        self.bgColor = bgColor
        self.onClick = onClick
        self.configure(cursor="hand2")
        self.grid_propagate(False)

        # Imagen opcional
        if image_filename:
            image_path = os.path.join(ASSETS_DIR, image_filename)
            try:
                img = Image.open(image_path)
                img = img.resize((80, 80), Image.Resampling.LANCZOS)
                self.photo = ImageTk.PhotoImage(img)
                self.image_label = tk.Label(self, image=self.photo, bg=bgColor)
                self.image_label.pack(pady=(10, 5))
                self.image_label.bind("<Button-1>", self.handle_click)
            except FileNotFoundError:
                self.image_label = tk.Label(self, text="[Imagen no encontrada]", bg=bgColor, fg="white")
                self.image_label.pack(pady=(10, 5))

        # Título
        self.title_label = tk.Label(
            self,
            text=title,
            bg=bgColor,
            fg="white",
            font=("Arial", 14, "bold"),
            wraplength=200,
            justify="center"
        )
        self.title_label.pack(expand=True)
        self.title_label.bind("<Button-1>", self.handle_click)

        # Hover y clic
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.handle_click)

    def handle_click(self, event=None):
        if self.onClick:
            self.onClick()

    def on_hover(self, event):
        self.configure(highlightbackground="black", highlightthickness=2)

    def on_leave(self, event):
        self.configure(highlightthickness=0)

import tkinter as tk
from PIL import Image, ImageTk, Image
import os
import webbrowser  # Para abrir la página de la DIAN

class Documentos(tk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent, bg="#f5f7fa")
        self.controller = controller

        # --- Título y subtítulo ---
        tk.Label(
            self, text="Facturación y Cotización", 
            font=("Arial", 18, "bold"), 
            bg="#f5f7fa"
        ).pack(pady=(20, 5))

        tk.Label(
            self, text="Selecciona el documento que deseas generar", 
            bg="#f5f7fa",
            font=("Arial", 11)
        ).pack(pady=(0, 20))

        # --- Contenedor principal ---
        container = tk.Frame(self, bg="#f5f7fa")
        container.pack()

        # --- Rutas de imágenes ---
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        assets_path = os.path.join(BASE_DIR, "frontend", "assets")
        factura_img_path = os.path.join(assets_path, "factura.webp")
        cotizacion_img_path = os.path.join(assets_path, "cotizacion.webp")
        dian_img_path = os.path.join(assets_path, "DIANLogo.webp")  # nueva imagen para DIAN

        # --- Función para cargar imágenes ---
        def load_image(path, size=(150, 150)):
            try:
                img = Image.open(path)
                img = img.resize(size, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
            except Exception:
                fallback = Image.new("RGB", size, "#ddd")
                return ImageTk.PhotoImage(fallback)

        factura_img = load_image(factura_img_path)
        cotizacion_img = load_image(cotizacion_img_path)
        dian_img = load_image(dian_img_path)

        # --- Tarjetas de acción ---
        frame_cards = tk.Frame(container, bg="#f5f7fa")
        frame_cards.pack(pady=50, anchor="n")

        # Factura Electrónica interna
        self.create_card(
            frame_cards, 
            title="Generar Factura Electrónica", 
            image=factura_img, 
            bg="#28a745",
            command=lambda: controller.show_page("GenerarFactura")
        ).pack(side="left", padx=30, pady=5)

        # Cotización
        self.create_card(
            frame_cards, 
            title="Generar Cotización", 
            image=cotizacion_img, 
            bg="#17a2b8",
            command=lambda: controller.show_page("GenerarCotizacion")
        ).pack(side="left", padx=30, pady=5)

        # Factura Oficial DIAN
        self.create_card(
            frame_cards,
            title="Factura Oficial DIAN",
            image=dian_img,
            bg="#ffc107",
            command=lambda: webbrowser.open("https://catalogo-vpfe-hab.dian.gov.co/User/Login")
        ).pack(side="left", padx=30, pady=5)

        # Mantener referencias de imágenes
        self.factura_img = factura_img
        self.cotizacion_img = cotizacion_img
        self.dian_img = dian_img

    # --- Crear una tarjeta ---
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
        title_label.pack(pady=(0, 10))

        btn = tk.Button(
            frame, text="Seleccionar", bg=bg, fg="white",
            font=("Arial", 10, "bold"), width=18, height=1,
            activebackground="#333", relief="flat",
            command=command
        )
        btn.pack()

        # --- Efecto hover ---
        def on_enter(e): frame.config(bd=4)
        def on_leave(e): frame.config(bd=2)

        for widget in (frame, img_label, title_label):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

        return frame

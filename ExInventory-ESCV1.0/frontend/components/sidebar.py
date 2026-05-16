import tkinter as tk

class Sidebar(tk.Frame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, bg="white", width=160, *args, **kwargs)
        self.controller = controller
        self.grid_propagate(False)  # Mantener ancho fijo

        # Colores
        self.active_bg = "#f3f4f6"      # Fondo del botón activo
        self.hover_bg = "#f3f4f6"       # Fondo al pasar el mouse
        self.default_bg = "white"
        self.active_bar_color = "#28a745"  # Barra lateral activa

        # Estilo base para botones
        self.button_style = {
            "font": ("Arial", 12),
            "anchor": "w",
            "bg": self.default_bg,
            "fg": "#374151",
            "relief": "flat",
            "bd": 0,
            "padx": 12,
            "pady": 8,
        }
        self.section_title_style = {
            "font": ("Arial", 10, "bold"),
            "bg": self.default_bg,
            "fg": "#9ca3af",
            "anchor": "w"
        }
        self.espacioEntreBTN = 5
        self.espacioLadosBTN = 8

        self.buttons = {}
        self.active_button = None
        self.active_bar = None

        # ===== Botón Inicio arriba del todo =====
        self.add_button("🏠 Inicio", lambda: self.show_page("Inicio"))

        # ===== Sección NAVEGACIÓN =====
        self.add_section("NAVEGACIÓN", [
            ("📦 Inventarios", "Inventarios"),
        ])

        # ===== Sección NAVEGACIÓN =====
        self.add_section("MOVIMIENTOS", [
            ("🔄 Ventas", "EntradasYSalidas"),
            ("🧾 Facturación", "Documentos"),
            ("📑 Ver Facturas", "VerDocumentos"),
        ])

        # ===== Sección CONFIGURACIÓN =====
        self.add_section("CONFIGURACIÓN", [
            ("⚙️ Ajustes", "Configuracion"),
            ("👥 Usuarios", "Usuarios"),
            ("❓ Ayuda", "Ayuda"),
        ])

        self.add_section("SOBRE NOSOTROS", [
            ("📄 Política de Privacidad", "Privacidad"),
            ("📜 Términos y Condiciones", "Terminos"),
        ])
        
    def add_section(self, title, items):
        # Solo espacio y título, sin separador visual
        tk.Label(self, text=title, **self.section_title_style).pack(fill="x", pady=(15,5), padx=self.espacioLadosBTN)
        for text, page in items:
            self.add_button(text, lambda p=page: self.show_page(p))

    def add_button(self, text, command, bottom=False):
        btn = tk.Button(self, text=text, command=lambda b=text: self.on_click(b, command), **self.button_style)
        pack_opts = {"fill": "x", "pady": self.espacioEntreBTN, "padx": self.espacioLadosBTN}
        if bottom:
            pack_opts["side"] = "bottom"
        btn.pack(**pack_opts)

        # Hover effect
        btn.bind("<Enter>", lambda e: e.widget.config(bg=self.hover_bg))
        btn.bind("<Leave>", lambda e: e.widget.config(bg=self.active_bg if self.active_button == text else self.default_bg))

        self.buttons[text] = btn

    def on_click(self, button_text, command):
        # Reset botones
        for b_text, btn in self.buttons.items():
            btn.config(bg=self.default_bg)

        # Botón activo
        active_btn = self.buttons[button_text]
        active_btn.config(bg=self.active_bg)
        self.active_button = button_text

        # Barra lateral activa
        if self.active_bar:
            self.active_bar.place_forget()
        self.active_bar = tk.Frame(self, bg=self.active_bar_color, width=4)
        self.active_bar.place(x=0, y=active_btn.winfo_y(), height=active_btn.winfo_height())

        command()

    def show_page(self, page_name):
        self.controller.show_page(page_name)

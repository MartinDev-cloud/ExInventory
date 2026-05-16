import tkinter as tk
from PIL import Image, ImageTk
import os
from tkinter import messagebox

# ---------------- Tooltip ----------------
class Tooltip:
    def __init__(self, parent, delay=300):
        self.parent = parent
        self.delay = delay
        self.tw = None
        self.id = None
        self.text = ""

    def show_tooltip(self, text, event):
        self.text = text
        self.schedule(event)

    def schedule(self, event):
        self.unschedule()
        self.id = self.parent.after(self.delay, lambda: self._create_tooltip(event))

    def unschedule(self):
        if self.id:
            self.parent.after_cancel(self.id)
            self.id = None

    def _create_tooltip(self, event):
        if self.tw:
            self.tw.destroy()
        x = event.x_root + 10
        y = event.y_root + 10
        self.tw = tk.Toplevel(self.parent)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            self.tw, text=self.text, justify='left',
            background="#333", foreground="white",
            relief='solid', bd=0, padx=6, pady=3,
            font=("Arial", 10)
        )
        label.pack()

    def hide_tooltip(self):
        self.unschedule()
        if self.tw:
            self.tw.destroy()
            self.tw = None

# ---------------- Header ----------------
class Header(tk.Frame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, bg="white", *args, **kwargs)
        self.controller = controller
        self.previous_page = None
        self.usuario_logueado = None
        self.tooltip = Tooltip(self.winfo_toplevel())

        # --- Logo + título a la izquierda ---
        left_frame = tk.Frame(self, bg="white")
        left_frame.pack(side="left", padx=20, pady=10)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base_dir, "..", "assets", "logo.webp")

        try:
            img = Image.open(logo_path).convert("RGBA").resize((90, 90), Image.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(img)
            tk.Label(left_frame, image=self.logo_img, bg="white").pack(side="left")
        except Exception as e:
            print("⚠ Error cargando logo:", e)
            tk.Label(left_frame, text="[Logo]", bg="white", fg="#0039e6").pack(side="left")

        tk.Label(left_frame, text="ExInventory", font=("Arial", 20, "bold"),
                 fg="#0039e6", bg="white").pack(side="left", padx=12)

        # --- Botones a la derecha ---
        self.right_frame = tk.Frame(self, bg="white")
        self.right_frame.pack(side="right", padx=20, pady=10)

        # Botones
        self.back_button = tk.Button(
            self.right_frame, text="⬅ Volver", font=("Arial", 12),
            bg="white", fg="#333", bd=0, relief="flat", cursor="hand2",
            command=self.go_back
        )

        self.login_button = tk.Button(
            self.right_frame, text="Iniciar sesión", font=("Arial", 11, "bold"),
            bg="#1d4ed8", fg="white", bd=0, relief="flat", cursor="hand2",
            activebackground="#2563eb", activeforeground="white",
            padx=14, pady=6,
            command=self.iniciar_sesion
        )

        self.import_button = tk.Button(
            self.right_frame, text="Importar documentos", font=("Arial", 11, "bold"),
            bg="#16a34a", fg="white", bd=0, relief="flat", cursor="hand2",
            activebackground="#22c55e", activeforeground="white",
            padx=14, pady=6,
            command=self.importar_datos
        )
        self.import_button.pack_forget()

        self.welcome_label = tk.Label(self.right_frame, text="", font=("Arial", 11, "bold"),
                                      bg="white", fg="#0039e6")
        self.welcome_label.pack_forget()

        self.notif_icon = self._make_icon_button(self.right_frame, "notificaciones.webp", "Notificaciones")

        # --- Orden inicial (sin sesión) ---
        self.notif_icon.pack(side="right", padx=8)
        self.back_button.pack(side="right", padx=8)
        self.login_button.pack(side="right", padx=8)

    # ---------------- Funciones ----------------
    def iniciar_sesion(self):
        from frontend.pages.usuario_logueado import LoginModal
        LoginModal(self.controller, controller=self.controller)

    def actualizar_usuario_logueado(self, usuario):
        self.usuario_logueado = usuario
        self.login_button.pack_forget()
        # Limpiar botones actuales
        for widget in self.right_frame.winfo_children():
            widget.pack_forget()
        # Mostrar bienvenida (cambia aquí: usa 'nombre' en lugar de 'nombres' y 'apellidos')
        self.welcome_label.config(
            text=f"¡Te damos la Bienvenida!, {usuario.get('nombre', '')}".strip()
        )
        self.welcome_label.pack(side="left", padx=8)

        # Mostrar botones: Importar + Cerrar sesión al lado
        self.import_button.pack(side="left", padx=8)
        if not hasattr(self, "logout_button"):
            self.logout_button = tk.Button(
                self.right_frame, text="🚪 Cerrar sesión", font=("Arial", 11, "bold"),
                bg="#ef4444", fg="white", bd=0, relief="flat", cursor="hand2",
                activebackground="#f87171", activeforeground="white",
                padx=14, pady=6,
                command=self.cerrar_sesion
            )
        self.logout_button.pack(side="left", padx=8)

        # Notificaciones y volver a la derecha
        self.notif_icon.pack(side="right", padx=8)
        self.back_button.pack(side="right", padx=8)

    def cerrar_sesion(self):
        self.usuario_logueado = None
        messagebox.showinfo("Sesión cerrada", "Has cerrado sesión correctamente")

        # Restaurar estado inicial (sin sesión)
        for widget in self.right_frame.winfo_children():
            widget.pack_forget()

        self.notif_icon.pack(side="right", padx=8)
        self.back_button.pack(side="right", padx=8)
        self.login_button.pack(side="right", padx=8)

        self.welcome_label.pack_forget()
        self.import_button.pack_forget()
        if hasattr(self, "logout_button"):
            self.logout_button.pack_forget()

    def importar_datos(self):
        if not self.usuario_logueado:
            messagebox.showwarning("Acceso denegado", "Debes iniciar sesión para importar datos.")

    def _make_icon_button(self, parent, filename, tooltip=""):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "..", "assets", filename)

        try:
            img = Image.open(path).convert("RGBA").resize((32, 32), Image.LANCZOS)
            icon_img = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"⚠ Error cargando icono {filename}: {e}")
            return

        lbl = tk.Label(parent, image=icon_img, bg="white", cursor="hand2")
        lbl.image = icon_img

        def on_enter(e):
            img_hover = img.resize((36, 36), Image.LANCZOS)
            lbl.image = ImageTk.PhotoImage(img_hover)
            lbl.config(image=lbl.image)

        def on_leave(e):
            lbl.image = icon_img
            lbl.config(image=lbl.image)

        lbl.bind("<Enter>", on_enter)
        lbl.bind("<Leave>", on_leave)

        if tooltip:
            lbl.bind("<Enter>", lambda e: self.tooltip.show_tooltip(tooltip, e))
            lbl.bind("<Leave>", lambda e: self.tooltip.hide_tooltip())

        return lbl

    def set_previous_page(self, page_name):
        self.previous_page = page_name

    def go_back(self):
        if self.previous_page and self.previous_page in self.controller.pages:
            self.controller.show_page(self.previous_page)
        else:
            self.controller.show_page("Inicio")

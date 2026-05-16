import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageFilter
import requests, os

API_URL = "http://localhost:5001/login_escritorio"

class LoginModal(tk.Toplevel):
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.title("Iniciar Sesión")
        self.config(bg="#f0f0f0")

        # --- Modal encima del padre y bloqueándolo ---
        self.transient(parent)
        self.grab_set()

        # --- Tamaño fijo ---
        self.width = 800
        self.height = 600
        self.resizable(False, False)
        self.pos_x = (self.winfo_screenwidth() - self.width) // 2
        self.pos_y = (self.winfo_screenheight() - self.height) // 2
        self.geometry(f"{self.width}x{self.height}+{self.pos_x}+{self.pos_y}")

        # --- Bloquear movimiento ---
        self._first_configure = True
        self.bind("<Configure>", self.lock_position)

        # --- Manejar cierre con X ---
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # --- Contenedor principal ---
        container = tk.Frame(self, bg="#f0f0f0")
        container.pack(fill="both", expand=True)

        # --- Lado izquierdo ---
        left = tk.Frame(container, bg="#f0f0f0")
        left.pack(side="left", fill="both", expand=True)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        bg_path = os.path.join(base_dir, "..", "assets", "bg.png")
        logo_path = os.path.join(base_dir, "..", "assets", "logo.webp")

        try:
            bg = Image.open(bg_path).resize((800,900)).filter(ImageFilter.GaussianBlur(4))
            self.bg_img = ImageTk.PhotoImage(bg)
            tk.Label(left, image=self.bg_img, bg="#f0f0f0").place(relx=0.5, rely=0.5, anchor="center")
        except:
            pass

        tk.Label(left, text="ExInventory", font=("Arial", 38, "bold"),
                 bg="#f0f0f0", fg="#0039e6").place(relx=0.5, rely=0.15, anchor="center")

        try:
            img = Image.open(logo_path).resize((250,250))
            self.logo_img = ImageTk.PhotoImage(img)
            tk.Label(left, image=self.logo_img, bg="#f0f0f0").place(relx=0.5, rely=0.45, anchor="center")
        except:
            tk.Label(left, text="[LOGO]", font=("Arial", 40, "bold"),
                     bg="#f0f0f0", fg="#0039e6").place(relx=0.5, rely=0.45, anchor="center")

        tk.Label(left, text="Tu inventario, siempre a mano", font=("Arial", 14, "italic"),
                 bg="#f0f0f0", fg="#555555").place(relx=0.5, rely=0.75, anchor="center")
        tk.Label(left, text="© 2025 Imperial Devs", font=("Arial", 9),
                 bg="#f0f0f0", fg="#0039e6").place(relx=0.5, rely=0.80, anchor="center")

        # --- Lado derecho (card) ---
        right = tk.Frame(container, bg="#f0f0f0")
        right.pack(side="right", fill="both", expand=True)

        card = tk.Frame(right, bg="#ffffff", bd=0, highlightthickness=0)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.config(padx=35, pady=35)

        tk.Label(card, text="Iniciar Sesión", font=("Arial", 25, "bold"), bg="#ffffff").pack(pady=(0,10))

        # Texto explicativo para el usuario
        tk.Label(card, text="Inicia sesión para importar tus documentos, gestiona tus ventas e inventarios a través de nuestra página web www.exinventory.com",
                font=("Arial", 11), bg="#ffffff", fg="#555555",wraplength=320).pack(pady=(0,25))

        # --- Campos ---
        self.entry_email = self.crear_input(card, "Correo electrónico")
        self.entry_password = self.crear_input(card, "Contraseña", show="*")

        # --- Botones ---
        btn_container = tk.Frame(card, bg="#ffffff")
        btn_container.pack(fill="x", pady=(0,15))

        b_login = tk.Button(btn_container, text="Ingresar", bg="#16a34a", fg="white",
                            font=("Arial", 12, "bold"), padx=25, pady=8, bd=0,
                            activebackground="#15803d", cursor="hand2", command=self.login)
        b_login.pack(side="left", expand=True, fill="x", pady=2)

        b_close = tk.Button(btn_container, text="Cerrar", bg="#E53935", fg="white",
                            font=("Arial", 12, "bold"), padx=25, pady=8, bd=0,
                            activebackground="#c62828", cursor="hand2", command=self.on_close)
        b_close.pack(side="right", expand=True, fill="x", padx=(8,0), pady=2)

        tk.Button(card, text="¿No tienes una cuenta? Crea una", bd=0,
                  fg="#007fff", bg="#ffffff", font=("Arial", 11),
                  cursor="hand2", command=self.abrir_registro).pack()

        tk.Label(card,
                 text="Al hacer clic en Ingresar aceptas nuestros\nTérminos y Condiciones y Política de Privacidad.",
                 bg="#ffffff", fg="#777777", font=("Arial", 9), justify="center").pack(pady=(10,0))

    # --- Funciones ---
    def lock_position(self, event):
        """Evita que la ventana se mueva"""
        if self._first_configure:
            self._first_configure = False
            return
        self.geometry(f"{self.width}x{self.height}+{self.pos_x}+{self.pos_y}")

    def crear_input(self, parent, label_text, show=None):
        tk.Label(parent, text=label_text, bg="#ffffff", font=("Arial", 12)).pack(anchor="w", padx=15)
        entry = tk.Entry(parent, width=34, font=("Arial", 12), bd=1, relief="solid", show=show)
        entry.pack(pady=(4,15), padx=15)
        return entry

    def login(self):
        email = self.entry_email.get().strip()
        password = self.entry_password.get().strip()
        if not email or not password:
            messagebox.showwarning("Campos vacíos", "Ingresa correo y contraseña.")
            return
        try:
            resp = requests.post(API_URL, json={"email": email, "password": password})
            if resp.status_code == 200:
                user = resp.json()["user"]
                if user.get("tipo") != "emprendedor":
                    messagebox.showerror("Error", "Este correo no está registrado como emprendedor")
                    return
                messagebox.showinfo("Éxito", f"Bienvenido {user['nombre']}")
                if hasattr(self.controller, "header"):
                    self.controller.header.actualizar_usuario_logueado(user)
                self.on_close()
            elif resp.status_code == 400 and resp.json().get("error") == "Usuario no encontrado":
                messagebox.showerror("Error", "Este correo no está registrado")
            else:
                messagebox.showerror("Error", resp.json().get("error", "Error desconocido"))
        except Exception as e:
            messagebox.showerror("Error", f"No hay conexión con servidor:\n{e}")

    def abrir_registro(self):
        from frontend.pages.registro_logueo import RegisterModal
        self.on_close()
        RegisterModal(self.parent, controller=self.controller)

    def on_close(self):
        """Cerrar modal y devolver la ventana padre"""
        self.destroy()
        self.parent.deiconify()

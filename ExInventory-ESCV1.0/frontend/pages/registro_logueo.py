# Fixed version of the RegisterModal class in register_modal.py
# Changes:
# - Changed tipo_persona options to lowercase to match schema enum
# - Added more robust error handling
# - Ensured all validations are consistent
# - Modified to handle text pasting better: Changed "ubicacion" to a Text widget for multi-line support
# - Added select-all functionality to Entry widgets (Ctrl+A or double-click)

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageFilter
import requests, os
import re  # Para validaciones de email y teléfono

API_URL = "http://localhost:5001/api/auth/register_escritorio"

class RegisterModal(tk.Toplevel):
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.title("Registro de Emprendedor")
        self.config(bg="#f0f0f0")

        # --- Modal encima del padre y bloqueándolo ---
        self.transient(parent)
        self.grab_set()

        # --- Tamaño fijo y centrado (ampliado) ---
        self.width = 1200
        self.height = 900
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

        # Card con borde sutil para mejor apariencia
        card = tk.Frame(right, bg="#ffffff", bd=2, relief="ridge", highlightbackground="#e0e0e0", highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.config(padx=40, pady=40)  # Aumenté el padding para más espacio

        tk.Label(card, text="Regístra tu Negocio", font=("Arial", 26, "bold"), bg="#ffffff", fg="#333333").pack(pady=(0,15))
        tk.Label(card, text="Conéctate y crea tu cuenta para gestionar tus ventas e inventarios a través de nuestra página web www.exinventory.com",
            font=("Arial", 12), bg="#ffffff", fg="#666666", wraplength=500, justify="center").pack(pady=(0,15))

        # --- Campos organizados en filas de dos (títulos arriba, dos campos por fila) ---
        # Fila 1: Nombres y Apellidos
        row1 = tk.Frame(card, bg="#ffffff")
        row1.pack(fill="x", pady=(0,15))
        self.entry_nombres = self.crear_input(row1, "Nombre(s)", side="left")
        self.entry_apellidos = self.crear_input(row1, "Apellido(s)", side="right")

        # Fila 2: Correo y Teléfono
        row2 = tk.Frame(card, bg="#ffffff")
        row2.pack(fill="x", pady=(0,15))
        self.entry_email = self.crear_input(row2, "Correo electrónico", side="left")
        self.entry_telefono = self.crear_input(row2, "Teléfono", side="right")

        # Fila 3: Contraseña y Confirmar Contraseña
        row3 = tk.Frame(card, bg="#ffffff")
        row3.pack(fill="x", pady=(0,15))
        self.entry_password = self.crear_input(row3, "Contraseña", side="left")
        self.entry_confirm_password = self.crear_input(row3, "Confirmar contraseña", side="right")

        # Fila 4: Tipo de persona y Nombre de marca
        row4 = tk.Frame(card, bg="#ffffff")
        row4.pack(fill="x", pady=(0,15))
        # Izquierda: Tipo de persona
        left_frame = tk.Frame(row4, bg="#ffffff")
        left_frame.pack(side="left", expand=True, fill="x", padx=(0,12))
       # --- Tipo de persona (visual bonito, pero envía valores válidos) ---
        tk.Label(left_frame, text="Tipo de persona", bg="#ffffff", font=("Arial", 12, "bold"), fg="#333333").pack(anchor="w", pady=(0, 7), padx=(5, 0))

        # Diccionario visual → valor real (para el backend)
        self.opciones_tipo = {"Selecciona": "", "Natural": "natural", "Jurídica": "juridica"}
        self.var_tipo_persona = tk.StringVar(value="Selecciona")

        self.option_tipo_persona = tk.OptionMenu(left_frame, self.var_tipo_persona, *self.opciones_tipo.keys())
        self.option_tipo_persona.config(font=("Arial", 12), width=16, bg="#f9f9f9", relief="solid", bd=1)
        self.option_tipo_persona.pack(pady=(0,12), padx=(20, 0))

        # Derecha: Nombre de marca
        right_frame = tk.Frame(row4, bg="#ffffff")
        right_frame.pack(side="right", expand=True, fill="x", padx=(0,19),pady=(10,0))
        self.entry_marca = self.crear_input(right_frame, "Nombre de tu negocio")
        self.entry_marca.pack(padx=(28,0), pady=(10,25))

        # Fila 5: Ubicación (ancho completo) - Cambiado a Text para permitir multilínea
        row5 = tk.Frame(card, bg="#ffffff")
        row5.pack(fill="x", pady=(0,15))
        self.entry_ubicacion = self.crear_text(row5, "Ubicación (Ciudad o Dirección del negocio)", height=3, width=50)

        # Checkboxes con mejor estilo
        self.var_aceptar_datos = tk.BooleanVar()
        self.var_aceptar_condiciones = tk.BooleanVar()
        tk.Checkbutton(card, text="Acepto expresamente la autorización de tratamiento de datos personales y la Política de Tratamiento de Datos Personales de ExInventory",
                       variable=self.var_aceptar_datos, bg="#ffffff", font=("Arial", 10), fg="#555555", wraplength=450, justify="left").pack(anchor="w", pady=(0,5))
        tk.Checkbutton(card, text="Acepto expresamente las condiciones de activación de mi cuenta por medio de la plataforma, para la gestion de mis inventarios, productos y/o servicios ofrecidos en mi negocio",
                       variable=self.var_aceptar_condiciones, bg="#ffffff", font=("Arial", 10), fg="#555555", wraplength=450, justify="left").pack(anchor="w", pady=(5,15))

        # --- Botones ---
        btn_container = tk.Frame(card, bg="#ffffff")
        btn_container.pack(fill="x", pady=(15,5))

        b_register = tk.Button(btn_container, text="REGISTRARSE", bg="#16a34a", fg="white",
                               font=("Arial", 12, "bold"), padx=25, pady=8, bd=0,
                               activebackground="#15803d", cursor="hand2", command=self.registrar)
        b_register.pack(side="left", expand=True, fill="x", padx=(0,5))

        b_close = tk.Button(btn_container, text="volver a inicio", bg="#e7e7e7", fg="#333333",
                            font=("Arial", 12, "bold"), padx=25, pady=8, bd=0, relief="flat",
                            activebackground="#e0e0e0", cursor="hand2", command=self.on_close)
        b_close.pack(side="right", expand=True, fill="x", padx=(5,0))

        tk.Button(card, text="¿Ya tienes una cuenta? Inicia sesión aquí", bd=0, fg="#007fff",
                  bg="#ffffff", font=("Arial", 11,), cursor="hand2", command=self.abrir_login).pack(pady=(15))

        tk.Label(card, text="Al registrarte aceptas nuestros\nTérminos y Condiciones y Política de Privacidad.",
                 bg="#ffffff", fg="#888888", font=("Arial", 9), justify="center").pack(pady=(5))

    # --- Funciones ---
    def lock_position(self, event):
        """Evita que la ventana se mueva"""
        if self._first_configure:
            self._first_configure = False
            return
        self.geometry(f"{self.width}x{self.height}+{self.pos_x}+{self.pos_y}")

    def crear_input(self, parent, label_text, show=None, width=20, side=None):
        if side:
            frame = tk.Frame(parent, bg="#ffffff")
            frame.pack(side=side, expand=True, fill="x", padx=5)
            tk.Label(frame, text=label_text, bg="#ffffff", font=("Arial", 12, "bold"), fg="#333333").pack(anchor="w")
            entry = tk.Entry(frame, width=width, font=("Arial", 12), bd=1, relief="solid", bg="#f9f9f9", fg="#333333", show=show)
            entry.pack(pady=(5,0))
            # Añadir funcionalidad para seleccionar todo
            entry.bind("<Control-a>", lambda e: entry.select_range(0, 'end'))
            entry.bind("<Double-1>", lambda e: entry.select_range(0, 'end'))
            return entry
        else:
            tk.Label(parent, text=label_text, bg="#ffffff", font=("Arial", 12, "bold"), fg="#333333").pack(anchor="w", padx=15)
            entry = tk.Entry(parent, width=width, font=("Arial", 12), bd=1, relief="solid", bg="#f9f9f9", fg="#333333", show=show)
            entry.pack(pady=(5,15), padx=15)
            # Añadir funcionalidad para seleccionar todo
            entry.bind("<Control-a>", lambda e: entry.select_range(0, 'end'))
            entry.bind("<Double-1>", lambda e: entry.select_range(0, 'end'))
            return entry

    def crear_text(self, parent, label_text, height=3, width=50):
        """Crea un widget Text para campos multilínea como ubicación"""
        tk.Label(parent, text=label_text, bg="#ffffff", font=("Arial", 12, "bold"), fg="#333333").pack(anchor="w", padx=15)
        text = tk.Text(parent, height=height, width=width, font=("Arial", 12), bd=1, relief="solid", bg="#f9f9f9", fg="#333333", wrap="word")
        text.pack(pady=(5,15), padx=15)
        # Añadir funcionalidad para seleccionar todo
        text.bind("<Control-a>", lambda e: text.tag_add("sel", "1.0", "end"))
        text.bind("<Double-1>", lambda e: text.tag_add("sel", "1.0", "end"))
        return text

    def validar_email(self, email):
        return re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email)

    def validar_telefono(self, telefono):
        return telefono.isdigit() and 7 <= len(telefono) <= 15

    def registrar(self):
        # Obtener valores
        nombres = self.entry_nombres.get().strip()
        apellidos = self.entry_apellidos.get().strip()
        email = self.entry_email.get().strip()
        telefono = self.entry_telefono.get().strip()
        password = self.entry_password.get().strip()
        confirm_password = self.entry_confirm_password.get().strip()
        tipo_persona = self.opciones_tipo.get(self.var_tipo_persona.get(), "")
        marca = self.entry_marca.get().strip()
        ubicacion = self.entry_ubicacion.get("1.0", "end-1c").strip()  # Para Text widget
        aceptar_datos = self.var_aceptar_datos.get()
        aceptar_condiciones = self.var_aceptar_condiciones.get()

        # Validaciones
        errores = []

        if not nombres:
            errores.append("Nombre(s)")
        if len(nombres) > 255:
            errores.append("Los nombres son demasiado largos.")
        if not apellidos:
            errores.append("Apellido(s)")
        if len(apellidos) > 255:
            errores.append("Los apellidos son demasiado largos.")
        if not email:
            errores.append("Correo")
        if not self.validar_email(email):
            errores.append("(El correo debe contener '@' y un dominio válido)")
        if len(email) > 255:
            errores.append("El correo es demasiado largo.")
        if not telefono:
            errores.append("Telefono.")
        if not self.validar_telefono(telefono):
            errores.append("(El teléfono debe contener solo números y tener entre 7 y 15 dígitos)")
        if not password:
            errores.append("Contraseña.")
        if len(password) < 6:
            errores.append("(La contraseña debe tener al menos 6 caracteres)")
        if len(password) > 255:
            errores.append("La contraseña no puede exceder los 255 caracteres.")
        if not confirm_password:
            errores.append("Confirmar contraseña")
        if password != confirm_password:
            errores.append("(Las contraseñas deben coincidir)")
        if tipo_persona == "Selecciona":  # Updated check
            errores.append("Selecciona un tipo de persona.")
        if not marca:
            errores.append("Nombre del negocio")
        if len(marca) > 255:
            errores.append("El nombre del negocio es demasiado largo.")
        if not ubicacion:
            errores.append("Ubicacion del negocio")
        if len(ubicacion) > 40:
            errores.append("La ubicación es demasiado larga.")
        if not aceptar_datos:
            errores.append("Debes aceptar la autorización de tratamiento de datos personales.")
        if not aceptar_condiciones:
            errores.append("Debes aceptar las condiciones de activación de la cuenta.")

        if errores:
            errores.insert(0, "Llena y valida los siguientes campos:\n")  # ← Insertar al inicio
            messagebox.showwarning("Errores de validación", "\n".join(errores))
            return

        # Enviar a API
        try:
            resp = requests.post(API_URL, json={
                "nombres": nombres,
                "apellidos": apellidos,
                "email": email,
                "telefono": telefono,
                "password": password,
                "tipoPersona": tipo_persona,
                "marca": marca,
                "ubicacion": ubicacion,
                "aceptarDatos": aceptar_datos,
                "aceptarCondiciones": aceptar_condiciones,
                "tipo": "emprendedor"
            })
            if resp.status_code == 201:
                messagebox.showinfo("Éxito", resp.json().get("message", "Usuario registrado correctamente"))

                # --- Actualizar header automáticamente ---
                user = {"nombre": f"{nombres} {apellidos}".strip(), "email": email, "tipo": "emprendedor"}
                if hasattr(self.controller, "header"):
                    self.controller.header.actualizar_usuario_logueado(user)

                self.on_close()
            else:
                try:
                    data = resp.json()
                    error_msg = data.get("message", "Error desconocido")

                    # Detección más precisa
                    if "correo" in error_msg.lower() or "email" in error_msg.lower():
                        messagebox.showerror("Correo ya registrado", "Este correo ya está registrado. Intenta con otro.")
                    elif "marca" in error_msg.lower():
                        messagebox.showerror("Marca duplicada", "Este nombre de negocio ya se encuentra registrado.")
                    else:
                        messagebox.showerror("Error en registro", error_msg)

                except Exception:
                    messagebox.showerror("Error inesperado", f"Respuesta no válida del servidor:\n{resp.text}")
        except Exception as e:
            import traceback
            messagebox.showerror("Error de conexión", f"{traceback.format_exc()}")

    def abrir_login(self):
        from frontend.pages.usuario_logueado import LoginModal
        self.on_close()
        LoginModal(self.parent, controller=self.controller)

    def on_close(self):
        """Cerrar modal y devolver la ventana padre"""
        self.destroy()
       
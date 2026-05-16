import tkinter as tk
from tkinter import ttk, messagebox
import requests
import locale

# Configurar locale para formato colombiano (opcional, pero útil)
try:
    locale.setlocale(locale.LC_ALL, 'es_CO.UTF-8')
except locale.Error:
    pass  # Si no está disponible, usar formateo manual

# Importar las bases de datos (asumiendo que están disponibles)
from backend.db import productosdb, serviciosdb, platillosdb

class GenerarCotizacion(tk.Frame):
    IVA = 0  # Para cotizaciones, no aplicar IVA

    def __init__(self, parent, controller=None, refrescar_callback=None):
        super().__init__(parent, bg="#e6f2ff")
        self.controller = controller
        self.editar_id = None
        self.tipo_documento = "Cotización"
        self.refrescar_callback = refrescar_callback

        self.cliente = {
            "nombre": tk.StringVar(),
            "tipoDocumento": tk.StringVar(value="CC"),
            "numeroDocumento": tk.StringVar(),
            "direccion": tk.StringVar(),
            "telefono": tk.StringVar(),
            "email": tk.StringVar()
        }

        self.productos = []

        # Cargar datos desde DB
        self.productos_db = productosdb.obtener_productos()
        self.servicios_db = serviciosdb.obtener_servicios()
        self.platillos_db = platillosdb.obtener_platillos()

        style = ttk.Style()
        style.configure("TFrame", background="#ffffff")
        style.configure("TLabel", background="#ffffff", foreground="#333333", font=("Segoe UI", 10, "bold"))
        style.configure("TEntry", padding=5, font=("Segoe UI", 10), relief="flat", borderwidth=1)
        style.configure("TCombobox", padding=5, font=("Segoe UI", 10), relief="flat")
        style.configure("Card.TLabelframe", background="#ffffff", foreground="#333333", borderwidth=1, relief="solid")
        style.configure("Card.TLabelframe.Label", background="#ffffff", foreground="#007bff", font=("Segoe UI", 12, "bold"))

        self.create_widgets()
        self.add_producto()

    def create_widgets(self):
        # Frame cliente
        frame_cliente = ttk.LabelFrame(self, text="Datos del Cliente", style="Card.TLabelframe")
        frame_cliente.pack(padx=20, pady=10, fill="x")
        # Configurar columnas para expandir las entradas
        frame_cliente.columnconfigure(1, weight=1)
        frame_cliente.columnconfigure(3, weight=1)

        labels = ["Nombre", "Tipo Documento", "Número Documento", "Dirección", "Teléfono", "Correo/Email (opcional)"]
        keys = ["nombre", "tipoDocumento", "numeroDocumento", "direccion", "telefono", "email"]

        for i, (label, key) in enumerate(zip(labels, keys)):
            ttk.Label(frame_cliente, text=f"{label}:").grid(row=i//2, column=(i%2)*2, padx=5, pady=5, sticky="e")
            if key == "tipoDocumento":
                ttk.Combobox(frame_cliente, textvariable=self.cliente[key],
                             values=["CC", "NIT", "TI"], width=5, state="readonly").grid(
                    row=i//2, column=(i%2)*2+1, padx=5, pady=5, sticky="ew")
            else:
                entry = ttk.Entry(frame_cliente, textvariable=self.cliente[key])
                entry.grid(row=i//2, column=(i%2)*2+1, padx=5, pady=5, sticky="ew")
                if key in ["telefono", "numeroDocumento"]:
                    entry.configure(validate="key", validatecommand=(self.register(self.validar_numeros), "%P"))
                elif key == "email":
                    entry.configure(validate="focusout", validatecommand=(self.register(self.validar_email), "%P"))

        # --- Frame productos con scrollbar ---
        contenedor_productos = ttk.LabelFrame(self, text="Productos / Servicios", style="Card.TLabelframe")
        contenedor_productos.pack(padx=20, pady=10, fill="both", expand=True)

        canvas = tk.Canvas(contenedor_productos, bg="#ffffff", highlightthickness=0)
        scroll_y = ttk.Scrollbar(contenedor_productos, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scroll_y.set)

        self.frame_productos = ttk.Frame(canvas, style="Card.TLabelframe")

        # Vincular scroll con el frame interno
        self.frame_productos.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((30, 20), window=self.frame_productos, anchor="nw")

        # Empaquetar scroll y canvas
        canvas.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        # Configurar columnas (sin weight para uniformidad)
        self.frame_productos.columnconfigure(0, weight=0)  # Nombre
        self.frame_productos.columnconfigure(1, weight=0)  # Cantidad
        self.frame_productos.columnconfigure(2, weight=0)  # Precio Unitario
        self.frame_productos.columnconfigure(3, weight=0)  # Precio por Cantidad
        self.frame_productos.columnconfigure(4, weight=0)  # Acción

        # Encabezados
        ttk.Label(self.frame_productos, text="Nombre").grid(row=0, column=0, padx=5, sticky="w")
        ttk.Label(self.frame_productos, text="Cantidad").grid(row=0, column=1, padx=5)
        ttk.Label(self.frame_productos, text="Precio Unitario").grid(row=0, column=2, padx=5)
        ttk.Label(self.frame_productos, text="Precio por Cantidad").grid(row=0, column=3, padx=5)
        ttk.Label(self.frame_productos, text="Acción").grid(row=0, column=4, padx=5)

        # Botón agregar producto
        tk.Button(self, text="Agregar Producto", bg="#007bff", fg="white", font=("Segoe UI", 10, "bold"),
                  activebackground="#0056b3", activeforeground="white", relief="flat",
                  padx=15, pady=8, cursor="hand2", command=self.add_producto).pack(pady=5)

        # Frame resumen
        self.frame_resumen = ttk.LabelFrame(self, text="Resumen", style="Card.TLabelframe")
        self.frame_resumen.pack(padx=20, pady=10, fill="x")
        self.lbl_subtotal = ttk.Label(self.frame_resumen, text="Subtotal: 0.00")
        self.lbl_subtotal.pack(anchor="w", padx=10, pady=2)
        self.lbl_total = ttk.Label(self.frame_resumen, text="Total: 0.00",
                                   font=("Segoe UI", 12, "bold"), foreground="#28a745")
        self.lbl_total.pack(anchor="w", padx=10, pady=2)

        # Botón generar cotización
        self.btn_generar = tk.Button(self, text="Generar Cotización", bg="#28a745", fg="white",
                                     font=("Segoe UI", 10, "bold"), activebackground="#1e7e34",
                                     activeforeground="white", relief="flat",
                                     padx=15, pady=8, cursor="hand2", command=self.generar_cotizacion)
        self.btn_generar.pack(pady=10)

    # Función para formatear números como moneda
    def format_currency(self, value):
        try:
            # Convertir a float por seguridad
            value = float(value)
        except:
            return "0"
        # Formatear número con separadores estándar (usando coma como miles)
        formatted = f"{value:,.2f}"
        # Cambiar formato: . → separador de miles, , → separador decimal
        formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        return formatted

    # --- Productos ---
    def render_productos(self):
        for widget in self.frame_productos.winfo_children():
            if int(widget.grid_info()['row']) > 0:
                widget.destroy()

        for i, prod in enumerate(self.productos, start=1):
            # Nombre: Cambiar a Combobox para consultar desde DB
            nombres_productos = [p.get("nombre", "") for p in self.productos_db]
            nombres_servicios = [s.get("numeroHabitacion", "") for s in self.servicios_db]
            nombres_platillos = [pl.get("nombrePlato", "") for pl in self.platillos_db]
            # Combinar todos los nombres (puedes filtrar por tipo si es necesario)
            nombres_combinados = list(set(nombres_productos + nombres_servicios + nombres_platillos))
            combo_nombre = ttk.Combobox(self.frame_productos, textvariable=prod["nombre"], values=nombres_combinados, width=37)
            combo_nombre.grid(row=i, column=0, padx=5, pady=2)
            combo_nombre.bind("<<ComboboxSelected>>", lambda e, p=prod: self.actualizar_precio_desde_db(p))

            # Cantidad
            cantidad_entry = ttk.Entry(self.frame_productos, textvariable=prod["cantidad"], width=10)
            cantidad_entry.grid(row=i, column=1, padx=5, pady=2)
            cantidad_entry.configure(validate="key",
                                     validatecommand=(self.register(self.validar_positivos), "%P"))

            # Precio Unitario con "$" en verde a la izquierda
            frame_precio = tk.Frame(self.frame_productos, bg="#ffffff")
            frame_precio.grid(row=i, column=2, padx=5, pady=2)
            tk.Label(frame_precio, text="$", bg="#ffffff", fg="#28a745", font=("Segoe UI", 10, "bold")).pack(side="left")
            valor_entry = ttk.Entry(frame_precio, textvariable=prod["valorUnitario"], width=30)
            valor_entry.pack(side="left")
            valor_entry.configure(validate="key",
                                  validatecommand=(self.register(self.validar_positivos), "%P"))

            # Precio por Cantidad (calculado automáticamente) con "$" a la izquierda
            frame_total = tk.Frame(self.frame_productos, bg="#ffffff")
            frame_total.grid(row=i, column=3, padx=5, pady=2)
            tk.Label(frame_total, text="$", bg="#ffffff", fg="#28a745", font=("Segoe UI", 10, "bold")).pack(side="left")
            precio_total_label = tk.Label(frame_total, text="0.00", bg="#ffffff", fg="#333333", font=("Segoe UI", 10), width=25, anchor="w")
            precio_total_label.pack(side="left")
            # Usar trace para actualizar automáticamente
            def update_precio_total(*args, label=precio_total_label, prod=prod):
                try:
                    total = prod["cantidad"].get() * prod["valorUnitario"].get()
                    label.config(text=self.format_currency(total))
                    self.actualizar_resumen()
                except:
                    label.config(text="0.00")
            prod["cantidad"].trace_add("write", update_precio_total)
            prod["valorUnitario"].trace_add("write", update_precio_total)
            update_precio_total()  # Inicializar

            # Acción
            btn = tk.Button(self.frame_productos, text="Eliminar", bg="#dc3545", fg="white",
                            font=("Segoe UI", 9, "bold"), activebackground="#c82333",
                            activeforeground="white", relief="flat", padx=5, pady=2, cursor="hand2",
                            command=lambda index=i - 1: self.eliminar_producto(index))
            btn.grid(row=i, column=4, padx=5, pady=2)

        self.actualizar_resumen()

    def actualizar_precio_desde_db(self, prod):
        """Actualiza el precio unitario cuando se selecciona un nombre desde DB"""
        nombre = prod["nombre"].get()
        # Buscar en productos
        for p in self.productos_db:
            if p.get("nombre") == nombre:
                prod["valorUnitario"].set(p.get("precioVenta", 0))
                return
        # Buscar en servicios
        for s in self.servicios_db:
            if s.get("numeroHabitacion") == nombre:
                prod["valorUnitario"].set(s.get("precioHabitacion", 0))  # Asumiendo que servicios tienen "precioHabitacion"
                return
        # Buscar en platillos
        for pl in self.platillos_db:
            if pl.get("nombrePlato") == nombre:
                prod["valorUnitario"].set(pl.get("precioVenta", 0))  # Asumiendo que platillos tienen "precioVenta"
                return
        # Si no se encuentra, dejar en 0

    def add_producto(self):
        self.productos.append({
            "nombre": tk.StringVar(),
            "cantidad": tk.DoubleVar(value=1),
            "valorUnitario": tk.DoubleVar(value=0)
        })
        self.render_productos()

    def eliminar_producto(self, index):
        if len(self.productos) > 1:
            self.productos.pop(index)
            self.render_productos()
        else:
            messagebox.showwarning("Advertencia", "Debe haber al menos un producto en la cotización.")

    # --- Validaciones ---
    def validar_positivos(self, value_if_allowed):
        if value_if_allowed == "":
            return True
        try:
            return float(value_if_allowed) >= 0
        except ValueError:
            return False

    def validar_numeros(self, value_if_allowed):
        return value_if_allowed.isdigit() or value_if_allowed == ""

    def validar_email(self, email):
        """Valida el formato de correo electrónico con mensajes claros"""
        if not email:
            return True  # Campo opcional, no validar si está vacío

        if "@" not in email:
            messagebox.showerror("Error", "El correo electrónico debe contener '@'.")
            return False

        # Separar usuario y dominio
        partes = email.split("@")
        if len(partes) != 2 or not partes[0]:
            messagebox.showerror("Error", "El correo electrónico debe tener texto antes y después de '@'.")
            return False

        dominio = partes[1]
        if "." not in dominio:
            messagebox.showerror("Error", "El correo electrónico debe contener un dominio válido (por ejemplo, '.com', '.co').")
            return False

        if dominio.startswith(".") or dominio.endswith("."):
            messagebox.showerror("Error", "El dominio del correo no puede comenzar o terminar con '.'.")
            return False

        return True

    # --- Resumen ---
    def calcular_subtotal(self):
        return sum(prod["cantidad"].get() * prod["valorUnitario"].get() for prod in self.productos)

    def actualizar_resumen(self):
        subtotal = self.calcular_subtotal()
        total = subtotal  # Para cotizaciones, total = subtotal (sin IVA)
        self.lbl_subtotal.config(text=f"Subtotal: {self.format_currency(subtotal)}")
        self.lbl_total.config(text=f"Total: {self.format_currency(total)}")

    # --- Cargar datos existentes ---
    def cargar_datos(self, documento):
        self.editar_id = documento.get("_id")
        self.tipo_documento = documento.get("tipo", "Cotización")
        for k, v in self.cliente.items():
            v.set(documento["cliente"].get(k, ""))

        self.productos.clear()
        for p in documento.get("productos", []):
            self.productos.append({
                "nombre": tk.StringVar(value=p.get("nombre", "")),
                "cantidad": tk.DoubleVar(value=p.get("cantidad", 1)),
                "valorUnitario": tk.DoubleVar(value=p.get("valorUnitario", 0))
            })
        self.render_productos()
        self.btn_generar.config(text=f"Actualizar {self.tipo_documento}")

    # --- Guardar / Actualizar cotización ---
    def generar_cotizacion(self):
        # Validaciones de campos obligatorios
        for campo, nombre in [
            ("nombre", "El nombre del cliente"),
            ("numeroDocumento", "El número de documento"),
            ("direccion", "La dirección"),
            ("telefono", "El teléfono"),
        ]:
            if not self.cliente[campo].get().strip():
                messagebox.showerror("Error", f"{nombre} es obligatorio.")
                return

        email = self.cliente["email"].get()
        if not self.validar_email(email):
            messagebox.showerror("Error", f"Correo inválido: '{email}'")
            return
        telefono = self.cliente["telefono"].get().strip()
        if not telefono.isdigit():
            messagebox.showerror("Error", "El teléfono solo debe contener números.")
            return
        if len(telefono) != 10:
            messagebox.showerror("Error", "El teléfono debe tener exactamente 10 dígitos.")
            return

        if not self.cliente["numeroDocumento"].get().isdigit():
            messagebox.showerror("Error", "Número de documento inválido")
            return

        for prod in self.productos:
            if not prod["nombre"].get().strip():
                messagebox.showerror("Error", "Todos los productos deben tener un nombre.")
                return
            if prod["cantidad"].get() <= 0:
                messagebox.showerror("Error", "La cantidad debe ser mayor a 0.")
                return
            if prod["valorUnitario"].get() < 0:
                messagebox.showerror("Error", "El precio unitario no puede ser negativo.")
                return

        subtotal = self.calcular_subtotal()
        total = subtotal  # Para cotizaciones, total = subtotal

        cotizacion = {
            "cliente": {k: v.get() for k, v in self.cliente.items()},
            "productos": [{"nombre": p["nombre"].get(), "cantidad": p["cantidad"].get(),
                           "valorUnitario": p["valorUnitario"].get()} for p in self.productos],
            "subtotal": subtotal,
            "total": total
        }

        try:
            if self.editar_id:
                url = f"http://127.0.0.1:5000/cotizaciones/{self.editar_id}"
                r = requests.put(url, json=cotizacion)
                if r.status_code == 200:
                    messagebox.showinfo("Actualizado", f"{self.tipo_documento} actualizada correctamente")
                    if self.refrescar_callback:
                        self.refrescar_callback(False)
                    self.master.destroy()
                else:
                    messagebox.showerror("Error", r.text)
            else:
                url = "http://127.0.0.1:5000/cotizaciones"
                r = requests.post(url, json=cotizacion)
                if r.status_code == 200:
                    messagebox.showinfo("Guardado", f"{self.tipo_documento} guardada con éxito")
                    if self.refrescar_callback:
                        self.refrescar_callback(False)
                    for v in self.cliente.values():
                        v.set("")
                    self.productos.clear()
                    self.add_producto()
                    self.btn_generar.config(text="Generar Cotización")
                else:
                    messagebox.showerror("Error", r.text)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar con el backend:\n{e}")
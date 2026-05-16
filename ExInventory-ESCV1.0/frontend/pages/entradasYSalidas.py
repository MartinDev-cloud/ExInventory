import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from backend.db import categoriasdb, productosdb, serviciosdb, platillosdb, ventasdb
import datetime


class EntradasYSalidas(tk.Frame):
	def __init__(self, parent, controller, *args, **kwargs):
		super().__init__(parent, bg="#f9fafb", *args, **kwargs)
		self.controller = controller
		self.ventas = {"productos": [], "servicios": [], "platillos": []}
		self.items_por_registrar = {"productos": [], "platillos": []}
		
		self.tabs = ttk.Notebook(self)
		self.tabs.pack(fill="both", expand=True, padx=20, pady=(20, 0))
		
		self.tab_info = {
			"productos": {
				"label": "Productos",
				"categoria_var": tk.StringVar(value="Todos"),
				"item_var": tk.StringVar(),
				"cantidad_var": tk.StringVar(),
				"tabla": None
			},
			"servicios": {
				"label": "Servicios",
				"categoria_var": tk.StringVar(value="Todos"),
				"item_var": tk.StringVar(),
				"hora_entrada_var": tk.StringVar(),
				"hora_salida_var": tk.StringVar(),
				"tabla": None
			},
			"platillos": {
				"label": "Platillos",
				"categoria_var": tk.StringVar(value="Todos"),
				"item_var": tk.StringVar(),
				"cantidad_var": tk.StringVar(),
				"tabla": None
			}
		}
		
		for tipo in ("productos", "servicios", "platillos"):
			self._create_tab(tipo)
		
		self.cargar_ventas_desde_db()
		self.auto_refresh()

	def cargar_ventas_desde_db(self):
		"""Carga ventas desde DB evitando duplicación en productos/platillos"""
		for tipo in ("productos", "servicios", "platillos"):
			self.ventas[tipo] = []
			tabla = self.tab_info[tipo]["tabla"]
			for row in tabla.get_children():
				tabla.delete(row)
		
		ventas_db = ventasdb.obtener_ventas()
		
		# Servicios: una fila por venta
		for venta in [v for v in ventas_db if v.get("tipo") == "servicios"]:
			self.ventas["servicios"].append(venta)
			tabla = self.tab_info["servicios"]["tabla"]
			tabla.insert("", "end", values=(
				venta.get("fecha", ""),
				venta.get("categoria", ""),
				venta.get("servicio", ""),
				venta.get("hora_entrada", ""),
				venta.get("hora_salida", "")
			))
		
		# Productos/Platillos: agrupar por fecha
		for tipo in ("productos", "platillos"):
			tabla = self.tab_info[tipo]["tabla"]
			ventas_tipo = [v for v in ventas_db if v.get("tipo") == tipo]
			fechas_procesadas = set()
			
			for venta in ventas_tipo:
				fecha = venta.get("fecha", "")
				if fecha in fechas_procesadas:
					continue
				
				fechas_procesadas.add(fecha)
				self.ventas[tipo].append(venta)
				
				ventas_misma_fecha = [v for v in ventas_tipo if v.get("fecha") == fecha]
				total = sum(float(v.get("subtotal", 0)) for v in ventas_misma_fecha)
				cantidad_total = sum(int(v.get("cantidad", 0)) for v in ventas_misma_fecha)
				
				item_text = f"{'producto' if cantidad_total == 1 else 'productos'}" if tipo == "productos" else f"{'platillo' if cantidad_total == 1 else 'platillos'}"
				
				tabla.insert("", "end", values=(fecha, f"{cantidad_total} {item_text}", f"${total:.2f}"))

	def _create_tab(self, tipo):
		info = self.tab_info[tipo]
		frame = tk.Frame(self.tabs, bg="#f9fafb")
		self.tabs.add(frame, text=info["label"])

		# Campos específicos para servicios
		if tipo == "servicios":
			self._crear_campos_servicio(frame, info)

		# Selector de categoría
		self._crear_selector_categoria(frame, info, tipo)

		# Selector de ítem
		self._crear_selector_item(frame, info, tipo)

		# Campos fecha/hora para servicios o cantidad para productos/platillos
		if tipo == "servicios":
			self._crear_campos_fecha_hora(frame, info)
		else:
			self._crear_campo_cantidad(frame, info)

		# Botones y tablas
		self._crear_botones_y_tablas(frame, info, tipo)

		# Inicializar combos
		self.update_categorias_combo(tipo)
		self.update_items_combo(tipo)

	def _crear_campos_servicio(self, frame, info):
		"""Campos de nombre y celular para servicios"""
		info["nombre_var"] = tk.StringVar()
		info["celular_var"] = tk.StringVar()

		nombre_frame = tk.Frame(frame, bg="#f9fafb")
		nombre_frame.pack(padx=10, pady=(10, 5), anchor="w")
		tk.Label(nombre_frame, text="Nombre:", font=("Arial", 11, "bold"), bg="#f9fafb").pack(side="left")
		tk.Entry(nombre_frame, textvariable=info["nombre_var"], width=30).pack(side="left", padx=8)

		celular_frame = tk.Frame(frame, bg="#f9fafb")
		celular_frame.pack(padx=10, pady=(0, 5), anchor="w")
		tk.Label(celular_frame, text="Celular/Contacto (opcional):", font=("Arial", 11, "bold"), bg="#f9fafb").pack(side="left")
		tk.Entry(celular_frame, textvariable=info["celular_var"], width=30).pack(side="left", padx=8)

	def _crear_selector_categoria(self, frame, info, tipo):
		"""Selector de categoría"""
		categoria_frame = tk.Frame(frame, bg="#f9fafb")
		categoria_frame.pack(padx=10, pady=(10, 5), anchor="w")
		tk.Label(categoria_frame, text="Categoría:", font=("Arial", 11, "bold"), bg="#f9fafb").pack(side="left")
		categoria_combo = ttk.Combobox(categoria_frame, textvariable=info["categoria_var"], state="readonly", width=30)
		categoria_combo.pack(side="left", padx=8)
		categoria_combo.bind("<<ComboboxSelected>>", lambda e, t=tipo: self.update_items_combo(t))

	def _crear_selector_item(self, frame, info, tipo):
		"""Selector de producto/servicio/platillo"""
		item_frame = tk.Frame(frame, bg="#f9fafb")
		item_frame.pack(padx=10, pady=(0, 5), anchor="w")
		
		labels = {"productos": "Producto:", "servicios": "Servicio:", "platillos": "Platillo:"}
		tk.Label(item_frame, text=labels[tipo], font=("Arial", 11, "bold"), bg="#f9fafb").pack(side="left")
		
		item_combo = ttk.Combobox(item_frame, textvariable=info["item_var"], state="readonly", width=40)
		item_combo.pack(side="left", padx=8)
		info["item_combo"] = item_combo

	def _crear_campos_fecha_hora(self, frame, info):
		"""Campos de fecha y hora para servicios"""
		# Variables para hora
		info["hora_entrada_hora_var"] = tk.StringVar()
		info["hora_entrada_min_var"] = tk.StringVar()
		info["hora_entrada_ampm_var"] = tk.StringVar(value="AM")
		info["hora_salida_hora_var"] = tk.StringVar()
		info["hora_salida_min_var"] = tk.StringVar()
		info["hora_salida_ampm_var"] = tk.StringVar(value="AM")

		horas_12 = [f"{h:02d}" for h in range(1, 13)]
		minutos = [f"{m:02d}" for m in range(60)]

		# Estilo para DateEntry
		style = ttk.Style()
		style.configure("Custom.DateEntry", fieldbackground="#f5f5f5", background="#f5f5f5", 
						foreground="black", arrowcolor="black", bordercolor="#d1d5db", 
						lightcolor="#d1d5db", darkcolor="#d1d5db")

		# Entrada
		self._crear_selector_fecha_hora(frame, info, "entrada", horas_12, minutos)
		# Salida
		self._crear_selector_fecha_hora(frame, info, "salida", horas_12, minutos)

		# Actualizar variables completas al cambiar
		def actualizar_fecha_hora_completa(*args):
			for momento in ["entrada", "salida"]:
				h = info[f"hora_{momento}_hora_var"].get()
				m = info[f"hora_{momento}_min_var"].get()
				ampm = info[f"hora_{momento}_ampm_var"].get()
				if h and m and ampm:
					info[f"hora_{momento}_var"].set(f"{h}:{m} {ampm}")

		# Vincular eventos
		for momento in ["entrada", "salida"]:
			for widget in [f"hora_{momento}_hora_combo", f"hora_{momento}_min_combo", f"hora_{momento}_ampm_combo"]:
				info[widget].bind("<<ComboboxSelected>>", actualizar_fecha_hora_completa)
			info[f"fecha_{momento}"].bind("<<DateEntrySelected>>", actualizar_fecha_hora_completa)

	def _crear_selector_fecha_hora(self, frame, info, momento, horas_12, minutos):
		"""Crea selector de fecha y hora (entrada o salida)"""
		selector_frame = tk.Frame(frame, bg="#f9fafb")
		pady = (0, 5) if momento == "entrada" else (0, 10)
		selector_frame.pack(padx=10, pady=pady, anchor="w")
		
		tk.Label(selector_frame, text=f"Fecha de {momento}:", font=("Arial", 11, "bold"), bg="#f9fafb").pack(side="left")
		
		fecha = DateEntry(selector_frame, width=12, style="Custom.DateEntry", locale="es_ES", 
						  date_pattern='yyyy-mm-dd', state="readonly")
		fecha.pack(side="left", padx=8)
		fecha.bind("<FocusIn>", lambda e: self.focus())
		info[f"fecha_{momento}"] = fecha

		tk.Label(selector_frame, text="Hora:", font=("Arial", 11, "bold"), bg="#f9fafb").pack(side="left")

		hora_combo = ttk.Combobox(selector_frame, textvariable=info[f"hora_{momento}_hora_var"], 
								  values=horas_12, state="readonly", width=3)
		hora_combo.pack(side="left", padx=(8, 0))
		info[f"hora_{momento}_hora_combo"] = hora_combo

		tk.Label(selector_frame, text=":", bg="#f9fafb").pack(side="left", padx=(4, 0))

		min_combo = ttk.Combobox(selector_frame, textvariable=info[f"hora_{momento}_min_var"], 
								 values=minutos, state="readonly", width=3)
		min_combo.pack(side="left")
		info[f"hora_{momento}_min_combo"] = min_combo

		ampm_combo = ttk.Combobox(selector_frame, textvariable=info[f"hora_{momento}_ampm_var"], 
								  values=["AM", "PM"], state="readonly", width=3)
		ampm_combo.pack(side="left", padx=(4, 0))
		info[f"hora_{momento}_ampm_combo"] = ampm_combo

	def _crear_campo_cantidad(self, frame, info):
		"""Campo de cantidad para productos/platillos"""
		cantidad_frame = tk.Frame(frame, bg="#f9fafb")
		cantidad_frame.pack(padx=10, pady=(0, 10), anchor="w")
		tk.Label(cantidad_frame, text="Cantidad:", font=("Arial", 11, "bold"), bg="#f9fafb").pack(side="left")
		tk.Entry(cantidad_frame, textvariable=info["cantidad_var"], width=8).pack(side="left", padx=8)

	def _crear_botones_y_tablas(self, frame, info, tipo):
		"""Crea botones y tablas según el tipo"""
		if tipo in ("productos", "platillos","servicios"):
			self._crear_seccion_preregistro(frame, info, tipo)

		# Botón Registrar venta
		registrar_frame = tk.Frame(frame, bg="#f9fafb")
		registrar_frame.pack(fill="x", padx=10, pady=(0, 0))
		tk.Button(registrar_frame, text="Registrar venta", bg="#10b981", fg="white", 
				  font=("Arial", 11, "bold"), padx=12, pady=6, relief="flat", cursor="hand2", 
				  command=lambda t=tipo: self.registrar_venta(t)).pack(side="left")

		# Tabla de ventas registradas
		self._crear_tabla_ventas(frame, info, tipo)

	def _crear_seccion_preregistro(self, frame, info, tipo):
		"""Sección de items por registrar para productos/platillos/servicios"""
		buttons_frame = tk.Frame(frame, bg="#f9fafb")
		buttons_frame.pack(fill="x", padx=10, pady=(0, 10))
		
		if tipo != "servicios":
			# Botón de "Agregar a lista" solo para productos/platillos
			tk.Button(
				buttons_frame, text="Agregar a lista", bg="#10b981", fg="white", 
				font=("Arial", 11, "bold"), padx=12, pady=6, relief="flat", cursor="hand2", 
				command=lambda t=tipo: self.agregar_a_lista(t)
			).pack(side="left", padx=(0, 10))

		# Botón de "Cómo eliminar" siempre
		def mostrar_info_eliminar():
			if tipo == "productos":
				mensaje = "Para eliminar un producto o una lista de productos registrados, selecciónala y haz click derecho."
			elif tipo == "platillos":
				mensaje = "Para eliminar un platillo o una lista de platillos registrados, selecciónala y haz click derecho."
			else:  # servicios
				mensaje = "Para eliminar un servicio registrado, selecciónalo y haz click derecho."
			messagebox.showinfo("Eliminar items", mensaje)

		tk.Button(
			buttons_frame, text="ⓘ ¿Cómo eliminar?", font=("Arial", 10), bg="#f1f5f9",
			fg="#2563eb", relief="flat", cursor="hand2",
			command=mostrar_info_eliminar
		).pack(side="right", padx=(10, 0))

		# Solo crear tabla y total si no es servicios
		if tipo != "servicios":
			# Tabla de items por registrar
			pre_tabla_frame = tk.Frame(frame, bg="#f9fafb")
			pre_tabla_frame.pack(fill="x", padx=10, pady=(0, 10))
			tk.Label(pre_tabla_frame, text="por registrar:", font=("Arial", 11, "bold"), bg="#f9fafb").pack(anchor="w", pady=(0, 5))

			columns = ("categoria", "item", "cantidad", "precio_unitario", "subtotal")
			pre_tabla = ttk.Treeview(pre_tabla_frame, columns=columns, show="headings", height=5)
			pre_tabla.heading("categoria", text="Categoría")
			pre_tabla.heading("item", text="Producto" if tipo == "productos" else "Platillo")
			pre_tabla.heading("cantidad", text="Cantidad")
			pre_tabla.heading("precio_unitario", text="Precio Unit.")
			pre_tabla.heading("subtotal", text="Subtotal")
			for col in columns:
				pre_tabla.column(col, anchor="center", width=100)
			pre_tabla.pack(fill="x")

			# Menú contextual para eliminar
			pre_tabla.bind("<Button-3>", lambda e: self._mostrar_menu_preregistro(e, pre_tabla, tipo))
			pre_tabla.bind("<Button-1>", lambda e: pre_tabla.selection_set(pre_tabla.identify_row(e.y)))

			# Total
			total_frame = tk.Frame(frame, bg="#f9fafb")
			total_frame.pack(fill="x", padx=10, pady=(0, 10))
			total_label = tk.Label(total_frame, text="Total: $0.00", font=("Arial", 11, "bold"), bg="#f9fafb")
			total_label.pack(side="right")
			
			info[f"pre_tabla_{tipo}"] = pre_tabla
			info[f"total_label_{tipo}"] = total_label

	def _mostrar_menu_preregistro(self, event, pre_tabla, tipo):
		"""Menú contextual para quitar items de la lista de preregistro"""
		item_id = pre_tabla.identify_row(event.y)
		if item_id:
			menu = tk.Menu(pre_tabla, tearoff=0)
			menu.add_command(label="Quitar de la lista", command=lambda: self.quitar_de_lista(tipo, item_id))
			menu.tk_popup(event.x_root, event.y_root)

	def _crear_tabla_ventas(self, frame, info, tipo):
		"""Tabla de ventas registradas"""
		tabla_frame = tk.Frame(frame, bg="#f9fafb")
		tabla_frame.pack(fill="both", expand=True, padx=10, pady=(10, 10))
		
		if tipo == "servicios":
			columns = ("fecha", "categoria", "servicio", "hora_entrada", "hora_salida")
			headings = {
				"fecha": "Fecha/Hora de registro",
				"categoria": "Categoría",
				"servicio": "Servicio",
				"hora_entrada": "fecha de entrada",
				"hora_salida": "fecha de salida"
			}
		else:
			columns = ("fecha", "num_items", "precio_total")
			item_label = "Numero de productos" if tipo == "productos" else "Número de platillos"
			headings = {
				"fecha": "Fecha/Hora de registro",
				"num_items": item_label,
				"precio_total": "Total"
			}
		
		tabla = ttk.Treeview(tabla_frame, columns=columns, show="headings", height=10)
		for col in columns:
			tabla.heading(col, text=headings[col])
			tabla.column(col, anchor="center", width=120)
		tabla.pack(fill="both", expand=True)
		info["tabla"] = tabla

		# Menú contextual
		tabla.bind("<Button-3>", lambda e: self._mostrar_menu_venta(e, tabla, tipo))
		tabla.bind("<Button-1>", lambda e: tabla.selection_set(tabla.identify_row(e.y)))

	def _mostrar_menu_venta(self, event, tabla, tipo):
		"""Menú contextual para ver detalles o eliminar venta"""
		item_id = tabla.identify_row(event.y)
		if item_id:
			menu = tk.Menu(tabla, tearoff=0)
			if tipo == "servicios":
				menu.add_command(label="Más información", command=lambda: self.mostrar_detalles_servicio(tipo, item_id))
			else:
				menu.add_command(label="Más información", command=lambda: self.mostrar_detalles_venta(tipo, item_id))
			menu.add_command(label="Eliminar venta", command=lambda: self.eliminar_venta(tipo, item_id))
			menu.tk_popup(event.x_root, event.y_root)

	def auto_refresh(self):
		"""Actualiza combos cada 5 segundos"""
		for tipo in ("productos", "servicios", "platillos"):
			self.update_items_combo(tipo)
		self.after(5000, self.auto_refresh)

	def update_categorias_combo(self, tipo):
		"""Actualiza el combo de categorías"""
		info = self.tab_info[tipo]
		categorias = categoriasdb.obtener_categorias(tipo)
		info["categoria_var"].set(categorias[0] if categorias else "Todos")
		
		for child in self.tabs.nametowidget(self.tabs.tabs()[["productos", "servicios", "platillos"].index(tipo)]).winfo_children():
			if isinstance(child, tk.Frame):
				for subchild in child.winfo_children():
					if isinstance(subchild, ttk.Combobox) and subchild.cget("textvariable") == str(info["categoria_var"]):
						subchild["values"] = categorias
						break

	def update_items_combo(self, tipo):
		"""Actualiza el combo de items según categoría"""
		info = self.tab_info[tipo]
		categoria = info["categoria_var"].get()
		
		# Obtener items según tipo
		db_config = {
			"productos": (productosdb.obtener_productos, "nombre"),
			"servicios": (serviciosdb.obtener_servicios, "numeroHabitacion"),
			"platillos": (platillosdb.obtener_platillos, "nombrePlato")
		}
		obtener_func, nombre_campo = db_config[tipo]
		items = obtener_func()
		
		if categoria != "Todos":
			items = [i for i in items if i.get("categoria") == categoria]
		
		nombres = [i.get(nombre_campo, "") for i in items]
		info["item_combo"]["values"] = nombres
		info["item_var"].set(nombres[0] if nombres else "")
		
		# Mostrar stock solo para productos
		if tipo == "productos":
			self.mostrar_stock_producto(info)
			info["item_combo"].bind("<<ComboboxSelected>>", lambda e: self.mostrar_stock_producto(info))

	def mostrar_stock_producto(self, info):
		"""Muestra el stock disponible del producto seleccionado"""
		nombre = info["item_var"].get()
		if not hasattr(self, "stock_label"):
			self.stock_label = tk.Label(info["item_combo"].master, text="", font=("Arial", 10, "bold"), 
										 bg="#f9fafb", fg="#2563eb")
			self.stock_label.pack(side="left", padx=10)
		
		if nombre:
			productos = productosdb.obtener_productos({"nombre": nombre})
			stock = productos[0].get("stockActual", "?") if productos else "?"
			self.stock_label.config(text=f"Stock disponible: {stock}")
		else:
			self.stock_label.config(text="")

	def agregar_a_lista(self, tipo):
		"""Agrega un item a la lista de preregistro"""
		info = self.tab_info[tipo]
		categoria = info["categoria_var"].get()
		item_nombre = info["item_var"].get()
		cantidad = info["cantidad_var"].get()
		
		# Validar entrada
		if not item_nombre or not cantidad.isdigit() or int(cantidad) <= 0:
			messagebox.showwarning("Datos incompletos", 
				f"Selecciona un {'producto' if tipo == 'productos' else 'platillo'} y una cantidad válida.")
			return
		
		cantidad = int(cantidad)
		
		# Obtener datos del item
		db_config = {
			"productos": (productosdb.obtener_productos, {"nombre": item_nombre}, "stockActual"),
			"platillos": (platillosdb.obtener_platillos, {"nombrePlato": item_nombre}, None)
		}
		obtener_func, filtro, stock_field = db_config[tipo]
		items = obtener_func(filtro)
		
		if not items:
			messagebox.showwarning("Error", f"{'Producto' if tipo == 'productos' else 'Platillo'} no encontrado")
			return
		
		item = items[0]
		
		# Validar precio de venta
		if "precioVenta" not in item or not str(item["precioVenta"]).replace(".", "").isdigit():
			messagebox.showwarning("Error", f"El {'producto' if tipo == 'productos' else 'platillo'} no tiene un precio de venta válido")
			return
		
		precio = float(item["precioVenta"])
		
		# Validar stock solo para productos
		if tipo == "productos":
			stock = int(item.get(stock_field, 0))
			if cantidad > stock:
				messagebox.showwarning("Stock insuficiente", f"No hay suficiente stock disponible. Stock actual: {stock}")
				return
		
		# Agregar a la tabla de preregistro
		subtotal = precio * cantidad
		pre_tabla = info[f"pre_tabla_{tipo}"]
		pre_tabla.insert("", "end", values=(categoria, item_nombre, cantidad, f"${precio:.2f}", f"${subtotal:.2f}"))
		
		# Actualizar total
		total = sum(float(pre_tabla.item(item)["values"][4].replace("$", "")) for item in pre_tabla.get_children())
		info[f"total_label_{tipo}"].config(text=f"Total: ${total:.2f}")
		
		# Guardar en lista temporal
		self.items_por_registrar[tipo].append({
			"categoria": categoria,
			"item": item_nombre,
			"cantidad": cantidad,
			"precio": precio,
			"subtotal": subtotal
		})
		
		info["cantidad_var"].set("")

	def registrar_venta(self, tipo):
		"""Registra la venta en la base de datos"""
		info = self.tab_info[tipo]
		fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		
		if tipo in ("productos", "platillos"):
			self._registrar_venta_items(tipo, info, fecha)
		elif tipo == "servicios":
			self._registrar_venta_servicio(tipo, info, fecha)

	def _registrar_venta_items(self, tipo, info, fecha):
		"""Registra venta de productos o platillos"""
		if not self.items_por_registrar[tipo]:
			messagebox.showwarning("Lista vacía", "Agrega items a la lista antes de registrar la venta")
			return
		
		total = sum(item["subtotal"] for item in self.items_por_registrar[tipo])
		
		# Registrar cada item
		for item in self.items_por_registrar[tipo]:
			venta = {
				"fecha": fecha,
				"tipo": tipo,
				"categoria": item["categoria"],
				"producto" if tipo == "productos" else "platillo": item["item"],
				"cantidad": item["cantidad"],
				"precio": item["precio"],
				"subtotal": item["subtotal"]
			}
			self.ventas[tipo].append(venta)
			
			if tipo == "productos":
				productosdb.actualizar_stock_por_nombre(item["item"], str(item["cantidad"]))
			
			ventasdb.registrar_venta(venta)
		
		# Agregar a tabla visual
		cantidad_total = sum(item["cantidad"] for item in self.items_por_registrar[tipo])
		item_text = f"{'producto' if cantidad_total == 1 else 'productos'}" if tipo == "productos" else f"{'platillo' if cantidad_total == 1 else 'platillos'}"
		info["tabla"].insert("", "end", values=(fecha, f"{cantidad_total} {item_text}", f"${total:.2f}"))
		
		# Limpiar preregistro
		pre_tabla = info[f"pre_tabla_{tipo}"]
		for item in pre_tabla.get_children():
			pre_tabla.delete(item)
		info[f"total_label_{tipo}"].config(text="Total: $0.00")
		self.items_por_registrar[tipo].clear()
		
		if tipo == "productos":
			self.mostrar_stock_producto(info)

	def _registrar_venta_servicio(self, tipo, info, fecha):
		"""Registra venta de servicio"""
		# Validar campos requeridos
		h_ent = info['hora_entrada_hora_var'].get()
		m_ent = info['hora_entrada_min_var'].get()
		ampm_ent = info['hora_entrada_ampm_var'].get()
		h_sal = info['hora_salida_hora_var'].get()
		m_sal = info['hora_salida_min_var'].get()
		ampm_sal = info['hora_salida_ampm_var'].get()
		item = info["item_var"].get()
		nombre = info["nombre_var"].get()
		
		if not all([h_ent, m_ent, ampm_ent, h_sal, m_sal, ampm_sal]):
			messagebox.showwarning("Datos incompletos", "Debes seleccionar hora y minutos de entrada y salida (AM/PM).")
			return
		
		if not item:
			messagebox.showwarning("Datos incompletos", "Selecciona un servicio antes de registrar la venta.")
			return
		
		if not nombre:
			messagebox.showwarning("Datos incompletos", "Debes ingresar el nombre del cliente.")
			return
		
		# Construir fechas completas
		fecha_entrada = info["fecha_entrada"].get_date()
		fecha_salida = info["fecha_salida"].get_date()
		hora_entrada = f"{h_ent}:{m_ent} {ampm_ent}"
		hora_salida = f"{h_sal}:{m_sal} {ampm_sal}"
		entrada_completa = f"{fecha_entrada.strftime('%Y-%m-%d')} : {hora_entrada}"
		salida_completa = f"{fecha_salida.strftime('%Y-%m-%d')} : {hora_salida}"
		
		venta = {
			"fecha": fecha,
			"tipo": tipo,
			"categoria": info["categoria_var"].get(),
			"servicio": item,
			"hora_entrada": entrada_completa,
			"hora_salida": salida_completa,
			"nombre": nombre,
			"contacto": info["celular_var"].get()
		}
		
		self.ventas[tipo].append(venta)
		info["tabla"].insert("", "end", values=(venta["fecha"], venta["categoria"], venta["servicio"], 
												venta["hora_entrada"], venta["hora_salida"]))
		
		try:
			ventasdb.registrar_venta(venta)
		except Exception as e:
			messagebox.showerror("Error BD", f"No se pudo registrar la venta en la base de datos:\n{e}")
			return
		
		# Limpiar campos
		info["hora_entrada_hora_var"].set("")
		info["hora_entrada_min_var"].set("")
		info["hora_entrada_ampm_var"].set("AM")
		info["hora_salida_hora_var"].set("")
		info["hora_salida_min_var"].set("")
		info["hora_salida_ampm_var"].set("AM")
		info["nombre_var"].set("")
		info["celular_var"].set("")

	def quitar_de_lista(self, tipo, item_id):
		"""Quita un item de la lista de preregistro"""
		info = self.tab_info[tipo]
		pre_tabla = info[f"pre_tabla_{tipo}"]
		
		values = pre_tabla.item(item_id)["values"]
		if not values:
			return
		
		pre_tabla.delete(item_id)
		
		# Remover de la lista temporal
		item_nombre = values[1]
		self.items_por_registrar[tipo] = [item for item in self.items_por_registrar[tipo] if item["item"] != item_nombre]
		
		# Recalcular total
		total = sum(item["subtotal"] for item in self.items_por_registrar[tipo])
		info[f"total_label_{tipo}"].config(text=f"Total: ${total:.2f}")
		
		if tipo == "productos":
			self.mostrar_stock_producto(info)

	def mostrar_detalles_venta(self, tipo, item_id):
		"""Muestra detalles de una venta de productos/platillos"""
		info = self.tab_info[tipo]
		tabla = info["tabla"]
		values = tabla.item(item_id)["values"]
		if not values:
			return
		
		fecha = values[0]
		ventas_db = ventasdb.obtener_ventas({"fecha": fecha, "tipo": tipo})
		if not ventas_db:
			messagebox.showwarning("Error", "No se encontraron detalles de esta venta")
			return
		
		# Crear ventana emergente
		ventana = tk.Toplevel(self)
		ventana.title("Detalles de la venta")
		ventana.geometry("800x500")
		ventana.configure(bg="#f9fafb")
		
		container_frame = tk.Frame(ventana, bg="#f9fafb")
		container_frame.pack(fill="both", expand=True, padx=20, pady=20)
		
		main_frame = tk.Frame(container_frame, bg="#f9fafb")
		main_frame.pack(fill="both", expand=True)
		
		# Información general
		tk.Label(main_frame, text="Detalles de la venta", font=("Arial", 14, "bold"), bg="#f9fafb").pack(anchor="w", pady=(0, 20))
		tk.Label(main_frame, text=f"Fecha/hora de registro: {fecha}", font=("Arial", 11), bg="#f9fafb").pack(anchor="w")
		
		total = sum(float(venta.get("subtotal", 0)) for venta in ventas_db)
		tk.Label(main_frame, text=f"Total de la venta: ${total:.2f}", font=("Arial", 11, "bold"), bg="#f9fafb").pack(anchor="w", pady=(0, 20))
		tk.Label(main_frame, text="vendidos:", font=("Arial", 11, "bold"), bg="#f9fafb").pack(anchor="w", pady=(0, 10))
		
		# Tabla de items
		columns = ("categoria", "item", "cantidad", "precio_unitario", "subtotal")
		tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=10)
		tree.heading("categoria", text="Categoría")
		tree.heading("item", text="Producto" if tipo == "productos" else "Platillo")
		tree.heading("cantidad", text="Cantidad")
		tree.heading("precio_unitario", text="Precio Unit.")
		tree.heading("subtotal", text="Subtotal")
		
		for col in columns:
			tree.column(col, anchor="center", width=100)
		
		scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
		tree.configure(yscrollcommand=scrollbar.set)
		tree.pack(side="left", fill="both", expand=True)
		scrollbar.pack(side="right", fill="y")
		
		# Insertar items
		for venta in ventas_db:
			item_nombre = venta.get("producto" if tipo == "productos" else "platillo", "")
			tree.insert("", "end", values=(
				venta.get("categoria", ""),
				item_nombre,
				venta.get("cantidad", 0),
				f"${float(venta.get('precio', 0)):.2f}",
				f"${float(venta.get('subtotal', 0)):.2f}"
			))
		
		# Botón cerrar
		button_frame = tk.Frame(container_frame, bg="#f9fafb")
		button_frame.pack(fill="x", pady=(20, 0))
		tk.Button(button_frame, text="Cerrar", font=("Arial", 11), command=ventana.destroy, 
				  bg="#ef4444", fg="white", padx=20, pady=5).pack()
		
		ventana.transient(self)
		ventana.grab_set()

	def mostrar_detalles_servicio(self, tipo, item_id):
		"""Muestra y permite editar detalles de un servicio"""
		info = self.tab_info[tipo]
		tabla = info["tabla"]
		values = tabla.item(item_id)["values"]
		if not values:
			return
		
		fecha = values[0]
		ventas_db = ventasdb.obtener_ventas({"fecha": fecha, "tipo": tipo})
		if not ventas_db:
			messagebox.showwarning("Error", "No se encontraron detalles de este servicio")
			return
		
		venta = ventas_db[0]
		
		ventana = tk.Toplevel(self)
		ventana.title("Detalles del Servicio")
		ventana.geometry("500x400")
		ventana.configure(bg="#f9fafb")
		
		main_frame = tk.Frame(ventana, bg="#f9fafb")
		main_frame.pack(fill="both", expand=True, padx=20, pady=20)
		
		tk.Label(main_frame, text="Detalles del Servicio", font=("Arial", 14, "bold"), bg="#f9fafb").pack(anchor="w", pady=(0, 20))
		
		# Parsear fechas existentes
		try:
			from datetime import datetime
			hora_entrada_str = venta.get("hora_entrada", "")
			hora_salida_str = venta.get("hora_salida", "")
			
			fecha_entrada_str = hora_entrada_str.split(" : ")[0] if " : " in hora_entrada_str else ""
			hora_ent = hora_entrada_str.split(" : ")[1] if " : " in hora_entrada_str else ""
			fecha_salida_str = hora_salida_str.split(" : ")[0] if " : " in hora_salida_str else ""
			hora_sal = hora_salida_str.split(" : ")[1] if " : " in hora_salida_str else ""
			
			fecha_entrada_obj = datetime.strptime(fecha_entrada_str, "%Y-%m-%d") if fecha_entrada_str else datetime.now()
			fecha_salida_obj = datetime.strptime(fecha_salida_str, "%Y-%m-%d") if fecha_salida_str else datetime.now()
		except:
			fecha_entrada_obj = datetime.now()
			fecha_salida_obj = datetime.now()
			hora_ent = ""
			hora_sal = ""
		
		hora_entrada_var = tk.StringVar(value=hora_ent)
		hora_salida_var = tk.StringVar(value=hora_sal)
		
		# Información detallada
		detalles = [
			("Nombre del cliente:", venta.get("nombre", "No disponible")),
			("Contacto:", venta.get("contacto", "No disponible")),
			("Fecha de registro:", venta.get("fecha", "No disponible")),
			("Categoría:", venta.get("categoria", "No disponible")),
			("Servicio:", venta.get("servicio", "No disponible"))
		]
		
		for label, valor in detalles:
			frame = tk.Frame(main_frame, bg="#f9fafb")
			frame.pack(fill="x", pady=5)
			tk.Label(frame, text=label, font=("Arial", 11, "bold"), bg="#f9fafb").pack(side="left")
			tk.Label(frame, text=valor, font=("Arial", 11), bg="#f9fafb").pack(side="left", padx=(10, 0))
		
		# Fecha/hora de entrada
		entrada_frame = tk.Frame(main_frame, bg="#f9fafb")
		entrada_frame.pack(fill="x", pady=5)
		tk.Label(entrada_frame, text="Fecha de entrada:", font=("Arial", 11, "bold"), bg="#f9fafb").pack(side="left")
		fecha_entrada = DateEntry(entrada_frame, width=12, locale="es_ES", date_pattern="yyyy-mm-dd",
								   year=fecha_entrada_obj.year, month=fecha_entrada_obj.month, day=fecha_entrada_obj.day)
		fecha_entrada.pack(side="left", padx=(10, 5))
		tk.Label(entrada_frame, text="Hora:", font=("Arial", 11, "bold"), bg="#f9fafb").pack(side="left", padx=(5, 0))
		tk.Entry(entrada_frame, textvariable=hora_entrada_var, width=15).pack(side="left", padx=5)
		
		# Fecha/hora de salida
		salida_frame = tk.Frame(main_frame, bg="#f9fafb")
		salida_frame.pack(fill="x", pady=5)
		tk.Label(salida_frame, text="Fecha de salida:", font=("Arial", 11, "bold"), bg="#f9fafb").pack(side="left")
		fecha_salida = DateEntry(salida_frame, width=12, locale="es_ES", date_pattern="yyyy-mm-dd",
								  year=fecha_salida_obj.year, month=fecha_salida_obj.month, day=fecha_salida_obj.day)
		fecha_salida.pack(side="left", padx=(10, 5))
		tk.Label(salida_frame, text="Hora:", font=("Arial", 11, "bold"), bg="#f9fafb").pack(side="left", padx=(5, 0))
		tk.Entry(salida_frame, textvariable=hora_salida_var, width=15).pack(side="left", padx=5)
		
		def actualizar_fechas():
			"""Actualiza las fechas del servicio en DB"""
			try:
				if not hora_entrada_var.get() or not hora_salida_var.get():
					messagebox.showwarning("Datos incompletos", "Por favor, ingresa tanto la hora de entrada como la de salida")
					return
				
				# Validar formato AM/PM
				for hora in [hora_entrada_var.get(), hora_salida_var.get()]:
					if not (" AM" in hora.upper() or " PM" in hora.upper()):
						messagebox.showwarning("Formato incorrecto", "Las horas deben estar en formato '12:00 AM/PM'")
						return
				
				nueva_entrada = f"{fecha_entrada.get_date().strftime('%Y-%m-%d')} : {hora_entrada_var.get()}"
				nueva_salida = f"{fecha_salida.get_date().strftime('%Y-%m-%d')} : {hora_salida_var.get()}"
				
				venta_actualizada = venta.copy()
				venta_actualizada["hora_entrada"] = nueva_entrada
				venta_actualizada["hora_salida"] = nueva_salida
				
				# Actualizar en DB
				if ventasdb.actualizar_venta(venta["_id"], venta_actualizada):
					# Actualizar en tabla visual
					tabla.set(item_id, "hora_entrada", nueva_entrada)
					tabla.set(item_id, "hora_salida", nueva_salida)
					
					# Actualizar en lista local
					for v in self.ventas[tipo]:
						if v.get("_id") == venta["_id"]:
							v["hora_entrada"] = nueva_entrada
							v["hora_salida"] = nueva_salida
							break
					
					messagebox.showinfo("Éxito", "Las fechas se han actualizado correctamente")
					ventana.destroy()
				else:
					messagebox.showerror("Error", "No se pudo actualizar la venta en la base de datos")
			except Exception as e:
				messagebox.showerror("Error", f"No se pudieron actualizar las fechas: {str(e)}")
		
		# Botones
		botones_frame = tk.Frame(main_frame, bg="#f9fafb")
		botones_frame.pack(fill="x", pady=20)
		tk.Button(botones_frame, text="Actualizar fechas", font=("Arial", 11), command=actualizar_fechas, 
				  bg="#10b981", fg="white", padx=20, pady=5).pack(side="left", padx=(0, 10))
		tk.Button(botones_frame, text="Cerrar", font=("Arial", 11), command=ventana.destroy, 
				  bg="#ef4444", fg="white", padx=20, pady=5).pack(side="left")
		
		ventana.transient(self)
		ventana.grab_set()

	def eliminar_venta(self, tipo, item_id):
		"""Elimina una venta de la base de datos y la tabla"""
		info = self.tab_info[tipo]
		tabla = info["tabla"]
		values = tabla.item(item_id, "values")
		if not values:
			return
		
		if not messagebox.askyesno("Eliminar venta", "¿Seguro que deseas eliminar esta venta?"):
			return
		
		fecha = values[0]
		
		# Remover de lista local
		venta = next((v for v in self.ventas[tipo] if v["fecha"] == fecha), None)
		if venta:
			self.ventas[tipo].remove(venta)
		
		tabla.delete(item_id)
		
		# Eliminar de la base de datos (todas las ventas con esa fecha y tipo)
		ventas_db = ventasdb.obtener_ventas({"fecha": fecha, "tipo": tipo})
		for venta_db in ventas_db:
			if "_id" in venta_db:
				ventasdb.eliminar_venta(venta_db["_id"])
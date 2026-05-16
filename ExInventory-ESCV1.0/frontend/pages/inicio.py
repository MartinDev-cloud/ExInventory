import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from backend.db.productosdb import obtener_productos
from backend.db.ventasdb import obtener_ventas
from backend.main_documentos import obtener_facturas
import seaborn as sns

sns.set_style("whitegrid")


def format_currency(value):
    """Formatea el valor en pesos:
       - Para millones: 1'234.567,90
       - Para menos de un millón: 123.456,78
    """
    integer_part = int(value)
    decimal_part = int(round((value - integer_part) * 100))

    if value >= 1_000_000:
        millones = integer_part // 1_000_000
        resto = integer_part % 1_000_000
        resto_str = f"{resto:,}".replace(",", ".")
        if decimal_part > 0:
            return f"${millones}'{resto_str},{decimal_part:02d}"
        else:
            return f"${millones}'{resto_str}"
    else:
        integer_str = f"{integer_part:,}".replace(",", ".")
        if decimal_part > 0:
            return f"${integer_str},{decimal_part:02d}"
        else:
            return f"${integer_str}"


class Info(tk.Frame):
    def __init__(self, parent, title, content, bgColor="#007bff", big_number=False, width=250, height=100):
        super().__init__(parent, bg=bgColor, bd=0, relief="flat", width=width, height=height)
        self.configure(padx=10, pady=10)
        self.big_number = big_number

        self.base_font_family = "Segoe UI"
        self.base_font_weight = "bold"

        self.grid_propagate(False)
        self.pack_propagate(False)

        self.title_label = tk.Label(self, text=title, font=(self.base_font_family, 12, "bold"), fg="white", bg=bgColor)
        self.title_label.pack(anchor="w")

        justify_mode = "center" if big_number else "left"
        self.content_label = tk.Label(
            self, text=content, font=(self.base_font_family, 10, "bold"),
            fg="white", bg=bgColor, justify=justify_mode, wraplength=width-20
        )
        self.content_label.pack(fill="both", expand=True)

        if self.big_number:
            self.bind("<Configure>", self._adjust_font_to_fit)

    def _adjust_font_to_fit(self, event=None):
        text = self.content_label.cget("text")
        if not text:
            return

        max_width = self.winfo_width() - 10
        max_height = self.winfo_height() - 10

        font_size = 16
        temp = tk.Label(self, text=text, font=(self.base_font_family, font_size, self.base_font_weight))
        temp.update_idletasks()
        text_width = temp.winfo_reqwidth()
        text_height = temp.winfo_reqheight()

        while (text_width > max_width or text_height > max_height) and font_size > 1:
            font_size -= 1
            temp.config(font=(self.base_font_family, font_size, self.base_font_weight))
            temp.update_idletasks()
            text_width = temp.winfo_reqwidth()
            text_height = temp.winfo_reqheight()

        while text_width < max_width and text_height < max_height:
            font_size += 1
            temp.config(font=(self.base_font_family, font_size, self.base_font_weight))
            temp.update_idletasks()
            text_width = temp.winfo_reqwidth()
            text_height = temp.winfo_reqheight()

        font_size -= 1
        self.content_label.config(
            font=(self.base_font_family, font_size, self.base_font_weight),
            wraplength=self.winfo_width()
        )
        temp.destroy()


class Inicio(tk.Frame):
    def __init__(self, parent, controller, inventory_api_url='http://localhost:8000'):
        super().__init__(parent, bg="#f5f7fa")
        self.controller = controller
        self.inventory_api_url = inventory_api_url
        self.info_labels = {}
        self.last_data = None
        self._destroyed = False
        self.chart_widgets = {}
        self.daily_sales_value = 0

        body = tk.Frame(self, bg="#f5f7fa")
        body.pack(fill="both", expand=True)
        dashboard_grid = tk.Frame(body, bg="#f5f7fa")
        dashboard_grid.pack(fill="both", expand=True, padx=20, pady=20)

        self.info1 = Info(dashboard_grid, "Total de Ventas del Día", "Sin registros", "#28a745", big_number=True, width=250, height=120)
        self.info_labels['dailySales'] = self.info1.content_label
        self.info1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.info2 = Info(dashboard_grid, "Top 3 Más Vendidos", "Sin registros", "#007bff")
        self.info_labels['topProducts'] = self.info2.content_label
        self.info2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.info3 = Info(dashboard_grid, "Bajo en Inventario", "Sin datos que mostrar", "#dc3545")
        self.info_labels['lowInventory'] = self.info3.content_label
        self.info3.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        self.info4 = Info(dashboard_grid, "Facturas Generadas", "Sin registros", "#ffc107")
        self.info_labels['generatedInvoices'] = self.info4.content_label
        self.info4.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        tk.Button(dashboard_grid, text="Inventarios", bg="#0039e6", fg="white",
                  font=("Segoe UI", 12, "bold"), bd=0, relief="raised",
                  command=lambda: controller.show_page("Inventarios")).grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        tk.Button(dashboard_grid, text="Documentos", bg="#ff6600", fg="white",
                  font=("Segoe UI", 12, "bold"), bd=0, relief="raised",
                  command=lambda: controller.show_page("Documentos")).grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

        self.chart_frame = tk.Frame(dashboard_grid, bg="#f5f7fa")
        self.chart_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=20)

        for i in range(3):
            dashboard_grid.grid_rowconfigure(i, weight=1)
        for j in range(3):
            dashboard_grid.grid_columnconfigure(j, weight=1)

        self.bind("<Destroy>", self._on_destroy)
        self._start_auto_refresh()

    def _on_destroy(self, event):
        self._destroyed = True

    def _start_auto_refresh(self):
        if self._destroyed:
            return
        try:
            data = self.fetch_dashboard_data()
            self._update_labels(data)
        except Exception as e:
            print("Error refrescando datos:", e)
        self.after(5000, self._start_auto_refresh)

    def _update_labels(self, data):
        self.info_labels['dailySales'].config(text=data.get("dailySales") or "Sin registros")
        self.daily_sales_value = self.parse_currency_to_float(data.get("dailySales"))

        self.info_labels['topProducts'].config(
            text="\n".join(data.get("topProducts", [])) if data.get("topProducts") else "Sin registros"
        )
        self.info_labels['lowInventory'].config(
            text="\n".join([f"{p['name']}: {p['stock']} unidades" for p in data.get("lowInventory", [])])
            if data.get("lowInventory") else "¡Muy bien! No tienes productos bajos en stock o sin reponer"
        )

        facturas_info = []
        try:
            facturas = obtener_facturas(limit=3)
            for factura in facturas:
                cliente = factura.get("cliente", {})
                nombre_cliente = cliente.get("nombre", "Sin nombre")
                productos = factura.get("productos", [])
                cantidad_total = sum(int(p.get("cantidad", 0)) for p in productos) if productos else 1
                total_factura = float(factura.get("total", factura.get("subtotal", 0)))
                facturas_info.append(f"{nombre_cliente} - {cantidad_total} items {format_currency(total_factura)}")
        except Exception as e:
            print(f"Error cargando facturas: {e}")

        self.info_labels['generatedInvoices'].config(
            text="\n".join(facturas_info) if facturas_info else "No has registrado ninguna factura",
            justify="left",
            wraplength=250
        )

        if data != self.last_data:
            self._update_charts(data)
            self.last_data = data

    def fetch_dashboard_data(self):
        try:
            hoy_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            hoy_fin = hoy_inicio + timedelta(days=1)
            ventas_hoy = obtener_ventas({
                "fecha": {
                    "$gte": hoy_inicio.strftime("%Y-%m-%d %H:%M:%S"),
                    "$lt": hoy_fin.strftime("%Y-%m-%d %H:%M:%S")
                }
            })

            daily_sales = 0
            items_count = {}
            categorias_count = {"Productos": {}, "Platillos": {}, "Servicios": {}}

            for venta in ventas_hoy:
                tipo = venta.get("tipo", "")
                if tipo == "productos":
                    nombre = venta.get("producto", "")
                    cantidad = int(venta.get("cantidad", 0))
                    subtotal = float(venta.get("subtotal", 0))
                    categoria = "Productos"
                elif tipo == "platillos":
                    nombre = venta.get("platillo", "")
                    cantidad = int(venta.get("cantidad", 0))
                    subtotal = float(venta.get("subtotal", 0))
                    categoria = "Platillos"
                elif tipo == "servicios":
                    nombre = f"Servicio {venta.get('servicio', '')}"
                    cantidad = 1
                    subtotal = float(venta.get("precio", 0))
                    categoria = "Servicios"
                else:
                    continue

                daily_sales += subtotal

                if nombre:
                    items_count.setdefault(nombre, {"cantidad": 0, "subtotal": 0, "categoria": categoria})
                    items_count[nombre]["cantidad"] += cantidad
                    items_count[nombre]["subtotal"] += subtotal

            top_display = []
            if items_count:
                top_items = sorted(items_count.items(), key=lambda x: x[1]["cantidad"], reverse=True)[:3]
                for nombre, info in top_items:
                    if info["cantidad"] > 0:
                        top_display.append(f"{nombre} x{info['cantidad']}")

            productos = obtener_productos()
            low_inventory = [
                {"name": p.get("nombre", "Sin nombre"), "stock": int(p.get("stockActual", 0))}
                for p in productos
                if int(p.get("stockActual", 0)) < int(p.get("stockMinimo", 0))
            ]

            return {
                "dailySales": format_currency(daily_sales),
                "topProducts": top_display if top_display else ["No hay ventas hoy"],
                "lowInventory": low_inventory,
                "generatedInvoices": len(ventas_hoy),
                "ventas_hoy": ventas_hoy
            }

        except Exception as e:
            print(f"Error en fetch_dashboard_data: {e}")
            import traceback
            traceback.print_exc()
            return {
                "dailySales": "Error",
                "topProducts": ["Error cargando datos"],
                "lowInventory": [],
                "generatedInvoices": "Error",
                "ventas_hoy": []
            }

    def _update_charts(self, data):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        self.chart_widgets.clear()

        # Gráfica Top Productos
        try:
            ventas_hoy = data.get("ventas_hoy", [])
            product_count = {}
            for venta in ventas_hoy:
                if venta.get("tipo") == "productos":
                    nombre = venta.get("producto", "")
                    cantidad = int(venta.get("cantidad", 0))
                    if nombre:
                        product_count[nombre] = product_count.get(nombre, 0) + cantidad

            sorted_products = sorted(product_count.items(), key=lambda x: x[1], reverse=True)[:5]
            if sorted_products:
                names = [item[0] for item in sorted_products]
                values = [item[1] for item in sorted_products]

                fig, ax = plt.subplots(figsize=(5, 3))
                bars = ax.bar(names, values, color="#4e73df", edgecolor="#2e59d9")
                ax.set_title("Productos Más Vendidos Hoy", fontsize=10, fontweight='bold')
                ax.set_ylabel("Cantidad", fontsize=9)
                ax.set_facecolor("#f8f9fa")
                fig.patch.set_facecolor("#f8f9fa")

                for bar in bars:
                    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height(), f'{int(bar.get_height())}', ha='center', va='bottom', fontsize=8)

                plt.xticks(rotation=30, ha='right', fontsize=9)
                plt.yticks(fontsize=9)
                plt.tight_layout()

                canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(side="left", fill="both", expand=True, padx=10, pady=10)
                self.chart_widgets["topProducts"] = canvas
            else:
                tk.Label(self.chart_frame, text="No hay ventas de productos hoy",
                        font=("Segoe UI", 10), bg="#f5f7fa", fg="#666").pack(side="left", fill="both", expand=True)
        except Exception as e:
            print(f"Error Top Productos: {e}")

        # Gráfica Últimos 7 días
        try:
            fechas = []
            ventas_semana = []
            for i in range(6, -1, -1):
                fecha = datetime.now() - timedelta(days=i)
                fecha_inicio = fecha.replace(hour=0, minute=0, second=0, microsecond=0)
                fecha_fin = fecha_inicio + timedelta(days=1)
                fecha_display = fecha.strftime("%d/%m")
                fechas.append(fecha_display)

                ventas_dia = obtener_ventas({
                    "fecha": {
                        "$gte": fecha_inicio.strftime("%Y-%m-%d %H:%M:%S"),
                        "$lt": fecha_fin.strftime("%Y-%m-%d %H:%M:%S")
                    }
                })
                total_dia = sum(float(v.get("subtotal", 0)) for v in ventas_dia)
                ventas_semana.append(total_dia)

            fig, ax = plt.subplots(figsize=(8, 3))
            ax.plot(fechas, ventas_semana, marker='o', color="#36b9cc", linewidth=2, markersize=6, markerfacecolor="#1cc88a")
            ax.set_title("Ventas Últimos 7 Días", fontsize=12, fontweight='bold', pad=20)
            ax.set_ylabel("Monto ($)")
            ax.set_facecolor("#f8f9fa")
            fig.patch.set_facecolor("#f8f9fa")
            ax.grid(True, alpha=0.3)
            for fecha, valor in zip(fechas, ventas_semana):
                if valor > 0:
                    ax.annotate(f'${valor:.0f}', (fecha, valor), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side="right", fill="both", expand=True, padx=10, pady=10)
            self.chart_widgets["ventasSemana"] = canvas
        except Exception as e:
            print(f"Error Ventas 7 días: {e}")

    @staticmethod
    def parse_currency_to_float(text):
        if not text or text.lower() == "sin registros":
            return 0
        text = text.replace("$", "").replace("'", "").replace(".", "").replace(",", ".")
        try:
            return float(text)
        except:
            return 0

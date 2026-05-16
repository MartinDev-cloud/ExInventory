import tkinter as tk
from tkinter import messagebox, Canvas, Frame
from frontend.components.addItemModal import AddItemModal
from frontend.components.detailModal import DetailModal
from frontend.components.cardItem import CardItem
from frontend.components.crearCategoria import CrearCategoria
from backend.db import productosdb  # importa tu módulo de base de datos


class Productos(tk.Frame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, bg="#f9fafb", *args, **kwargs)
        self.controller = controller
        self.selected_category = "Todos"
        self.items = productosdb.obtener_productos()

        # Menú de categorías
        self.categorias_menu = CrearCategoria(self, self.on_category_selected, pagina="productos")
        self.categorias_menu.pack(fill="x", padx=20, pady=(10, 0))

        # Botón añadir producto
        tk.Button(
            self, text="+ Añadir Producto", bg="#28a745", fg="white",
            font=("Arial", 10, "bold"), padx=3, pady=5, relief="flat",
            cursor="hand2", command=self.open_add_modal
        ).pack(pady=10, anchor="w", padx=20)

        # Canvas con scrollbar
        self.container = tk.Frame(self, bg="#f9fafb")
        self.container.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self.canvas = Canvas(self.container, bg="#f9fafb", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas, bg="#f9fafb")

        self.window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.scrollable_frame.bind("<Configure>", self.update_scrollbar)
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.window_id, width=e.width))

        # Soporte scroll con mouse (Windows, Linux y Mac)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)      # Windows y Mac
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)        # Linux scroll up
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)        # Linux scroll down


        self.render_items()   # primera carga de productos
        self.auto_refresh()   # refresco automático

    def auto_refresh(self):
        self.render_items()
        self.after(5000, self.auto_refresh)

    def on_category_selected(self, category):
        self.selected_category = category
        self.render_items()

    def update_scrollbar(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        if self.scrollable_frame.winfo_reqheight() > self.canvas.winfo_height():
            self.scrollbar.pack(side="right", fill="y")
        else:
            self.scrollbar.pack_forget()

    def _on_mousewheel(self, event):
        if self.scrollable_frame.winfo_reqheight() <= self.canvas.winfo_height():
            return  # No scroll si no hay overflow

        if event.num == 4:   # Linux scroll up
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5: # Linux scroll down
            self.canvas.yview_scroll(1, "units")
        else:  # Windows / Mac
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # --- CRUD ---
    def open_add_modal(self):
        AddItemModal(self, "Añadir producto", self.get_fields(), self.handle_add, lambda: None)

    def open_edit_modal(self, item):
        edit_item = item.copy()

        # Normalizar el ID si viene como '_id' o 'id'
        if "_id" in edit_item and edit_item["_id"]:
            edit_item["_id"] = str(edit_item["_id"])
        elif "id" in edit_item and edit_item["id"]:
            edit_item["_id"] = str(edit_item["id"])
        else:
            messagebox.showerror("Error", "Este producto no tiene un ID válido.")
            return

        AddItemModal(
            self,
            "Editar producto",
            self.get_fields(),
            self.handle_update,
            lambda: None,
            initialData=edit_item
        )

    def handle_add(self, newItem):
        if "imagen" in newItem and newItem["imagen"]:
            newItem["imagen"] = productosdb.guardar_imagen(newItem["imagen"])
        new_id = productosdb.crear_producto(newItem)
        newItem["_id"] = new_id
        self.items.append(newItem)
        self.render_items()

    def handle_update(self, updatedItem):
        if "_id" not in updatedItem or not updatedItem["_id"]:
            messagebox.showerror("Error", "No se encontró el ID del producto.")
            return

        updated = productosdb.actualizar_producto(updatedItem["_id"], updatedItem)
        if not updated:
            messagebox.showerror("Error", "No se pudo actualizar el producto en la base de datos.")
            return

        # ✅ Recargar desde DB para mantener consistencia
        self.items = productosdb.obtener_productos()
        self.render_items()

    def handle_delete(self, itemId):
        if not messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar este producto?"):
            return
        productosdb.eliminar_producto(itemId)
        self.items = [i for i in self.items if str(i.get("_id")) != str(itemId)]
        self.render_items()

    def open_detail_modal(self, item):
        fields = [
            ("Descripción:", "descripcion"), ("Stock actual:", "stockActual"),
            ("Stock mínimo:", "stockMinimo"), ("Costo:", "costo"),
            ("Precio venta:", "precioVenta"), ("Ubicación:", "ubicacion"),
            ("Proveedor:", "proveedor"), ("Categoría:", "categoria"),
            ("Fecha ingreso:", "fechaIngreso"), ("Fecha vencimiento:", "fechaVencimiento")
        ]
        DetailModal(
            parent=self,
            item=item,
            fields=fields,
            on_edit=lambda i=item: self.open_edit_modal(i),
            on_delete=self.handle_delete,
            title="Detalle del producto"
        )

    def render_items(self):
        # Siempre traer los productos desde la base de datos
        self.items = productosdb.obtener_productos()

        # Limpiar el contenedor
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Filtrar por categoría
        items_to_show = self.items if self.selected_category == "Todos" else [
            i for i in self.items if i.get("categoria") == self.selected_category
        ]

        # Dibujar tarjetas
        columns = 4
        for idx, item in enumerate(items_to_show):
            row, col = divmod(idx, columns)
            card = CardItem(
                self.scrollable_frame,
                title=item.get("nombre", "Sin nombre"),
                description=f"${item.get('precioVenta', '0')}",
                image_filename=item.get("imagen"),
                onClick=lambda i=item: self.open_detail_modal(i),
                image_type="productosIMG"
            )
            card.grid(row=row, column=col, padx=10, pady=10)
            for col in range(columns):
                self.scrollable_frame.grid_columnconfigure(col, weight=1, uniform="col")
        self.update_scrollbar()

    def get_fields(self):
        return [
            {"name": "nombre", "label": "Nombre del producto", "type": "text"},
            {"name": "imagen", "label": "Imagen del producto", "type": "file"},
            {"name": "descripcion", "label": "Descripción", "type": "textarea"},
            {"name": "stockActual", "label": "Cantidad actual", "type": "number"},
            {"name": "stockMinimo", "label": "Cantidad mínima", "type": "number"},
            {"name": "costo", "label": "Costo del producto", "type": "float"},
            {"name": "precioVenta", "label": "Precio de venta", "type": "float"},
            {"name": "proveedor", "label": "Proveedor", "type": "text"},
            {"name": "ubicacion", "label": "Ubicacion", "type": "text"},
            {"name": "categoria", "label": "Categoría", "type": "text"},
            {"name": "fechaIngreso", "label": "Fecha de ingreso", "type": "date"},
            {"name": "fechaVencimiento", "label": "Fecha de vencimiento", "type": "date"},
        ]

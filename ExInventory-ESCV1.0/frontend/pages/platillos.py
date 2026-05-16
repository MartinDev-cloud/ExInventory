import tkinter as tk
from tkinter import messagebox, Canvas, Frame
from frontend.components.addItemModal import AddItemModal
from frontend.components.detailModal import DetailModal
from frontend.components.cardItem import CardItem
from frontend.components.crearCategoria import CrearCategoria
from backend.db import platillosdb  # Tu módulo de base de datos de platillos


class Platillos(tk.Frame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, bg="#f9fafb", *args, **kwargs)
        self.controller = controller
        self.selected_category = "Todos"
        self.items = platillosdb.obtener_platillos()

        # Menú de categorías opcional
        self.categorias_menu = CrearCategoria(self, self.on_category_selected, pagina="platillos")
        self.categorias_menu.pack(fill="x", padx=20, pady=(10, 0))

        # Botón añadir platillo
        tk.Button(
            self, text="+ Añadir Platillo", bg="#28a745", fg="white",
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
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        self.render_items()
        self.auto_refresh()

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
            return
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # --- CRUD ---
    def open_add_modal(self):
        AddItemModal(
            self,
            "Añadir Platillo",
            self.get_fields(),
            self.handle_add,
            lambda: None,
            item_type="platillos"
        )

    def open_edit_modal(self, item):
        AddItemModal(
            self,
            "Editar Platillo",
            self.get_fields(),
            self.handle_update,
            lambda: None,
            initialData=item,
            item_type="platillos"
        )

    def handle_add(self, newItem):
        new_id = platillosdb.crear_platillo(newItem)
        newItem["_id"] = new_id
        self.items.append(newItem)
        self.render_items()

    def handle_update(self, updatedItem):
        if "_id" not in updatedItem or not updatedItem["_id"]:
            messagebox.showerror("Error", "No se encontró el ID del platillo.")
            return

        updated = platillosdb.actualizar_platillo(updatedItem["_id"], updatedItem)
        if not updated:
            messagebox.showerror("Error", "No se pudo actualizar el platillo en la base de datos.")
            return

        self.items = platillosdb.obtener_platillos()
        self.render_items()

    def handle_delete(self, itemId):
        if not messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar este platillo?"):
            return
        platillosdb.eliminar_platillo(itemId)
        self.items = [i for i in self.items if str(i.get("_id")) != str(itemId)]
        self.render_items()

    def open_detail_modal(self, item):
        fields = [
            ("Nombre:", "nombrePlato"),
            ("Descripción:", "descripcion"),
            ("Costo de producción:", "costoProduccion"),
            ("Precio de venta:", "precioVenta"),
            ("Tamaño/Porción:", "tamanoPorcion"),
            ("Tiempo preparación:", "tiempoPreparacion"),
            ("Ubicación menú:", "ubicacionMenu"),
            ("Disponibilidad:", "disponibilidad"),
            ("Etiquetas:", "etiquetas"),
            ("Notas internas:", "notasInternas"),
        ]
        DetailModal(
            parent=self,
            item=item,
            fields=fields,
            on_edit=lambda i=item: self.open_edit_modal(i),
            on_delete=self.handle_delete,
            title="Detalle del platillo"
        )

    def render_items(self):
        self.items = platillosdb.obtener_platillos()
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        items_to_show = self.items if self.selected_category == "Todos" else [
            i for i in self.items if i.get("etiquetas") == self.selected_category
        ]

        columns = 4
        for idx, item in enumerate(items_to_show):
            row, col = divmod(idx, columns)

            card = CardItem(
                self.scrollable_frame,
                title=item.get("nombrePlato", ""),
                description=f"${item.get('precioVenta', 0)}",
                image_filename=item.get("imagen"),
                onClick=lambda i=item: self.open_detail_modal(i),
                image_type="platillosIMG"
            )
            card.grid(row=row, column=col, padx=10, pady=10)
            for col in range(columns):
                self.scrollable_frame.grid_columnconfigure(col, weight=1, uniform="col")

        self.update_scrollbar()

    def get_fields(self):
        return [
            {"name": "nombrePlato", "label": "Nombre del plato", "type": "text", "required": True},
            {"name": "imagen", "label": "Imagen del plato", "type": "file"},
            {"name": "descripcion", "label": "Descripción", "type": "textarea"},
            {"name": "costoProduccion", "label": "Costo de producción", "type": "number"},
            {"name": "precioVenta", "label": "Precio de venta", "type": "number"},
            {"name": "tamanoPorcion", "label": "Tamaño o porción", "type": "text"},
            {"name": "tiempoPreparacion", "label": "Tiempo de preparación", "type": "duration"},  # ✔ corregido
            {"name": "ubicacionMenu", "label": "Ubicación en menú", "type": "text"},
            {"name": "disponibilidad", "label": "Disponibilidad", "type": "text"},
            {"name": "etiquetas", "label": "Etiquetas", "type": "text"},
            {"name": "notasInternas", "label": "Notas internas", "type": "textarea"},
        ]


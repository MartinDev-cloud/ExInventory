import tkinter as tk
from tkinter import messagebox, Canvas, Frame
from frontend.components.addItemModal import AddItemModal
from frontend.components.detailModal import DetailModal
from frontend.components.cardItem import CardItem
from frontend.components.crearCategoria import CrearCategoria
from backend.db import serviciosdb  # Tu módulo de base de datos de servicios


class Servicios(tk.Frame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, bg="#f9fafb", *args, **kwargs)
        self.controller = controller
        self.selected_category = "Todos"
        self.items = serviciosdb.obtener_servicios()

        # Menú de categorías si aplica (opcional)
        self.categorias_menu = CrearCategoria(self, self.on_category_selected, pagina="servicios")
        self.categorias_menu.pack(fill="x", padx=20, pady=(10, 0))

        # Botón añadir servicio
        tk.Button(
            self, text="+ Añadir Servicio", bg="#28a745", fg="white",
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
            "Añadir Servicio",
            self.get_fields(),
            self.handle_add,
            lambda: None,
            item_type="servicios"  # <-- importante
        )

    def open_edit_modal(self, item):
        AddItemModal(
            self,
            "Editar Servicio",
            self.get_fields(),
            self.handle_update,
            lambda: None,
            initialData=item,
            item_type="servicios"  # <-- importante
        )

    def handle_add(self, newItem):

        new_id = serviciosdb.crear_servicio(newItem)
        newItem["_id"] = new_id
        self.items.append(newItem)
        self.render_items()

    def handle_update(self, updatedItem):
        if "_id" not in updatedItem or not updatedItem["_id"]:
            messagebox.showerror("Error", "No se encontró el ID del servicio.")
            return

        updated = serviciosdb.actualizar_servicio(updatedItem["_id"], updatedItem)
        if not updated:
            messagebox.showerror("Error", "No se pudo actualizar el servicio en la base de datos.")
            return

        self.items = serviciosdb.obtener_servicios()
        self.render_items()

    def handle_delete(self, itemId):
        if not messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar este servicio?"):
            return
        serviciosdb.eliminar_servicio(itemId)
        self.items = [i for i in self.items if str(i.get("_id")) != str(itemId)]
        self.render_items()

    def open_detail_modal(self, item):
        fields = [
            ("Número habitación:", "numeroHabitacion"),
            ("Tipo habitación:", "tipoHabitacion"),
            ("Incluye:", "incluye"),
            ("Costo mantenimiento:", "costoMantenimiento"),
            ("Precio habitación:", "precioHabitacion"),
            ("Costo extensión hora:", "costoExtensionHora"),
            ("Estado:", "estado"),
        ]
        DetailModal(parent=self, item=item, fields=fields, on_edit=lambda i=item: self.open_edit_modal(i), on_delete=self.handle_delete, title="Detalle del servicio")

    def render_items(self):
        self.items = serviciosdb.obtener_servicios()
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        items_to_show = self.items if self.selected_category == "Todos" else [
            i for i in self.items if i.get("tipoHabitacion") == self.selected_category
        ]

        columns = 4
        for idx, item in enumerate(items_to_show):
            row, col = divmod(idx, columns)

            card = CardItem(
                self.scrollable_frame,
                title=f"{item.get('numeroHabitacion', '')}",
                description=f"${item.get('precioHabitacion', 0)}",
                image_filename=item.get("imagen"),
                onClick=lambda i=item: self.open_detail_modal(i),
                image_type="serviciosIMG"
            )
            card.grid(row=row, column=col, padx=10, pady=10)
            for col in range(columns):
                self.scrollable_frame.grid_columnconfigure(col, weight=1, uniform="col")
        self.update_scrollbar()

    def get_fields(self):
        return [
            {"name": "numeroHabitacion", "label": "Número de habitación", "type": "text"},
            {"name": "tipoHabitacion", "label": "Tipo de habitación", "type": "text"},
            {"name": "imagen", "label": "Imagen de la habitación", "type": "file"},
            {"name": "incluye", "label": "Incluye (Descripción)", "type": "textarea"},
            {"name": "costoMantenimiento", "label": "Costo de mantenimiento", "type": "number"},
            {"name": "precioHabitacion", "label": "Precio de la habitación", "type": "number"},
            {"name": "costoExtensionHora", "label": "Costo de extensión de hora", "type": "number"},
            {"name": "estado", "label": "Estado (Disponible/En mantenimiento)", "type": "text"},
        ]

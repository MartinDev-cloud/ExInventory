import tkinter as tk
from tkinter import simpledialog, messagebox
from backend.db import categoriasdb

class CrearCategoria(tk.Frame):
    def __init__(self, parent, on_category_selected, pagina, *args, **kwargs):
        """
        Componente reutilizable para crear, listar y eliminar categorías/etiquetas/tipos.
        - parent: contenedor padre
        - on_category_selected: callback(category_name)
        - pagina: 'productos', 'servicios' o 'platillos'
        """
        super().__init__(parent, pady=0, bg="white",
                         highlightthickness=2, highlightbackground="#d1d5db", *args, **kwargs)

        self.on_category_selected = on_category_selected
        self.pagina = pagina
        self.active_category = "Todos"

        # Map de textos según pagina
        self.TEXTS = {
            "productos": {
                "singular": "Categoría",
                "create": "+ Crear categoría",
                "delete": "🗑 Eliminar categoría",
                "new_title": "Nueva categoría",
                "new_msg": "Ingrese el nombre de la categoría:",
                "delete_title": "Eliminar categoría",
                "delete_msg": "Seleccione una categoría para eliminar:"
            },
            "platillos": {
                "singular": "Etiqueta",
                "create": "+ Crear etiqueta",
                "delete": "🗑 Eliminar etiqueta",
                "new_title": "Nueva etiqueta",
                "new_msg": "Ingrese el nombre de la etiqueta:",
                "delete_title": "Eliminar etiqueta",
                "delete_msg": "Seleccione una etiqueta para eliminar:"
            },
            "servicios": {
                "singular": "Tipo de servicio",
                "create": "+ Crear tipo de servicio",
                "delete": "🗑 Eliminar tipo de servicio",
                "new_title": "Nuevo tipo de servicio",
                "new_msg": "Ingrese el nombre del tipo de servicio:",
                "delete_title": "Eliminar tipo de servicio",
                "delete_msg": "Seleccione un tipo de servicio para eliminar:"
            }
        }

        self.labels = self.TEXTS.get(self.pagina, self.TEXTS["productos"])

        # --- Cargar categorías desde MongoDB ---
        self.categories = categoriasdb.obtener_categorias(self.pagina)

        # --- Contenedor principal ---
        container = tk.Frame(self, bg="white", padx=10, pady=5)
        container.pack(fill="x", expand=True)

        # --- Fila superior: categorías + botones ---
        top_row = tk.Frame(container, bg="white")
        top_row.pack(fill="x", expand=True)

        # --- Canvas para desplazamiento horizontal de categorías ---
        self.canvas = tk.Canvas(top_row, bg="white", height=45, highlightthickness=0)
        self.scroll_frame = tk.Frame(self.canvas, bg="white")
        self.scroll_window = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.pack(side="left", fill="x", expand=True)

        # --- Botón crear (texto dinámico) ---
        self.create_btn = tk.Button(
            top_row, text=self.labels["create"],
            bg="#2563eb", fg="white",
            font=("Arial", 10, "bold"),
            padx=12, pady=6,
            relief="flat", cursor="hand2",
            command=self.add_category_dialog
        )
        self.create_btn.pack(side="right", padx=(10, 0))

        # --- Botón eliminar (texto dinámico) ---
        self.delete_btn = tk.Button(
            top_row, text=self.labels["delete"],
            bg="#dc2626", fg="white",
            font=("Arial", 10, "bold"),
            padx=12, pady=6,
            relief="flat", cursor="hand2",
            command=self.delete_category_dialog
        )
        self.delete_btn.pack(side="right", padx=(10, 0))

        # --- Scrollbar horizontal ---
        self.scrollbar = tk.Scrollbar(container, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(fill="x", pady=(2, 0))

        # Actualiza región del scroll
        self.scroll_frame.bind("<Configure>", self._update_scroll)

        self.category_buttons = {}
        self.render_buttons()

    def _update_scroll(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def render_buttons(self):
        for btn in self.category_buttons.values():
            btn.destroy()
        self.category_buttons.clear()

        # Recargar categorías desde la base de datos
        self.categories = categoriasdb.obtener_categorias(self.pagina)

        for cat in self.categories:
            btn = tk.Button(
                self.scroll_frame, text=cat,
                bg=self.get_bg_color(cat),
                fg=self.get_fg_color(cat),
                font=("Arial", 10, "bold"),
                padx=12, pady=6,
                relief="flat", cursor="hand2",
                command=lambda c=cat: self.select_category(c)
            )
            btn.pack(side="left", padx=6, pady=5)
            self.category_buttons[cat] = btn

        # Desplazar automáticamente al final
        self.after(100, lambda: self.canvas.xview_moveto(1.0))

    def get_bg_color(self, category):
        return "#28a745" if category == self.active_category else "#e5e7eb"

    def get_fg_color(self, category):
        return "white" if category == self.active_category else "black"

    def select_category(self, category):
        self.active_category = category
        self.render_buttons()
        self.on_category_selected(category)

    def add_category_dialog(self):
        title = self.labels["new_title"]
        msg = self.labels["new_msg"]
        new_cat = simpledialog.askstring(title, msg)
        if not new_cat:
            return

        new_cat = new_cat.strip()
        if not new_cat:
            messagebox.showwarning("Error", "El nombre no puede estar vacío")
            return

        ok = categoriasdb.crear_categoria(new_cat, self.pagina)
        if not ok:
            messagebox.showwarning("Error", f"Esa {self.labels['singular'].lower()} ya existe")
            return

        self.render_buttons()

    def delete_category_dialog(self):
        if len(self.categories) <= 1:
            messagebox.showinfo("Info", f"No hay {self.labels['singular'].lower()}s para eliminar")
            return

        win = tk.Toplevel(self)
        win.title(self.labels["delete_title"])

        # --- Centrar ventana ---
        width, height = 240, 220
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        win.geometry(f"{width}x{height}+{x}+{y}")
        win.resizable(False, False)

        tk.Label(win, text=self.labels["delete_msg"]).pack(pady=5)

        # Crear botones por categoría
        for cat in self.categories:
            if cat == "Todos":
                continue
            btn = tk.Button(
                win, text=cat, bg="#28a745", fg="white",
                command=lambda c=cat, w=win: self._confirm_delete(c, w)
            )
            btn.pack(fill="x", padx=10, pady=5)

    def _confirm_delete(self, category, window):
        if messagebox.askyesno("Confirmar", f"¿Seguro que deseas eliminar '{category}'?"):
            categoriasdb.eliminar_categoria(category, self.pagina)
            self.render_buttons()
        window.destroy()

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import os
import subprocess

class VerDocumentos(tk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent, bg="#f5f7fa")
        self.controller = controller

        # Cambiado por defecto a "Todos"
        self.tipo_mostrar = tk.StringVar(value="Todos")
        self.documentos = []

        # Estilos
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        style.configure("TButton", padding=5, relief="flat")

        self.create_widgets()
        self.cargar_documentos(mostrar_mensaje=False)

    # ------------------ BLOQUEAR COLUMNAS ------------------
    def bloquear_columnas(self, treeview):
        for col in treeview["columns"]:
            w = treeview.column(col, "width")
            treeview.column(col, width=w, minwidth=w, stretch=False)

        treeview.bind("<Button-1>", self._bloquear_eventos)
        treeview.bind("<B1-Motion>", lambda e: "break")

    def _bloquear_eventos(self, event):
        region = self.tabla.identify_region(event.x, event.y)
        if region == "heading":
            return "break"

    # ------------------ AJUSTAR COLUMNAS ------------------
    def ajustar_columnas(self):
        total_width = self.tabla.winfo_width()
        columnas = self.tabla["columns"]
        n = len(columnas)
        if total_width > 0:
            ancho_columna = total_width // n
            for col in columnas:
                self.tabla.column(col, width=ancho_columna)

    # ------------------ CREAR WIDGETS ------------------
    def create_widgets(self):
        ttk.Label(self, text="Documentos Guardados", font=("Arial", 16, "bold"), background="#f5f7fa").pack(pady=(10,0))
        ttk.Label(self, text="Consulta, controla y gestiona tus facturas y cotizaciones", background="#f5f7fa").pack(pady=(0,10))

        # Selector de tipo
        # Selector de tipo
        frame_filtro = ttk.Frame(self)
        frame_filtro.pack(pady=5)
        ttk.Label(frame_filtro, text="Mostrar:").pack(side="left", padx=5)
        combo_tipo = ttk.Combobox(
            frame_filtro, 
            textvariable=self.tipo_mostrar,
            values=["Facturas", "Cotizaciones", "Todos"],  # <-- Mayúscula inicial
            state="readonly", 
            width=15
        )
        combo_tipo.pack(side="left")
        combo_tipo.bind("<<ComboboxSelected>>", lambda e: self.cargar_documentos(False))

        # Treeview
        columnas = ("tipo", "cliente", "documento", "fecha", "cantidad", "total")
        self.tabla = ttk.Treeview(self, columns=columnas, show="headings", selectmode="browse")
        for col, text in zip(columnas, ["Tipo","Cliente","Teléfono","Fecha","Cantidad Total (P/S)","Precio Total"]):
            self.tabla.heading(col, text=text)
            self.tabla.column(col, width=120, anchor="center")

        self.tabla.pack(padx=20, pady=10, fill="both", expand=True)
        self.tabla['displaycolumns'] = columnas

        # Bloquear columnas y ajustar automáticamente al ancho
        self.bloquear_columnas(self.tabla)
        self.tabla.bind("<Configure>", lambda e: self.ajustar_columnas())

        # Botones
        frame_botones = tk.Frame(self, bg="#f5f7fa")
        frame_botones.pack(pady=10)

        btn_opts = [
            ("Ver PDF", "#2563eb", self.ver_pdf),
            ("Eliminar", "#dc2626", self.eliminar_documento),
            ("Editar", "#28a745", self.editar_documento)
        ]
        for text, color, cmd in btn_opts:
            tk.Button(frame_botones, text=text, bg=color, fg="white", font=("Arial",10,"bold"),
                      activebackground=color, activeforeground="white", relief="flat",
                      padx=12, pady=6, cursor="hand2", command=cmd).pack(side="left", padx=5)

    # ------------------ FUNCIONES ------------------
    def validar_seleccion(self, accion: str):
        selected = self.tabla.focus()
        if not selected:
            messagebox.showwarning("Aviso", f"Debes seleccionar un documento para {accion}.")
            return None
        return self.tabla.index(selected)

    def cargar_documentos(self, mostrar_mensaje=True):
        self.tabla.delete(*self.tabla.get_children())
        self.documentos.clear()
        try:
            tipo = self.tipo_mostrar.get()
            facturas = requests.get("http://127.0.0.1:5000/facturas").json()
            cotizaciones = requests.get("http://127.0.0.1:5000/cotizaciones").json()

            tipo = self.tipo_mostrar.get()
            docs = []
            if tipo == "Facturas":
                docs = [{"tipo":"Factura", **f} for f in facturas]
            elif tipo == "Cotizaciones":
                docs = [{"tipo":"Cotización", **c} for c in cotizaciones]
            elif tipo == "Todos":
                docs = [{"tipo":"Factura", **f} for f in facturas] + [{"tipo":"Cotización", **c} for c in cotizaciones]


            for d in docs:
                cliente = d["cliente"]["nombre"]
                doc = d["cliente"].get("telefono", "N/A")
                fecha = d.get("fecha","N/A")
                cantidad_total = sum(p.get("cantidad",1) for p in d.get("productos",[]))
                total = f"${d.get('total',0):.2f}"
                self.tabla.insert("", "end", values=(d["tipo"], cliente, doc, fecha, cantidad_total, total))
                self.documentos.append(d)

            if not docs and mostrar_mensaje:
                messagebox.showinfo("Sin datos","No hay documentos registrados para mostrar.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los documentos:\n{e}")

    def ver_pdf(self):
        index = self.validar_seleccion("abrirlo o verlo")
        if index is None: return
        documento = self.documentos[index]
        pdf_path = documento.get("pdfPath")
        if not pdf_path or not os.path.exists(pdf_path):
            messagebox.showerror("Error","No se encontró el archivo PDF asociado.")
            return
        try:
            if os.name=="nt":
                os.startfile(pdf_path)
            elif os.name=="posix":
                subprocess.call(("xdg-open", pdf_path))
            else:
                subprocess.call(("open", pdf_path))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el PDF:\n{e}")

    def eliminar_documento(self):
        index = self.validar_seleccion("eliminar")
        if index is None: return
        documento = self.documentos[index]
        tipo = documento["tipo"]
        doc_id = documento.get("_id")
        if not messagebox.askyesno("Confirmar", f"¿Seguro que deseas eliminar esta {tipo}?"):
            return
        try:
            url = f"http://127.0.0.1:5000/facturas/{doc_id}" if tipo=="Factura" else f"http://127.0.0.1:5000/cotizaciones/{doc_id}"
            respuesta = requests.delete(url)
            if respuesta.status_code==200:
                messagebox.showinfo("Eliminado", f"La {tipo} se eliminó correctamente.")
                self.cargar_documentos(False)
            else:
                messagebox.showerror("Error", f"No se pudo eliminar: {respuesta.text}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar al backend:\n{e}")

    def editar_documento(self):
        index = self.validar_seleccion("editar")
        if index is None: return
        documento = self.documentos[index]
        try:
            if documento["tipo"]=="Factura":
                from frontend.pages.generarFactura import GenerarFactura
                ventana = GenerarFactura
            else:
                from frontend.pages.generarCotizacion import GenerarCotizacion
                ventana = GenerarCotizacion

            edit_window = tk.Toplevel(self)
            edit_window.title(f"Editar {documento['tipo']}")
            
            # Pasamos la función de refresco
            ventana_doc = ventana(edit_window, refrescar_callback=self.cargar_documentos)
            ventana_doc.pack(fill="both", expand=True)
            ventana_doc.cargar_datos(documento)
            
            # Si cierras la ventana sin guardar, refresca también
            edit_window.protocol("WM_DELETE_WINDOW", lambda: [edit_window.destroy(), self.cargar_documentos(False)])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la ventana de edición:\n{e}")

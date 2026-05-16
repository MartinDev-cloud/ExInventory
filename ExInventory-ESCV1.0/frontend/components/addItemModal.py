import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import os
import re

# Ruta compartida en la raíz del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR)))
ASSETS_ROOT = os.path.join(PROJECT_ROOT, "assets")

class AddItemModal(tk.Toplevel):
    FIELD_WIDTH = 36
    FIELD_BG_COLOR = "#f5f5f5"
    FIELD_BORDER_COLOR = "#d1d5db"
    FIELD_HIGHLIGHT_COLOR = "#3b82f6"
    BUTTON_BG_ADD = "#28a745"
    BUTTON_BG_CANCEL = "#dc3545"

    def __init__(self, parent, title, fields, onAdd, onClose, initialData=None, item_type="productos"):
        super().__init__(parent)
        self.item_type = item_type
        self.title(title)
        self.geometry("355x650")
        self.resizable(False, True)
        self.transient(parent)
        self.grab_set()

        # Centrar ventana
        width, height = 355, 650
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        self.fields = fields
        self.onAdd = onAdd
        self.onClose = onClose
        self.initialData = initialData or {}
        self.formData = {}
        self.previewImages = {}

        if "_id" in self.initialData and self.initialData["_id"]:
            self.formData["_id"] = str(self.initialData["_id"])

        # Contenedor scroll
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.form_frame = tk.Frame(self.canvas, bg="white", padx=8)
        self.form_frame_id = self.canvas.create_window((0, 0), window=self.form_frame, anchor="nw")

        self.form_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.form_frame_id, width=e.width))
        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

        # Estilo uniforme para DateEntry
        style = ttk.Style(self)
        style.configure("Custom.DateEntry",
                        fieldbackground=self.FIELD_BG_COLOR,
                        background=self.FIELD_BG_COLOR,
                        bordercolor=self.FIELD_BORDER_COLOR,
                        lightcolor=self.FIELD_BORDER_COLOR,
                        darkcolor=self.FIELD_BORDER_COLOR,
                        foreground="black")

        self.inputs = {}
        for f in self.fields:
            self._create_field(f)

        # Botones
        btn_frame = tk.Frame(self.form_frame, bg="white")
        btn_frame.pack(pady=15, fill="x")

        btn_add = tk.Button(
            btn_frame,
            text="Actualizar" if self.initialData.get("_id") else "Añadir",
            bg=self.BUTTON_BG_ADD, fg="white", padx=15, pady=5,
            relief="flat", cursor="hand2", bd=0,
            command=self.handle_submit
        )
        btn_add.pack(side="left", expand=True, padx=5)

        btn_cancel = tk.Button(
            btn_frame, text="Cancelar", bg=self.BUTTON_BG_CANCEL, fg="white",
            padx=15, pady=5, relief="flat", cursor="hand2", bd=0,
            command=self.close_modal
        )
        btn_cancel.pack(side="right", expand=True, padx=5)

    # --- Validación de números positivos ---
    def only_positive_numbers(self, text):
        return text == "" or (text.isdigit() and int(text) >= 0)

    # --- Formatear duración ---
    def format_duration(self, days=0, hours=0, minutes=0, seconds=0):
        if not (0 <= days <= 365):
            raise ValueError("Los días deben estar entre 0 y 365")
        if not (0 <= hours <= 23):
            raise ValueError("Las horas deben estar entre 0 y 23")
        if not (0 <= minutes <= 59):
            raise ValueError("Los minutos deben estar entre 0 y 59")
        if not (0 <= seconds <= 59):
            raise ValueError("Los segundos deben estar entre 0 y 59")

        parts = []
        if days: parts.append(f"{days} día(s)")
        if hours: parts.append(f"{hours} hora(s)")
        if minutes: parts.append(f"{minutes} minuto(s)")
        if seconds: parts.append(f"{seconds} segundo(s)")
        return " ".join(parts)

    # --- Crear campos ---
    def _create_field(self, f):
        frame = tk.Frame(self.form_frame, bg="white")
        frame.pack(fill="x", pady=0, padx=10)

        label = tk.Label(frame, text=f["label"] + ":", font=("Arial", 10, "bold"), bg="white")
        label.pack(anchor="w", pady=(4, 2))

        field_type = f.get("type", "text")

        if field_type == "textarea":
            entry = tk.Text(frame, height=4, width=self.FIELD_WIDTH, font=("Arial", 10),
                            bd=0, bg=self.FIELD_BG_COLOR, relief="flat",
                            highlightthickness=2, highlightbackground=self.FIELD_BORDER_COLOR,
                            highlightcolor=self.FIELD_HIGHLIGHT_COLOR)
            entry.pack(pady=3, fill="x")
            if f["name"] in self.initialData:
                entry.insert("1.0", self.initialData[f["name"]])
            self.inputs[f["name"]] = entry

        elif field_type == "file":
            btn_file = tk.Button(frame, text="Seleccionar archivo", bg="#e2e8f0", fg="black",
                                 relief="flat", cursor="hand2",
                                 command=lambda name=f["name"], fr=frame: self.handle_file(name, fr))
            btn_file.pack(anchor="w", pady=5, fill="x", expand=True)
            if self.initialData.get(f["name"]):
                self.show_preview(self.initialData[f["name"]], frame, f["name"])

        elif field_type == "number":
            vcmd = self.register(self.only_positive_numbers)
            entry = tk.Entry(frame, font=("Arial", 10), width=self.FIELD_WIDTH,
                             bd=0, bg=self.FIELD_BG_COLOR, relief="flat",
                             highlightthickness=2, highlightbackground=self.FIELD_BORDER_COLOR,
                             highlightcolor=self.FIELD_HIGHLIGHT_COLOR,
                             validate="key", validatecommand=(vcmd, "%P"))
            entry.pack(pady=3, fill="x")
            if f["name"] in self.initialData:
                entry.insert(0, self.initialData[f["name"]])
            self.inputs[f["name"]] = entry

        elif field_type == "date":
            date_entry = DateEntry(
                frame,
                style="Custom.DateEntry",
                locale="es_ES",
                date_pattern="yyyy-mm-dd",
                borderwidth=0,
                background="white",
                foreground="black",
                selectbackground=self.FIELD_HIGHLIGHT_COLOR,
                selectforeground="white"
            )
            date_entry.pack(pady=3, fill="x", expand=True)
            date_entry.bind("<FocusIn>", lambda e: self.focus())
            if f["name"] in self.initialData and self.initialData[f["name"]]:
                try:
                    date_entry.set_date(self.initialData[f["name"]])
                except Exception:
                    pass
            self.inputs[f["name"]] = date_entry

        elif field_type == "time":
            time_frame = tk.Frame(frame, bg="white")
            time_frame.pack(fill="x")
            hour_var, minute_var, ampm_var = tk.StringVar(), tk.StringVar(), tk.StringVar(value="AM")
            vcmd_hour = (self.register(lambda P: P.isdigit() and 1 <= int(P) <= 12 or P == ""), "%P")
            vcmd_minute = (self.register(lambda P: P.isdigit() and 0 <= int(P) <= 59 or P == ""), "%P")
            tk.Entry(time_frame, width=3, textvariable=hour_var, validate="key", validatecommand=vcmd_hour).pack(side="left", padx=2)
            tk.Entry(time_frame, width=3, textvariable=minute_var, validate="key", validatecommand=vcmd_minute).pack(side="left", padx=2)
            ttk.Combobox(time_frame, values=["AM","PM"], width=4, textvariable=ampm_var, state="readonly").pack(side="left")
            self.inputs[f["name"]] = {"hour": hour_var, "minute": minute_var, "ampm": ampm_var}

        elif field_type == "duration":
            dur_frame = tk.Frame(frame, bg="white")
            dur_frame.pack(fill="x")
            day_var, hour_var, minute_var, second_var = tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()
            vcmd_day = (self.register(lambda P: P.isdigit() and 0 <= int(P) <= 365 or P == ""), "%P")
            vcmd_hour = (self.register(lambda P: P.isdigit() and 0 <= int(P) <= 23 or P == ""), "%P")
            vcmd_minute = (self.register(lambda P: P.isdigit() and 0 <= int(P) <= 59 or P == ""), "%P")
            vcmd_second = (self.register(lambda P: P.isdigit() and 0 <= int(P) <= 59 or P == ""), "%P")
            tk.Entry(dur_frame, width=4, textvariable=day_var, validate="key", validatecommand=vcmd_day).pack(side="left", padx=2)
            tk.Label(dur_frame, text="día(s)", bg="white").pack(side="left")
            tk.Entry(dur_frame, width=3, textvariable=hour_var, validate="key", validatecommand=vcmd_hour).pack(side="left", padx=2)
            tk.Label(dur_frame, text="hora(s)", bg="white").pack(side="left")
            tk.Entry(dur_frame, width=3, textvariable=minute_var, validate="key", validatecommand=vcmd_minute).pack(side="left", padx=2)
            tk.Label(dur_frame, text="minuto(s)", bg="white").pack(side="left")
            tk.Entry(dur_frame, width=3, textvariable=second_var, validate="key", validatecommand=vcmd_second).pack(side="left", padx=2)
            tk.Label(dur_frame, text="segundo(s)", bg="white").pack(side="left")

            # Inicializar valores si existen
            if f["name"] in self.initialData and self.initialData[f["name"]]:
                try:
                    s = self.initialData[f["name"]]
                    days = int(re.search(r"(\d+)\s*día", s).group(1)) if "día" in s else 0
                    hours = int(re.search(r"(\d+)\s*hora", s).group(1)) if "hora" in s else 0
                    minutes = int(re.search(r"(\d+)\s*minuto", s).group(1)) if "minuto" in s else 0
                    seconds = int(re.search(r"(\d+)\s*segundo", s).group(1)) if "segundo" in s else 0
                    day_var.set(str(days))
                    hour_var.set(str(hours))
                    minute_var.set(str(minutes))
                    second_var.set(str(seconds))
                except Exception:
                    pass

            self.inputs[f["name"]] = {"days": day_var, "hours": hour_var, "minutes": minute_var, "seconds": second_var}

        else:  # text
            entry = tk.Entry(frame, font=("Arial", 10), width=self.FIELD_WIDTH,
                             bd=0, bg=self.FIELD_BG_COLOR, relief="flat",
                             highlightthickness=2, highlightbackground=self.FIELD_BORDER_COLOR,
                             highlightcolor=self.FIELD_HIGHLIGHT_COLOR)
            entry.pack(pady=3, fill="x")
            if f["name"] in self.initialData:
                entry.insert(0, self.initialData[f["name"]])
            self.inputs[f["name"]] = entry

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def handle_file(self, name, parent_frame):
        file_path = filedialog.askopenfilename(title="Seleccionar imagen",
                                               filetypes=[("Archivos de imagen", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            self.formData[name] = file_path
            self.show_preview(file_path, parent_frame, name)

    def show_preview(self, image_path, parent_frame, name):
        try:
            folder_map = {
                "productos": "productosIMG",
                "servicios": "serviciosIMG",
                "platillos": "platillosIMG",
                "inventarios": "inventariosIMG"
            }
            folder = folder_map.get(self.item_type, "productosIMG")
            if not os.path.isabs(image_path):
                image_path = os.path.join(
                    ASSETS_ROOT, folder, image_path
                )
                image_path = os.path.normpath(image_path)

            img = Image.open(image_path).copy()
            img = img.resize((250, 250), Image.Resampling.LANCZOS)
            preview = ImageTk.PhotoImage(img)

            if name in self.previewImages:
                self.previewImages[name]["image_label"].configure(image=preview)
                self.previewImages[name]["image_label"].image = preview
                self.previewImages[name]["name_label"].configure(text=os.path.basename(image_path))
            else:
                lbl_img = tk.Label(parent_frame, image=preview, bg="white")
                lbl_img.image = preview
                lbl_img.pack(side="top", pady=5)
                lbl_name = tk.Label(parent_frame, text=os.path.basename(image_path), bg="white", fg="#374151",
                                    font=("Arial", 9, "italic"))
                lbl_name.pack(anchor="w")
                self.previewImages[name] = {"image_label": lbl_img, "name_label": lbl_name}

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen: {e}")

    def handle_submit(self):
        try:
            # Seleccionar DB según item_type
            if self.item_type == "productos":
                from backend.db import productosdb as db
            elif self.item_type == "servicios":
                from backend.db import serviciosdb as db
            elif self.item_type == "platillos":
                from backend.db import platillosdb as db
            elif self.item_type == "inventarios":
                from backend.db import inventariosdb as db
            else:
                messagebox.showerror("Error", f"Tipo de ítem desconocido: {self.item_type}")
                return
        except ImportError as e:
            messagebox.showerror("Error", f"No se pudo importar la base de datos: {e}")
            return

        for f in self.fields:
            name = f["name"]
            required = f.get("required", True)

            field_type = f.get("type", "text")
            value = None

            if field_type == "textarea":
                value = self.inputs[name].get("1.0", "end").strip()
            elif field_type == "file":
                if name in self.formData:
                    value = db.guardar_imagen(self.formData[name])
                else:
                    value = self.initialData.get(name)
            elif field_type == "date":
                value = self.inputs[name].get()
            elif field_type == "time":
                t = self.inputs[name]
                hour_str = t["hour"].get().strip()
                minute_str = t["minute"].get().strip()
                ampm = t["ampm"].get()
                if hour_str == "" or minute_str == "":
                    messagebox.showwarning("Campo obligatorio", f"El campo '{f['label']}' no puede estar vacío.")
                    return
                hour = int(hour_str)
                minute = int(minute_str)
                if ampm == "PM" and hour != 12: hour += 12
                elif ampm == "AM" and hour == 12: hour = 0
                value = f"{hour:02d}:{minute:02d}"
            elif field_type == "duration":
                t = self.inputs[name]
                try:
                    days = int(t["days"].get() or 0)
                    hours = int(t["hours"].get() or 0)
                    minutes = int(t["minutes"].get() or 0)
                    seconds = int(t["seconds"].get() or 0)
                    value = self.format_duration(days, hours, minutes, seconds)
                except ValueError as e:
                    messagebox.showwarning("Valor inválido", str(e))
                    return
            else:
                value = self.inputs[name].get().strip()

            if required and not value:
                messagebox.showwarning("Campo obligatorio", f"El campo '{f['label']}' no puede estar vacío.")
                return

            self.formData[name] = value

        if "_id" in self.initialData:
            self.formData["_id"] = str(self.initialData["_id"])

        self.onAdd(self.formData)
        self.destroy()

    def close_modal(self):
        self.onClose()
        self.destroy()

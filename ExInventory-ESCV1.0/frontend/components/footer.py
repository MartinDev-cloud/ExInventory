import tkinter as tk
import datetime


class Footer(tk.Frame):
    def __init__(self, parent, controller=None, *args, **kwargs):
        super().__init__(parent, bg="#002bb5", *args, **kwargs)
        self.configure(height=60)  # altura del footer
        self.pack_propagate(False)  # no se ajuste al contenido

        # Contenedor principal
        container = tk.Frame(self, bg="#002bb5")
        container.pack(fill="x", padx=20, pady=10)

        # Información de contacto
        info = tk.Frame(container, bg="#002bb5")
        info.pack(side="left", anchor="w")

        tk.Label(
            info, text="📧 contacto@imperialdevs.com",
            bg="#002bb5", fg="white", font=("Arial", 10)
        ).pack(anchor="w")

        tk.Label(
            info, text="📞 +57 312 345 6789",
            bg="#002bb5", fg="white", font=("Arial", 10)
        ).pack(anchor="w")

        tk.Label(
            info, text="📍 Santander de Quilichao, Cauca",
            bg="#002bb5", fg="white", font=("Arial", 10)
        ).pack(anchor="w")

        # Copyright dinámico
        year = datetime.datetime.now().year
        copy_label = tk.Label(
            container,
            text=f"© {year} Imperial Devs - Todos los derechos reservados.",
            bg="#002bb5", fg="white", font=("Arial", 9)
        )
        copy_label.pack(side="right", anchor="e")

# ExInventory - Gestión de Inventarios y Facturación

**ExInventory** es una aplicación de escritorio desarrollada en **Python** con **Tkinter** para la interfaz y **Flask** para el backend. Permite gestionar inventarios, productos, servicios y facturación.

El proyecto es **multiplataforma**, funcionando en **Windows, Linux y macOS**.

---

## 1. Requisitos previos

Antes de iniciar, asegúrate de tener:

* **Python 3.13** o superior con `pip` incluido.
* **Tkinter** (usualmente viene incluido en Python).
* Permisos de ejecución en Linux/macOS para scripts `.sh`.

> Asegúrate de que Python esté en el PATH del sistema.

---

## 2. Crear el entorno virtual

Dependiendo del sistema operativo, ejecuta el script correspondiente para crear el `.venv` y las dependencias.

### Windows

1. Ejecutar crear_venv(Windows).bat

El script hará lo siguiente:

1. Elimina cualquier entorno virtual `.venv` previo.
2. Crea un nuevo entorno virtual `.venv` compatible con tu directorio.
3. Actualiza `pip` a la última versión.
4. Instala todas las dependencias listadas en `requirements.txt`.

---

### Linux / macOS

1. Abrir **terminal** en la carpeta raíz del proyecto.
2. Dar permisos de ejecución al script (solo la primera vez):

```bash
chmod +x crear_venv(Linux-macOS).sh
```

3. Ejecutar el script:

```bash
./crear_venv(Linux-macOS).sh
```

> 🔹 Esto realizará las mismas acciones que en Windows, creando un `.venv` compatible con tu sistema.

---

## 3. Ejecutar la aplicación

Una vez creado el entorno virtual, ejecuta el frontend (puedes ejecutar directamente app.py desde un editor de codigo VSCode o Pycharm) o en cmd dentro de la carpeta raiz (ExInventory):

* **Windows:**

```bat
.venv\Scripts\python.exe frontend\app.py
```

* **Linux / macOS:**

```bash
.venv/bin/python frontend/app.py
```

> 🔹 Esto iniciará la aplicación **Tkinter** y el servidor **Flask** en segundo plano.

---

## 4. Actualizar dependencias

Si agregas o actualizas paquetes:

1. Activar el entorno virtual:

* **Windows:**

```bat
.venv\Scripts\activate
```

* **Linux/macOS:**

```bash
source .venv/bin/activate
```

2. Instalar o actualizar paquetes:

```bash
pip install nombre-del-paquete
```

3. Y guardar TODAS las dependencias actualizadas en `requirements.txt`:

```bash
pip freeze > requirements.txt
```

> 🔹 Esto asegura que otros desarrolladores puedan instalar exactamente las mismas dependencias.

---

## 5. Buenas prácticas

* No modifiques archivos dentro de `.venv`; recrea el entorno si cambias de máquina.
* Mantén `requirements.txt` actualizado con `pip freeze`.
* Siempre ejecutar los scripts de creación de `.venv` antes de correr la aplicación en un nuevo sistema.
* Para producción, considera herramientas como **PyInstaller** o **Docker**.

---

## 6. Estructura del proyecto

```
ExInventory-ESC/
│
├─ .venv/                     # Entorno virtual
├─ backend/                   # Código del backend (Flask,FastApi...)
│   └─ assets/                # Imagenes que guarda el usuario
│      └─ platillosIMG/
│      └─ productosIMG/
│      └─ serviciosIMG/
│   └─ db/
│   └─ docs/                  # Documentos que genera el usuario
│      └─ cotizacionesPDF/
│      └─ facturasPDF/
│   └─ main_documentos.py
│   └─ main_platillos.py
│   └─ main_productos.py
│   └─ main_servicios.py
├─ frontend/                  # Código del frontend (Tkinter)
│   └─ assets/
│      └─ "...".webp          # Imagenes .webp para los logos de la aplicacion
│   └─ components/
│   └─ pages/
│   └─ styles/
│   └─ app.py
├─ BaseDeDatos.json           # Base de datos Mongo DB Compass del proyecto ExInventory
├─ requirements.txt           # Dependencias del proyecto
├─ crear_venv(Windows).bat    # Ejecutable para creacion de entorno en Windows
├─ crear_venv(Linux-macOS).sh # Ejecutable para creacion de entorno en Linux/macOS
├─ Instrucciones.md
└─ requirements.txt

```

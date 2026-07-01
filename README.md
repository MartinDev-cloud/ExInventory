# ExInventory - Sistema de Gestión de Inventarios

ExInventory es una aplicación de escritorio desarrollada en Python orientada a la administración de inventarios, productos, servicios y generación de documentos comerciales.

La aplicación permite gestionar información de manera organizada mediante una interfaz gráfica desarrollada con Tkinter y una arquitectura modular que integra backend y frontend separados.

El proyecto está diseñado para funcionar en múltiples plataformas, incluyendo Windows, Linux y macOS.

---

# Características principales

- Gestión de productos y servicios.
- Administración de inventario.
- Registro y control de productos, platillos o servicios.
- Generación de facturas y cotizaciones en PDF.
- Almacenamiento de imágenes de productos y servicios.
- Arquitectura modular escalable.
- Integración con base de datos MongoDB Compass.
- Interfaz gráfica amigable desarrollada en Tkinter.

---

# Tecnologías utilizadas

- Python 3
- Tkinter
- Flask / FastAPI
- MongoDB Compass
- Pillow
- ReportLab
- CustomTkinter

---

# Compatibilidad

ExInventory puede ejecutarse en:
- Windows (Probado)
- Linux (En fase de prueba)
- macOS (En fase de prueba)

---

# 1. Requisitos previos

Antes de iniciar, asegúrate de tener instalado:

- Python 3.13 o superior.
- pip.
- Tkinter (normalmente incluido con Python).

> Asegúrate de que Python esté agregado al PATH del sistema.

---
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

* No modifiques archivos dentro de `.venv`; vuelve a crear el entorno si cambias de máquina o de directorio.
* Mantén `requirements.txt` actualizado con `pip freeze`.
* Siempre ejecuta los scripts de creación de `.venv` antes de correr la aplicación en un nuevo sistema (o no ejecutara correctamente).

---

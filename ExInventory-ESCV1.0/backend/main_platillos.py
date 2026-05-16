from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse
from backend.db import platillosdb
import os, shutil, uuid

app = FastAPI()

# Carpeta de imágenes (misma ruta que usa platillosdb)
IMG_DIR = os.path.join(os.path.dirname(__file__), "assets", "platillosIMG")
os.makedirs(IMG_DIR, exist_ok=True)

# ----------------- RUTAS -----------------
@app.get("/platillos")
def get_platillos():
    return platillosdb.obtener_platillos()

@app.post("/platillos")
def add_platillo(
    nombrePlato: str = Form(...),
    descripcion: str = Form(""),
    costoProduccion: float = Form(0),
    precioVenta: float = Form(0),
    tamanoPorcion: str = Form(""),
    tiempoPreparacion: str = Form(""),
    ubicacionMenu: str = Form(""),
    disponibilidad: str = Form(""),
    etiquetas: str = Form(""),
    notasInternas: str = Form(""),
    categoria: str = Form(""),
    imagen: UploadFile = None
):
    platillo = {
        "nombrePlato": nombrePlato,
        "descripcion": descripcion,
        "costoProduccion": costoProduccion,
        "precioVenta": precioVenta,
        "tamanoPorcion": tamanoPorcion,
        "tiempoPreparacion": tiempoPreparacion,
        "ubicacionMenu": ubicacionMenu,
        "disponibilidad": disponibilidad,
        "etiquetas": etiquetas,
        "notasInternas": notasInternas,
        "categoria": categoria,
        "imagen": None
    }

    if imagen:
        ext = os.path.splitext(imagen.filename)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(IMG_DIR, unique_name)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)
        platillo["imagen"] = unique_name

    new_id = platillosdb.crear_platillo(platillo)
    platillo["_id"] = new_id
    return {"success": True, "platillo": platillo}

@app.get("/platillos/imagen/{filename}")
def get_imagen(filename: str):
    filepath = os.path.join(IMG_DIR, filename)
    if os.path.exists(filepath):
        return FileResponse(filepath)
    return {"error": "Imagen no encontrada"}

@app.put("/platillos/{platillo_id}")
def update_platillo(
    platillo_id: str,
    nombrePlato: str = Form(...),
    descripcion: str = Form(""),
    costoProduccion: float = Form(0),
    precioVenta: float = Form(0),
    tamanoPorcion: str = Form(""),
    tiempoPreparacion: str = Form(""),
    ubicacionMenu: str = Form(""),
    disponibilidad: str = Form(""),
    etiquetas: str = Form(""),
    notasInternas: str = Form(""),
    categoria: str = Form(""),
    imagen: UploadFile = None
):
    nuevos_datos = {
        "nombrePlato": nombrePlato,
        "descripcion": descripcion,
        "costoProduccion": costoProduccion,
        "precioVenta": precioVenta,
        "tamanoPorcion": tamanoPorcion,
        "tiempoPreparacion": tiempoPreparacion,
        "ubicacionMenu": ubicacionMenu,
        "disponibilidad": disponibilidad,
        "etiquetas": etiquetas,
        "notasInternas": notasInternas,
        "categoria": categoria
    }

    if imagen:
        ext = os.path.splitext(imagen.filename)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(IMG_DIR, unique_name)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)
        nuevos_datos["imagen"] = unique_name

    updated = platillosdb.actualizar_platillo(platillo_id, nuevos_datos)
    return {"success": updated}

@app.delete("/platillos/{platillo_id}")
def delete_platillo(platillo_id: str):
    deleted = platillosdb.eliminar_platillo(platillo_id)
    return {"success": deleted}

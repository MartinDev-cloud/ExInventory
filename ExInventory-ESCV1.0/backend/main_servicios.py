from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse
from backend.db import serviciosdb
import os
import shutil
import uuid

app = FastAPI()

# Carpeta de imágenes (misma ruta que usa serviciosdb)
IMG_DIR = os.path.join(os.path.dirname(__file__), "assets", "serviciosIMG")
os.makedirs(IMG_DIR, exist_ok=True)


@app.get("/servicios")
def get_servicios():
    servicios = serviciosdb.obtener_servicios()
    return servicios


@app.post("/servicios")
def add_servicio(
    numeroHabitacion: str = Form(...),
    tipoHabitacion: str = Form(...),
    incluye: str = Form(""),
    costoMantenimiento: float = Form(0),
    precioHabitacion: float = Form(0),
    horaEntrada: str = Form(""),
    horaSalida: str = Form(""),
    costoExtensionHora: float = Form(0),
    estado: str = Form("Disponible"),
    categoria: str = Form(""),
    imagen: UploadFile = None
):
    servicio = {
        "numeroHabitacion": numeroHabitacion,
        "tipoHabitacion": tipoHabitacion,
        "incluye": incluye,
        "costoMantenimiento": costoMantenimiento,
        "precioHabitacion": precioHabitacion,
        "horaEntrada": horaEntrada,
        "horaSalida": horaSalida,
        "costoExtensionHora": costoExtensionHora,
        "estado": estado,
        "categoria": categoria,
        "imagen": None,
    }

    # --- Guardar imagen ---
    if imagen:
        ext = os.path.splitext(imagen.filename)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(IMG_DIR, unique_name)

        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)

        servicio["imagen"] = unique_name

    new_id = serviciosdb.crear_servicio(servicio)
    servicio["_id"] = new_id
    return {"success": True, "servicio": servicio}


@app.get("/servicios/imagen/{filename}")
def get_imagen(filename: str):
    filepath = os.path.join(IMG_DIR, filename)
    if os.path.exists(filepath):
        return FileResponse(filepath)
    return {"error": "Imagen no encontrada"}


@app.put("/servicios/{servicio_id}")
def update_servicio(
    servicio_id: str,
    numeroHabitacion: str = Form(...),
    tipoHabitacion: str = Form(...),
    incluye: str = Form(""),
    costoMantenimiento: float = Form(0),
    precioHabitacion: float = Form(0),
    horaEntrada: str = Form(""),
    horaSalida: str = Form(""),
    costoExtensionHora: float = Form(0),
    estado: str = Form("Disponible"),
    categoria: str = Form(""),
    imagen: UploadFile = None
):
    nuevos_datos = {
        "numeroHabitacion": numeroHabitacion,
        "tipoHabitacion": tipoHabitacion,
        "incluye": incluye,
        "costoMantenimiento": costoMantenimiento,
        "precioHabitacion": precioHabitacion,
        "horaEntrada": horaEntrada,
        "horaSalida": horaSalida,
        "costoExtensionHora": costoExtensionHora,
        "estado": estado,
        "categoria": categoria,
    }

    if imagen:
        ext = os.path.splitext(imagen.filename)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(IMG_DIR, unique_name)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)
        nuevos_datos["imagen"] = unique_name

    updated = serviciosdb.actualizar_servicio(servicio_id, nuevos_datos)
    return {"success": updated}


@app.delete("/servicios/{servicio_id}")
def delete_servicio(servicio_id: str):
    deleted = serviciosdb.eliminar_servicio(servicio_id)
    return {"success": deleted}

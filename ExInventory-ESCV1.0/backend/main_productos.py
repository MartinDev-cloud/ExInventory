from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from backend.db import productosdb
import os, shutil, uuid

# -----------------------------------------------------------
# 🚀 Configuración general de FastAPI
# -----------------------------------------------------------
app = FastAPI(title="API de Productos - ExInventory")

# Habilitar CORS para desarrollo local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes restringir a tu dominio si lo deseas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta compartida con productosdb para almacenar imágenes
IMG_DIR = os.path.join(os.path.dirname(__file__), "assets", "productosIMG")
os.makedirs(IMG_DIR, exist_ok=True)


# -----------------------------------------------------------
# 📦 Modelos de datos con Pydantic
# -----------------------------------------------------------
class ProductoBase(BaseModel):
    nombre: str
    descripcion: str
    stockActual: int
    stockMinimo: int
    costo: float
    precioVenta: float
    ubicacion: Optional[str] = ""
    proveedor: Optional[str] = ""
    categoria: Optional[str] = ""
    fechaIngreso: Optional[str] = ""
    fechaVencimiento: Optional[str] = ""


class ProductoCreate(ProductoBase):
    """Modelo completo usado para crear un producto."""
    pass


class ProductoUpdate(BaseModel):
    """Modelo parcial usado para PATCH (actualizaciones parciales)."""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    stockActual: Optional[int] = None
    stockMinimo: Optional[int] = None
    costo: Optional[float] = None
    precioVenta: Optional[float] = None
    ubicacion: Optional[str] = None
    proveedor: Optional[str] = None
    categoria: Optional[str] = None
    fechaIngreso: Optional[str] = None
    fechaVencimiento: Optional[str] = None


# -----------------------------------------------------------
# 🧩 Endpoints
# -----------------------------------------------------------

@app.get("/productos")
def get_productos():
    """Obtiene todos los productos desde MongoDB."""
    return productosdb.obtener_productos()


@app.get("/productos/imagen/{filename}")
def get_imagen(filename: str):
    """Devuelve una imagen guardada si existe."""
    filepath = os.path.join(IMG_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    return FileResponse(filepath)


# -----------------------------------------------------------
# 🆕 Crear producto (con imagen opcional)
# -----------------------------------------------------------
@app.post("/productos")
async def add_producto(
    data: ProductoCreate = Form(...),
    imagen: Optional[UploadFile] = File(None)
):
    producto = data.dict()

    # Guardar imagen si se incluye
    if imagen:
        ext = os.path.splitext(imagen.filename)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(IMG_DIR, unique_name)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)
        producto["imagen"] = unique_name
    else:
        producto["imagen"] = None

    new_id = productosdb.crear_producto(producto)
    producto["_id"] = new_id

    return {"success": True, "producto": producto}


# -----------------------------------------------------------
# ✏️ Actualizar producto parcialmente (PATCH)
# -----------------------------------------------------------
@app.patch("/productos/{producto_id}")
async def update_producto(
    producto_id: str,
    data: ProductoUpdate = Form(...),
    imagen: Optional[UploadFile] = File(None)
):
    """Actualiza parcialmente un producto. Si no hay imagen, conserva la anterior."""
    nuevos_datos = {k: v for k, v in data.dict().items() if v is not None}

    # Verificar si existe el producto
    producto_actual = productosdb.obtener_producto_por_id(producto_id)
    if not producto_actual:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Si se envía una nueva imagen, reemplazarla
    if imagen:
        ext = os.path.splitext(imagen.filename)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(IMG_DIR, unique_name)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)
        nuevos_datos["imagen"] = unique_name
        # productosdb ya se encarga de borrar la antigua si es diferente

    updated = productosdb.actualizar_producto(producto_id, nuevos_datos)
    if not updated:
        raise HTTPException(status_code=400, detail="No se pudo actualizar el producto")

    return {"success": True, "message": "Producto actualizado correctamente"}


# -----------------------------------------------------------
# ❌ Eliminar producto
# -----------------------------------------------------------
@app.delete("/productos/{producto_id}")
def delete_producto(producto_id: str):
    """Elimina un producto y su imagen asociada."""
    deleted = productosdb.eliminar_producto(producto_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"success": True, "message": "Producto eliminado correctamente"}

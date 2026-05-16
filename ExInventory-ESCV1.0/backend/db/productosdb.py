from pymongo import MongoClient
from bson.objectid import ObjectId
import os, shutil
import uuid

# --- Conexión MongoDB ---
client = MongoClient("mongodb://localhost:27017/")
db = client["ExInventory"]
productos_collection = db["Productos"]

# --- Carpeta de imágenes compartida (raíz del proyecto) ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DATA_PATH = os.path.join(PROJECT_ROOT, "assets", "productosIMG")
os.makedirs(DATA_PATH, exist_ok=True)


# ----------------- UTILIDADES -----------------
def guardar_imagen(imagen_path):
    if not imagen_path:
        return None
    if not os.path.isabs(imagen_path):
        return imagen_path
    ext = os.path.splitext(imagen_path)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    destino = os.path.join(DATA_PATH, unique_name)
    shutil.copy(imagen_path, destino)
    return unique_name


def producto_to_json(producto):
    return {
        "_id": str(producto["_id"]),
        "nombre": producto.get("nombre"),
        "descripcion": producto.get("descripcion"),
        "stockActual": producto.get("stockActual"),
        "stockMinimo": producto.get("stockMinimo"),
        "costo": producto.get("costo"),
        "precioVenta": producto.get("precioVenta"),
        "ubicacion": producto.get("ubicacion"),
        "proveedor": producto.get("proveedor"),
        "categoria": producto.get("categoria"),
        "fechaIngreso": str(producto.get("fechaIngreso")) if producto.get("fechaIngreso") else None,
        "fechaVencimiento": str(producto.get("fechaVencimiento")) if producto.get("fechaVencimiento") else None,
        "imagen": producto.get("imagen"),
    }


def _normalizar_numericos(data: dict):
    for k in ("stockActual", "stockMinimo", "costo", "precioVenta"):
        if k in data:
            if data[k] in (None, "",):
                raise ValueError(f"{k} vacío")
            data[k] = int(data[k])
    return data


# ----------------- CRUD -----------------
def crear_producto(producto):
    producto = _normalizar_numericos(producto)
    if "imagen" in producto:
        producto["imagen"] = guardar_imagen(producto["imagen"])
    result = productos_collection.insert_one(producto)
    return str(result.inserted_id)


def obtener_productos(filtro=None):
    if filtro is None:
        filtro = {}
    productos = list(productos_collection.find(filtro))
    return [producto_to_json(p) for p in productos]


def obtener_producto_por_id(producto_id):
    producto = productos_collection.find_one({"_id": ObjectId(producto_id)})
    return producto_to_json(producto) if producto else None


def actualizar_producto(producto_id, nuevos_datos):
    if "_id" in nuevos_datos:
        nuevos_datos.pop("_id")

    producto_actual = productos_collection.find_one({"_id": ObjectId(producto_id)})
    if not producto_actual:
        return False

    nuevos_datos = _normalizar_numericos(nuevos_datos)

    if "imagen" in nuevos_datos:
        nueva_imagen = nuevos_datos["imagen"]

        if nueva_imagen:
            if os.path.isabs(nueva_imagen):
                nueva_guardada = guardar_imagen(nueva_imagen)
                nuevos_datos["imagen"] = nueva_guardada
            if producto_actual.get("imagen") and producto_actual["imagen"] != nuevos_datos["imagen"]:
                img_antigua_path = os.path.join(DATA_PATH, producto_actual["imagen"])
                if os.path.exists(img_antigua_path):
                    os.remove(img_antigua_path)
        else:
            nuevos_datos.pop("imagen", None)

    result = productos_collection.update_one(
        {"_id": ObjectId(producto_id)},
        {"$set": nuevos_datos}
    )
    return result.modified_count > 0


def eliminar_producto(producto_id):
    producto = productos_collection.find_one({"_id": ObjectId(producto_id)})
    if producto and producto.get("imagen"):
        img_path = os.path.join(DATA_PATH, producto["imagen"])
        if os.path.exists(img_path):
            os.remove(img_path)
    result = productos_collection.delete_one({"_id": ObjectId(producto_id)})
    return result.deleted_count > 0


def actualizar_stock_por_nombre(nombre, cantidad):
    producto = productos_collection.find_one({"nombre": nombre})
    if producto and "stockActual" in producto:
        nuevo_stock = int(producto["stockActual"]) - int(cantidad)
        productos_collection.update_one({"_id": producto["_id"]}, {"$set": {"stockActual": nuevo_stock}})
        return nuevo_stock
    return None


def limpiar_imagenes_huerfanas():
    imagenes_db = {p.get("imagen") for p in productos_collection.find({}, {"imagen": 1}) if p.get("imagen")}
    for filename in os.listdir(DATA_PATH):
        if filename not in imagenes_db:
            file_path = os.path.join(DATA_PATH, filename)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"❌ Error al eliminar {filename}: {e}")


limpiar_imagenes_huerfanas()

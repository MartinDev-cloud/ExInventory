from pymongo import MongoClient
from bson.objectid import ObjectId
import os, shutil, uuid

# --- Conexión MongoDB ---
client = MongoClient("mongodb://localhost:27017/")
db = client["ExInventory"]
platillos_collection = db["Platillos"]

# --- Carpeta de imágenes compartida (raíz del proyecto) ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DATA_PATH = os.path.join(PROJECT_ROOT, "assets", "platillosIMG")
os.makedirs(DATA_PATH, exist_ok=True)

# ----------------- UTILIDADES -----------------
def guardar_imagen(imagen_path):
    """Copia la imagen a assets/platillosIMG con un nombre único y retorna SOLO el nombre"""
    if not imagen_path:
        return None

    if not os.path.isabs(imagen_path):
        return imagen_path

    ext = os.path.splitext(imagen_path)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    destino = os.path.join(DATA_PATH, unique_name)
    shutil.copy(imagen_path, destino)
    return unique_name

def platillo_to_json(platillo):
    """Convierte un documento de Mongo a JSON seguro"""
    return {
        "_id": str(platillo["_id"]),
        "nombrePlato": platillo.get("nombrePlato"),
        "descripcion": platillo.get("descripcion"),
        "costoProduccion": platillo.get("costoProduccion"),
        "precioVenta": platillo.get("precioVenta"),
        "tamanoPorcion": platillo.get("tamanoPorcion"),
        "tiempoPreparacion": platillo.get("tiempoPreparacion"),
        "ubicacionMenu": platillo.get("ubicacionMenu"),
        "disponibilidad": platillo.get("disponibilidad"),
        "etiquetas": platillo.get("etiquetas"),
        "notasInternas": platillo.get("notasInternas"),
        "categoria": platillo.get("categoria"),
        "imagen": platillo.get("imagen"),
    }

# ----------------- CRUD -----------------
def crear_platillo(platillo):
    """Inserta un nuevo platillo en MongoDB"""
    if "imagen" in platillo:
        platillo["imagen"] = guardar_imagen(platillo["imagen"])
    result = platillos_collection.insert_one(platillo)
    return str(result.inserted_id)

def obtener_platillos(filtro=None):
    """Devuelve todos los platillos como lista de diccionarios"""
    if filtro is None:
        filtro = {}
    platillos = list(platillos_collection.find(filtro))
    return [platillo_to_json(p) for p in platillos]

def obtener_platillo_por_id(platillo_id):
    """Devuelve un platillo por su _id"""
    platillo = platillos_collection.find_one({"_id": ObjectId(platillo_id)})
    return platillo_to_json(platillo) if platillo else None

def actualizar_platillo(platillo_id, nuevos_datos):
    """Actualiza un platillo y elimina imagen antigua si se reemplaza"""
    if "_id" in nuevos_datos:
        nuevos_datos.pop("_id")

    platillo_actual = platillos_collection.find_one({"_id": ObjectId(platillo_id)})
    if not platillo_actual:
        return False

    if "imagen" in nuevos_datos:
        nueva_imagen = nuevos_datos["imagen"]

        if nueva_imagen:
            if os.path.isabs(nueva_imagen):
                nueva_guardada = guardar_imagen(nueva_imagen)
                nuevos_datos["imagen"] = nueva_guardada
            else:
                nuevos_datos["imagen"] = nueva_imagen

            if platillo_actual.get("imagen") and platillo_actual["imagen"] != nuevos_datos["imagen"]:
                img_antigua_path = os.path.join(DATA_PATH, platillo_actual["imagen"])
                if os.path.exists(img_antigua_path):
                    os.remove(img_antigua_path)
        else:
            nuevos_datos.pop("imagen", None)

    result = platillos_collection.update_one(
        {"_id": ObjectId(platillo_id)},
        {"$set": nuevos_datos}
    )
    return result.modified_count > 0

def eliminar_platillo(platillo_id):
    """Elimina un platillo y su imagen"""
    platillo = platillos_collection.find_one({"_id": ObjectId(platillo_id)})
    if platillo and platillo.get("imagen"):
        img_path = os.path.join(DATA_PATH, platillo["imagen"])
        if os.path.exists(img_path):
            os.remove(img_path)

    result = platillos_collection.delete_one({"_id": ObjectId(platillo_id)})
    return result.deleted_count > 0

# ----------------- LIMPIEZA AUTOMÁTICA -----------------
def limpiar_imagenes_huerfanas():
    """Elimina imágenes huérfanas"""
    imagenes_db = {p.get("imagen") for p in platillos_collection.find({}, {"imagen": 1}) if p.get("imagen")}
    for filename in os.listdir(DATA_PATH):
        if filename not in imagenes_db:
            try:
                os.remove(os.path.join(DATA_PATH, filename))
            except Exception as e:
                print(f"❌ Error al eliminar {filename}: {e}")

# Ejecutar limpieza al iniciar
limpiar_imagenes_huerfanas()

from pymongo import MongoClient
from bson.objectid import ObjectId
import os, shutil
import uuid

# --- Conexión MongoDB ---
client = MongoClient("mongodb://localhost:27017/")
db = client["ExInventory"]
servicios_collection = db["Servicios"]

# --- Carpeta de imágenes compartida (raíz del proyecto) ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DATA_PATH = os.path.join(PROJECT_ROOT, "assets", "serviciosIMG")
os.makedirs(DATA_PATH, exist_ok=True)

# ----------------- UTILIDADES -----------------
def guardar_imagen(imagen_path):
    """Copia la imagen a assets/serviciosIMG con un nombre único y retorna SOLO el nombre"""
    if not imagen_path:
        return None

    # Si ya es un nombre (no una ruta absoluta), se asume que ya está guardada
    if not os.path.isabs(imagen_path):
        return imagen_path

    ext = os.path.splitext(imagen_path)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    destino = os.path.join(DATA_PATH, unique_name)
    shutil.copy(imagen_path, destino)
    return unique_name

def servicio_to_json(servicio):
    """Convierte un documento de Mongo a JSON seguro"""
    return {
        "_id": str(servicio["_id"]),
        "numeroHabitacion": servicio.get("numeroHabitacion"),
        "tipoHabitacion": servicio.get("tipoHabitacion"),
        "incluye": servicio.get("incluye"),
        "costoMantenimiento": servicio.get("costoMantenimiento"),
        "precioHabitacion": servicio.get("precioHabitacion"),
        "horaEntrada": servicio.get("horaEntrada"),
        "horaSalida": servicio.get("horaSalida"),
        "costoExtensionHora": servicio.get("costoExtensionHora"),
        "estado": servicio.get("estado"),
        "categoria": servicio.get("categoria"),
        "imagen": servicio.get("imagen"),
    }

# ----------------- CRUD -----------------
def crear_servicio(servicio):
    """Inserta un nuevo servicio en MongoDB"""
    if "imagen" in servicio:
        servicio["imagen"] = guardar_imagen(servicio["imagen"])
    result = servicios_collection.insert_one(servicio)
    return str(result.inserted_id)

def obtener_servicios(filtro=None):
    """Devuelve todos los servicios como lista de diccionarios"""
    if filtro is None:
        filtro = {}
    servicios = list(servicios_collection.find(filtro))
    return [servicio_to_json(s) for s in servicios]

def obtener_servicio_por_id(servicio_id):
    """Devuelve un servicio por su _id"""
    servicio = servicios_collection.find_one({"_id": ObjectId(servicio_id)})
    return servicio_to_json(servicio) if servicio else None

def actualizar_servicio(servicio_id, nuevos_datos):
    """Actualiza un servicio en MongoDB y elimina la imagen antigua si se reemplaza"""
    if "_id" in nuevos_datos:
        nuevos_datos.pop("_id")

    servicio_actual = servicios_collection.find_one({"_id": ObjectId(servicio_id)})
    if not servicio_actual:
        return False

    if "imagen" in nuevos_datos:
        nueva_imagen = nuevos_datos["imagen"]

        if nueva_imagen:
            if os.path.isabs(nueva_imagen):
                nueva_guardada = guardar_imagen(nueva_imagen)
                nuevos_datos["imagen"] = nueva_guardada
            else:
                nuevos_datos["imagen"] = nueva_imagen

            if servicio_actual.get("imagen") and servicio_actual["imagen"] != nuevos_datos["imagen"]:
                img_antigua_path = os.path.join(DATA_PATH, servicio_actual["imagen"])
                if os.path.exists(img_antigua_path):
                    os.remove(img_antigua_path)
        else:
            nuevos_datos.pop("imagen", None)

    result = servicios_collection.update_one(
        {"_id": ObjectId(servicio_id)},
        {"$set": nuevos_datos}
    )
    return result.modified_count > 0

def eliminar_servicio(servicio_id):
    """Elimina un servicio por su _id y borra su imagen asociada"""
    servicio = servicios_collection.find_one({"_id": ObjectId(servicio_id)})
    if servicio and servicio.get("imagen"):
        img_path = os.path.join(DATA_PATH, servicio["imagen"])
        if os.path.exists(img_path):
            os.remove(img_path)

    result = servicios_collection.delete_one({"_id": ObjectId(servicio_id)})
    return result.deleted_count > 0

# ----------------- LIMPIEZA AUTOMÁTICA -----------------
def limpiar_imagenes_huerfanas():
    """Elimina imágenes que ya no están asociadas a servicios en MongoDB"""
    imagenes_db = {s.get("imagen") for s in servicios_collection.find({}, {"imagen": 1}) if s.get("imagen")}

    for filename in os.listdir(DATA_PATH):
        if filename not in imagenes_db:
            file_path = os.path.join(DATA_PATH, filename)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"❌ Error al eliminar {filename}: {e}")

# Ejecutar limpieza al iniciar
limpiar_imagenes_huerfanas()

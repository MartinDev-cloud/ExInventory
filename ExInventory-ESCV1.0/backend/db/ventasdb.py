from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient("mongodb://localhost:27017/")
db = client["ExInventory"]
ventas_collection = db["Ventas"]

def registrar_venta(venta):
    """Guarda una venta en la colección Ventas y retorna el id."""
    result = ventas_collection.insert_one(venta)
    return str(result.inserted_id)

def obtener_ventas(filtro=None):
    if filtro is None:
        filtro = {}
    return list(ventas_collection.find(filtro))

def eliminar_venta(venta_id):
    """Elimina una venta por su _id."""
    result = ventas_collection.delete_one({"_id": ObjectId(venta_id)})
    return result.deleted_count > 0

def actualizar_venta(venta_id, datos_actualizados):
    """Actualiza una venta por su _id."""
    try:
        # Aseguramos que el _id sea un ObjectId
        _id = ObjectId(venta_id)
        # Removemos el _id de los datos actualizados si existe
        if "_id" in datos_actualizados:
            del datos_actualizados["_id"]

        result = ventas_collection.update_one(
            {"_id": _id},
            {"$set": datos_actualizados}
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"Error al actualizar venta: {str(e)}")
        raise e

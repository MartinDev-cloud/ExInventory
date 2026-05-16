from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")  # Ajusta si tu conexión es distinta
db = client["ExInventory"]
coleccion = db["Categorias"]

# Map: pagina -> campo que se usará en los documentos de items
FIELD_KEY = {
    "productos": "categoria",
    "platillos": "etiquetas",     # plural porque en Platillos ya usabas 'etiquetas'
    "servicios": "tipoHabitacion"   # clave técnica para servicios
}

def obtener_clave(pagina):
    """Devuelve la clave/field que corresponde a una página (ej. 'categoria', 'etiquetas', 'tipoHabitacion')."""
    return FIELD_KEY.get(pagina, "categoria")

def obtener_categorias(pagina):
    """Devuelve todas las categorías de una página, siempre agregando 'Todos' al inicio."""
    categorias = list(coleccion.find({"pagina": pagina}, {"_id": 0, "nombre": 1}))
    nombres = ["Todos"] + [c["nombre"] for c in categorias]
    return nombres

def crear_categoria(nombre, pagina):
    """Crea una nueva categoría si no existe. Guarda también la clave correspondiente (field)."""
    existe = coleccion.find_one({"nombre": nombre, "pagina": pagina})
    if existe:
        return False
    clave = obtener_clave(pagina)
    coleccion.insert_one({"nombre": nombre, "pagina": pagina, "clave": clave})
    return True

def eliminar_categoria(nombre, pagina):
    """Elimina una categoría excepto 'Todos'."""
    if nombre == "Todos":
        return False
    result = coleccion.delete_one({"nombre": nombre, "pagina": pagina})
    return result.deleted_count > 0

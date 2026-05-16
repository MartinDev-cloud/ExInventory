from flask import Flask, request, jsonify
from flask_cors import CORS
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from bson.objectid import ObjectId
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
CORS(app)

# -------------------- Carpetas PDF --------------------
FACTURAS_FOLDER = os.path.join(os.path.dirname(__file__), "docs/FacturasPDF")
COTIZACIONES_FOLDER = os.path.join(os.path.dirname(__file__), "docs/CotizacionesPDF")
os.makedirs(FACTURAS_FOLDER, exist_ok=True)
os.makedirs(COTIZACIONES_FOLDER, exist_ok=True)

# -------------------- Conexión MongoDB --------------------
client = MongoClient("mongodb://localhost:27017/")
db = client["ExInventory"]
facturas_collection = db["Facturas"]
cotizaciones_collection = db["Cotizaciones"]

# -------------------- Funciones Facturas --------------------
def crear_factura(factura_data):
    resultado = facturas_collection.insert_one(factura_data)
    return str(resultado.inserted_id)

# Función actualizada para obtener las últimas facturas
def obtener_facturas(limit=3):
    """
    Devuelve las facturas más recientes, ordenadas por fecha descendente.
    """
    return list(facturas_collection.find().sort("fecha", -1).limit(limit))


def obtener_factura(id_factura):
    return facturas_collection.find_one({"_id": ObjectId(id_factura)})

def actualizar_factura(id_factura, factura_data):
    resultado = facturas_collection.update_one(
        {"_id": ObjectId(id_factura)},
        {"$set": factura_data}
    )
    return resultado.modified_count

def eliminar_factura(id_factura):
    resultado = facturas_collection.delete_one({"_id": ObjectId(id_factura)})
    return resultado.deleted_count

# -------------------- Funciones Cotizaciones --------------------
def crear_cotizacion(cotizacion_data):
    resultado = cotizaciones_collection.insert_one(cotizacion_data)
    return str(resultado.inserted_id)

def obtener_cotizaciones():
    return list(cotizaciones_collection.find())

def obtener_cotizacion(id_cotizacion):
    return cotizaciones_collection.find_one({"_id": ObjectId(id_cotizacion)})

def actualizar_cotizacion(id_cotizacion, cotizacion_data):
    resultado = cotizaciones_collection.update_one(
        {"_id": ObjectId(id_cotizacion)},
        {"$set": cotizacion_data}
    )
    return resultado.modified_count

def eliminar_cotizacion(id_cotizacion):
    resultado = cotizaciones_collection.delete_one({"_id": ObjectId(id_cotizacion)})
    return resultado.deleted_count

# -------------------- Función PDF --------------------
def generar_pdf_documento(documento, id_doc, tipo="factura"):
    folder = FACTURAS_FOLDER if tipo=="factura" else COTIZACIONES_FOLDER
    filename = os.path.join(folder, f"{tipo.capitalize()}_{id_doc}.pdf")
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    cliente = documento["cliente"]
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, tipo.upper())
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Cliente: {cliente['nombre']}")
    c.drawString(50, height - 100, f"Documento: {cliente['tipoDocumento']} {cliente['numeroDocumento']}")
    c.drawString(50, height - 120, f"Dirección: {cliente['direccion']}")
    c.drawString(50, height - 140, f"Teléfono: {cliente['telefono']}")
    c.drawString(50, height - 160, f"Email: {cliente['email']}")

    # Productos
    y = height - 200
    c.drawString(50, y, "Productos / Servicios")
    c.drawString(250, y, "Cantidad")
    c.drawString(350, y, "Valor Unitario")
    c.drawString(450, y, "Subtotal")
    y -= 20
    for p in documento["productos"]:
        c.drawString(50, y, p["nombre"])
        c.drawString(250, y, str(p["cantidad"]))
        c.drawString(350, y, f"{p['valorUnitario']:.2f}")
        subtotal = p["cantidad"] * p["valorUnitario"]
        c.drawString(450, y, f"{subtotal:.2f}")
        y -= 20

    # Totales
    y -= 20
    c.drawString(350, y, "Subtotal:")
    c.drawString(450, y, f"{documento['subtotal']:.2f}")
    if tipo == "factura":
        y -= 20
        c.drawString(350, y, "IVA (19%):")
        c.drawString(450, y, f"{documento['iva']:.2f}")
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(350, y, "Total:")
    c.drawString(450, y, f"{documento['total']:.2f}")

    c.save()
    return filename

# -------------------- Rutas Facturas --------------------
@app.route("/facturas", methods=["POST"])
def api_crear_factura():
    data = request.get_json()
    try:
        data["fecha"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Guardar fecha
        id_factura = crear_factura(data)
        generar_pdf_documento(data, id_factura, tipo="factura")
        return jsonify({"mensaje": "Factura creada y PDF generado", "id": id_factura}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/facturas", methods=["GET"])
def api_obtener_facturas():
    facturas = obtener_facturas()
    for f in facturas:
        f["_id"] = str(f["_id"])
        # Agregar ruta del PDF
        f["pdfPath"] = os.path.join(FACTURAS_FOLDER, f"Factura_{f['_id']}.pdf")
    return jsonify(facturas), 200

@app.route("/facturas/<id_factura>", methods=["PUT"])
def api_actualizar_factura(id_factura):
    data = request.get_json()
    mod_count = actualizar_factura(id_factura, data)
    if mod_count:
        generar_pdf_documento(data, id_factura, tipo="factura")
        return jsonify({"mensaje": "Factura actualizada y PDF regenerado"}), 200
    return jsonify({"error": "Factura no encontrada"}), 404

@app.route("/facturas/<id_factura>", methods=["DELETE"])
def api_eliminar_factura(id_factura):
    del_count = eliminar_factura(id_factura)
    if del_count:
        pdf_path = os.path.join(FACTURAS_FOLDER, f"Factura_{id_factura}.pdf")
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        return jsonify({"mensaje": "Factura eliminada y PDF borrado"}), 200
    return jsonify({"error": "Factura no encontrada"}), 404

# -------------------- Rutas Cotizaciones --------------------

@app.route("/cotizaciones", methods=["POST"])
def api_crear_cotizacion():
    data = request.get_json()
    try:
        data["fecha"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        id_cotizacion = crear_cotizacion(data)
        generar_pdf_documento(data, id_cotizacion, tipo="cotizacion")
        return jsonify({"mensaje": "Cotización creada y PDF generado", "id": id_cotizacion}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/cotizaciones", methods=["GET"])
def api_obtener_cotizaciones():
    cotizaciones = obtener_cotizaciones()
    for c in cotizaciones:
        c["_id"] = str(c["_id"])
        c["pdfPath"] = os.path.join(COTIZACIONES_FOLDER, f"Cotizacion_{c['_id']}.pdf")
    return jsonify(cotizaciones), 200

@app.route("/cotizaciones/<id_cotizacion>", methods=["PUT"])
def api_actualizar_cotizacion(id_cotizacion):
    data = request.get_json()
    mod_count = actualizar_cotizacion(id_cotizacion, data)
    if mod_count:
        generar_pdf_documento(data, id_cotizacion, tipo="cotizacion")
        return jsonify({"mensaje": "Cotización actualizada y PDF regenerado"}), 200
    return jsonify({"error": "Cotización no encontrada"}), 404

@app.route("/cotizaciones/<id_cotizacion>", methods=["DELETE"])
def api_eliminar_cotizacion(id_cotizacion):
    del_count = eliminar_cotizacion(id_cotizacion)
    if del_count:
        pdf_path = os.path.join(COTIZACIONES_FOLDER, f"Cotizacion_{id_cotizacion}.pdf")
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        return jsonify({"mensaje": "Cotización eliminada y PDF borrado"}), 200
    return jsonify({"error": "Cotización no encontrada"}), 404

# -------------------- Main --------------------
if __name__ == "__main__":
    app.run(port=5000, debug=True)

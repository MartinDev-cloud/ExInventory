# backend/app.py
from flask import Flask, request, jsonify
from pymongo import MongoClient
import bcrypt
import os

app = Flask(__name__)

# Configura tu conexión a MongoDB
MONGO_URI = "mongodb://localhost:27017/"  # Cambia si usas otro host/usuario/password
client = MongoClient(MONGO_URI)
db = client["ExInventory"]
usuarios_col = db["Usuarios"]  # Nombre de tu colección

# ---------------- LOGIN ESCRITORIO ----------------
@app.route("/login_escritorio", methods=["POST"])
def login_escritorio():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email y contraseña son requeridos"}), 400

    # Buscar usuario por email
    user = usuarios_col.find_one({"email": email})
    if not user:
        return jsonify({"error": "Credenciales inválidas"}), 401

    # Verificar contraseña
    if not bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
        return jsonify({"error": "Credenciales inválidas"}), 401

    # Por defecto, todos los usuarios son emprendedores
    user_data = {
        "_id": str(user["_id"]),
        "nombre": user["nombre"],
        "email": user["email"],
        "tipo": "emprendedor"  # Asignar siempre
    }

    return jsonify({"message": "Login exitoso", "user": user_data}), 200

if __name__ == "__main__":
    app.run(port=5001, debug=True)

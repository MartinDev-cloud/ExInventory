#!/bin/bash
echo "==========================================="
echo "     RECONSTRUYENDO ENTORNO VIRTUAL"
echo "==========================================="
echo

# ---- Eliminar .venv antiguo ----
if [ -d ".venv" ]; then
    echo "Eliminando entorno virtual anterior..."
    rm -rf .venv
else
    echo "No se encontro un entorno virtual previo."
fi

# ---- Crear nuevo entorno virtual ----
echo "Creando nuevo entorno virtual..."
python3 -m venv .venv

# ---- Actualizar pip usando Python del venv ----
echo "Actualizando pip..."
.venv/bin/python -m pip install --upgrade pip

# ---- Instalar dependencias ----
if [ -f "requirements.txt" ]; then
    echo "Instalando dependencias desde requirements.txt..."
    .venv/bin/python -m pip install -r requirements.txt
else
    echo "ERROR: No se encontro requirements.txt"
    exit 1
fi

echo
echo "==========================================="
echo "      ✅ ENTORNO VIRTUAL LISTO"
echo "==========================================="

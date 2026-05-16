@echo off
title Reconstruyendo entorno virtual portátil de ExInventory
echo ===========================================
echo      RECONSTRUYENDO ENTORNO VIRTUAL
echo ===========================================
echo.

REM ---- Eliminar .venv antiguo ----
if exist .venv (
    echo Eliminando entorno virtual anterior...
    rmdir /s /q .venv
) else (
    echo No se encontro un entorno virtual previo.
)

REM ---- Crear nuevo entorno virtual ----
echo Creando nuevo entorno virtual...
py -m venv .venv

REM ---- Actualizar pip usando Python del venv ----
echo Actualizando pip...
.venv\Scripts\python.exe -m pip install --upgrade pip

REM ---- Instalar dependencias ----
if exist requirements.txt (
    echo Instalando dependencias desde requirements.txt...
    .venv\Scripts\python.exe -m pip install -r requirements.txt
) else (
    echo ERROR: No se encontro requirements.txt
    pause
    exit /b
)

REM ---- Confirmar instalación ----
echo.
echo ===========================================
echo      ✅ ENTORNO VIRTUAL LISTO
echo ===========================================
echo.

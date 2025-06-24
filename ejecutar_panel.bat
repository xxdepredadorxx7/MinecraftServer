@echo off
title Panel de Administracion Minecraft Server
color 0B

echo.
echo ===================================================
echo    PANEL DE ADMINISTRACION MINECRAFT SERVER
echo ===================================================
echo.

echo Instalando dependencias de Python...
python -m pip install rich psutil requests --quiet

if %errorlevel% neq 0 (
    echo.
    echo Error: No se pudo instalar las dependencias de Python
    echo Verifica que Python este instalado correctamente
    pause
    exit /b 1
)

echo.
echo Iniciando panel de administracion...
python "%~dp0\04_admin_panel.py"

if %errorlevel% neq 0 (
    echo.
    echo Error ejecutando el panel de administracion
    echo Verifica que todos los archivos esten en su lugar
    pause
)

echo.
echo Panel cerrado
pause

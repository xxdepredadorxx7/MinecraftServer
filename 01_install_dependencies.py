#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instalador de Dependencias para Sistema de Servidor Minecraft
Instala automáticamente todas las librerías necesarias
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Verificar que la versión de Python sea compatible"""
    if sys.version_info < (3, 7):
        print("❌ Error: Se requiere Python 3.7 o superior")
        print(f"   Versión actual: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version} - Compatible")
    return True

def check_java():
    """Verificar que Java esté instalado"""
    try:
        result = subprocess.run(["java", "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            # Java imprime la versión en stderr por alguna razón
            version_output = result.stderr.strip()
            print(f"✅ Java encontrado: {version_output.split()[2] if len(version_output.split()) > 2 else 'Versión detectada'}")
            return True
        else:
            print("❌ Java no encontrado")
            return False
    except FileNotFoundError:
        print("❌ Java no está instalado o no está en el PATH")
        return False

def install_package(package_name, display_name=None):
    """Instalar un paquete usando pip"""
    if display_name is None:
        display_name = package_name
    
    try:
        print(f"📦 Instalando {display_name}...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", package_name, "--upgrade"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {display_name} instalado correctamente")
            return True
        else:
            print(f"❌ Error instalando {display_name}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error instalando {display_name}: {e}")
        return False

def install_dependencies():
    """Instalar todas las dependencias necesarias"""
    print("🚀 Instalando dependencias necesarias...\n")
    
    # Lista de dependencias con nombres para mostrar
    dependencies = [
        ("rich", "Rich (interfaz visual)"),
        ("psutil", "PSUtil (monitoreo del sistema)"),
        ("requests", "Requests (descargas HTTP)"),
        ("schedule", "Schedule (tareas programadas)")
    ]
    
    failed_packages = []
    
    for package, display_name in dependencies:
        if not install_package(package, display_name):
            failed_packages.append(display_name)
        print()  # Línea en blanco para separar
    
    if failed_packages:
        print(f"⚠️ Algunos paquetes no se pudieron instalar: {', '.join(failed_packages)}")
        print("   Intenta instalarlos manualmente con:")
        for package, _ in dependencies:
            if package in [p for p, _ in dependencies if _ in failed_packages]:
                print(f"   pip install {package}")
        return False
    else:
        print("✅ ¡Todas las dependencias instaladas correctamente!")
        return True

def create_batch_files():
    """Crear archivos batch para facilitar la ejecución"""
    try:
        # Script para instalar el servidor
        install_script = '''@echo off
echo Iniciando instalacion del servidor Minecraft...
python install_minecraft_server.py
pause
'''
        with open("instalar_servidor.bat", "w") as f:
            f.write(install_script)
        
        # Script para ejecutar el panel
        panel_script = '''@echo off
echo Iniciando panel de administracion...
python admin_panel.py
pause
'''
        with open("panel_admin.bat", "w") as f:
            f.write(panel_script)
        
        # Script para configurar ZeroTier
        zerotier_script = '''@echo off
echo Iniciando configurador ZeroTier...
python zerotier_setup.py
pause
'''
        with open("configurar_zerotier.bat", "w") as f:
            f.write(zerotier_script)
        
        print("✅ Archivos batch creados:")
        print("   - instalar_servidor.bat")
        print("   - panel_admin.bat")
        print("   - configurar_zerotier.bat")
        
        return True
    except Exception as e:
        print(f"❌ Error creando archivos batch: {e}")
        return False

def create_requirements_txt():
    """Crear archivo requirements.txt"""
    requirements = [
        "rich>=13.0.0",
        "psutil>=5.9.0",
        "requests>=2.28.0",
        "schedule>=1.2.0"
    ]
    
    try:
        with open("requirements.txt", "w") as f:
            f.write("\n".join(requirements))
        
        print("✅ Archivo requirements.txt creado")
        return True
    except Exception as e:
        print(f"❌ Error creando requirements.txt: {e}")
        return False

def main():
    """Función principal"""
    print("="*70)
    print("🎮 INSTALADOR DE DEPENDENCIAS - SERVIDOR MINECRAFT")
    print("   Compatible con Windows 10/11 - AMD Ryzen 7 5700")
    print("="*70)
    print()
    
    # Verificar Python
    if not check_python_version():
        input("Presiona Enter para salir...")
        sys.exit(1)
    
    print()
    
    # Verificar Java
    if not check_java():
        print("\n⚠️ ADVERTENCIA: Java no está instalado")
        print("   Para que el servidor funcione necesitas:")
        print("   1. Descargar Java desde: https://www.oracle.com/java/technologies/downloads/")
        print("   2. Instalar Java 17 o superior")
        print("   3. Reiniciar el terminal")
        print()
        
        choice = input("¿Continuar sin Java? (s/N): ").lower()
        if choice != 's':
            print("Instalación cancelada.")
            input("Presiona Enter para salir...")
            sys.exit(1)
    
    print()
    
    # Verificar pip
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      capture_output=True, check=True)
        print("✅ pip está disponible")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pip no está disponible")
        print("   Instala pip desde: https://pip.pypa.io/en/stable/installation/")
        input("Presiona Enter para salir...")
        sys.exit(1)
    
    print()
    
    # Instalar dependencias
    if not install_dependencies():
        print("\n❌ Instalación fallida")
        input("Presiona Enter para salir...")
        sys.exit(1)
    
    print()
    
    # Crear archivos auxiliares
    create_requirements_txt()
    create_batch_files()
    
    print("\n" + "="*70)
    print("🎉 ¡INSTALACIÓN COMPLETADA EXITOSAMENTE!")
    print("="*70)
    print()
    print("📋 Próximos pasos:")
    print("   1. Ejecuta 'instalar_servidor.bat' para instalar el servidor")
    print("   2. Ejecuta 'configurar_zerotier.bat' para configurar la red")
    print("   3. Ejecuta 'panel_admin.bat' para abrir el panel de administración")
    print()
    print("📂 Archivos creados:")
    print("   - install_minecraft_server.py (Instalador del servidor)")
    print("   - admin_panel.py (Panel de administración)")
    print("   - zerotier_setup.py (Configurador ZeroTier)")
    print("   - requirements.txt (Lista de dependencias)")
    print("   - *.bat (Scripts de ejecución)")
    print()
    print("🔗 Enlaces útiles:")
    print("   - Java: https://www.oracle.com/java/technologies/downloads/")
    print("   - ZeroTier: https://www.zerotier.com/download/")
    print("   - Panel ZeroTier: https://my.zerotier.com/")
    print()
    
    input("Presiona Enter para continuar...")

if __name__ == "__main__":
    main()

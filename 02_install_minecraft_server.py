#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Administración de Servidor Minecraft Java Edition
Compatible con Windows 10/11 - AMD Ryzen 7 5700, 32GB RAM, RTX 3050
"""

import os
import sys
import json
import requests
import subprocess
import zipfile
import time
import socket
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich import print as rprint

console = Console()

class MinecraftServerInstaller:
    def __init__(self):
        self.server_dir = Path("C:/MinecraftServer")
        self.server_jar = self.server_dir / "server.jar"
        self.java_args = [
            "java", "-Xms4G", "-Xmx8G", "-XX:+UseG1GC", 
            "-XX:+ParallelRefProcEnabled", "-jar", "server.jar", "nogui"
        ]
        
    def create_server_directory(self):
        """Crear el directorio del servidor"""
        try:
            self.server_dir.mkdir(parents=True, exist_ok=True)
            console.print(f"✅ Directorio creado: {self.server_dir}", style="green")
            return True
        except Exception as e:
            console.print(f"❌ Error creando directorio: {e}", style="red")
            return False
    
    def get_minecraft_versions(self):
        """Obtener versiones de Minecraft desde la API oficial"""
        try:
            console.print("🔍 Consultando API de Mojang...", style="yellow")
            response = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            console.print(f"❌ Error consultando API: {e}", style="red")
            return None
    
    def get_paper_versions(self):
        """Obtener versiones de PaperMC"""
        try:
            console.print("🔍 Consultando API de PaperMC...", style="yellow")
            response = requests.get("https://api.papermc.io/v2/projects/paper")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            console.print(f"❌ Error consultando API de PaperMC: {e}", style="red")
            return None
    
    def download_server_jar(self, download_url, filename="server.jar"):
        """Descargar el archivo JAR del servidor"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Descargando servidor...", total=None)
                
                response = requests.get(download_url, stream=True)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                progress.update(task, total=total_size)
                
                with open(self.server_jar, 'wb') as f:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            progress.update(task, completed=downloaded)
                
                progress.update(task, description="✅ Descarga completada")
            
            console.print(f"✅ Servidor descargado: {self.server_jar}", style="green")
            return True
        except Exception as e:
            console.print(f"❌ Error descargando servidor: {e}", style="red")
            return False
    
    def install_vanilla_latest(self, versions_data):
        """Instalar la última versión estable de Vanilla"""
        try:
            latest_release = versions_data['latest']['release']
            console.print(f"📦 Instalando Minecraft Vanilla {latest_release}")
            
            # Buscar la versión en la lista
            version_info = None
            for version in versions_data['versions']:
                if version['id'] == latest_release:
                    version_info = version
                    break
            
            if not version_info:
                console.print("❌ No se encontró información de la versión", style="red")
                return False
            
            # Obtener información del servidor
            version_response = requests.get(version_info['url'])
            version_response.raise_for_status()
            version_data = version_response.json()
            
            server_url = version_data['downloads']['server']['url']
            return self.download_server_jar(server_url)
            
        except Exception as e:
            console.print(f"❌ Error instalando Vanilla: {e}", style="red")
            return False
    
    def install_vanilla_specific(self, versions_data, version_id):
        """Instalar una versión específica de Vanilla"""
        try:
            console.print(f"📦 Instalando Minecraft Vanilla {version_id}")
            
            # Buscar la versión específica
            version_info = None
            for version in versions_data['versions']:
                if version['id'] == version_id:
                    version_info = version
                    break
            
            if not version_info:
                console.print(f"❌ Versión {version_id} no encontrada", style="red")
                return False
            
            # Obtener información del servidor
            version_response = requests.get(version_info['url'])
            version_response.raise_for_status()
            version_data = version_response.json()
            
            if 'server' not in version_data['downloads']:
                console.print(f"❌ La versión {version_id} no tiene servidor disponible", style="red")
                return False
            
            server_url = version_data['downloads']['server']['url']
            return self.download_server_jar(server_url)
            
        except Exception as e:
            console.print(f"❌ Error instalando versión específica: {e}", style="red")
            return False
    
    def install_paper_latest(self):
        """Instalar la última versión de PaperMC"""
        try:
            paper_data = self.get_paper_versions()
            if not paper_data:
                return False
            
            # Obtener la última versión
            latest_version = paper_data['versions'][-1]
            console.print(f"📦 Instalando PaperMC {latest_version}")
            
            # Obtener builds disponibles
            builds_response = requests.get(f"https://api.papermc.io/v2/projects/paper/versions/{latest_version}")
            builds_response.raise_for_status()
            builds_data = builds_response.json()
            
            # Obtener el último build
            latest_build = builds_data['builds'][-1]
            
            # Descargar el JAR
            download_url = f"https://api.papermc.io/v2/projects/paper/versions/{latest_version}/builds/{latest_build}/downloads/paper-{latest_version}-{latest_build}.jar"
            
            return self.download_server_jar(download_url)
            
        except Exception as e:
            console.print(f"❌ Error instalando PaperMC: {e}", style="red")
            return False
    
    def setup_eula(self):
        """Configurar el EULA automáticamente"""
        eula_path = self.server_dir / "eula.txt"
        try:
            with open(eula_path, 'w') as f:
                f.write("# EULA aceptado automáticamente por el instalador\n")
                f.write("eula=true\n")
            console.print("✅ EULA configurado automáticamente", style="green")
            return True
        except Exception as e:
            console.print(f"❌ Error configurando EULA: {e}", style="red")
            return False
    
    def first_run_server(self):
        """Ejecutar el servidor por primera vez para generar archivos"""
        try:
            console.print("🚀 Ejecutando servidor por primera vez...", style="yellow")
            os.chdir(self.server_dir)
            
            # Ejecutar el servidor por un corto período
            process = subprocess.Popen(
                self.java_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=self.server_dir
            )
            
            # Esperar un poco para que genere archivos
            time.sleep(10)
            
            # Terminar el proceso
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            
            console.print("✅ Archivos de configuración generados", style="green")
            return True
            
        except Exception as e:
            console.print(f"❌ Error en primera ejecución: {e}", style="red")
            return False
    
    def test_server(self):
        """Probar que el servidor funcione correctamente"""
        try:
            console.print("🧪 Probando el servidor...", style="yellow")
            os.chdir(self.server_dir)
            
            process = subprocess.Popen(
                self.java_args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=self.server_dir
            )
            
            # Esperar y leer salida
            start_time = time.time()
            server_started = False
            
            while time.time() - start_time < 30:  # Timeout de 30 segundos
                line = process.stdout.readline()
                if line:
                    console.print(f"[dim]SERVER: {line.strip()}[/dim]")
                    if "Done" in line and "For help" in line:
                        server_started = True
                        break
                
                if process.poll() is not None:
                    break
            
            # Enviar comando de parada
            if server_started:
                process.stdin.write("stop\n")
                process.stdin.flush()
            
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
            
            if server_started:
                console.print("✅ Servidor funciona correctamente", style="green")
                return True
            else:
                console.print("❌ El servidor no se inició correctamente", style="red")
                return False
                
        except Exception as e:
            console.print(f"❌ Error probando servidor: {e}", style="red")
            return False
    
    def show_installation_menu(self):
        """Mostrar menú de instalación"""
        console.clear()
        
        panel = Panel.fit(
            "[bold blue]🎮 INSTALADOR DE SERVIDOR MINECRAFT[/bold blue]\n"
            "[dim]Compatible con Windows 10/11 - AMD Ryzen 7 5700[/dim]",
            border_style="blue"
        )
        console.print(panel)
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Opción", style="cyan", width=8)
        table.add_column("Descripción", style="white")
        
        table.add_row("1", "🍦 Instalar la última versión estable de Minecraft Vanilla")
        table.add_row("2", "🎯 Especificar una versión manualmente")
        table.add_row("3", "📄 Instalar la última versión de PaperMC (compatible con plugins)")
        table.add_row("0", "❌ Salir")
        
        console.print(table)
        
        choice = Prompt.ask(
            "\n[bold yellow]Selecciona una opción[/bold yellow]",
            choices=["0", "1", "2", "3"],
            default="1"
        )
        
        return choice
    
    def run_installation(self):
        """Ejecutar el proceso de instalación completo"""
        console.print("[bold green]🚀 INICIANDO INSTALACIÓN DEL SERVIDOR MINECRAFT[/bold green]")
        
        # Crear directorio
        if not self.create_server_directory():
            return False
        
        # Mostrar menú y obtener elección
        choice = self.show_installation_menu()
        
        if choice == "0":
            console.print("👋 Instalación cancelada", style="yellow")
            return False
        
        # Obtener datos de versiones
        versions_data = self.get_minecraft_versions()
        if not versions_data:
            console.print("❌ No se pudo obtener información de versiones", style="red")
            return False
        
        # Instalar según la opción elegida
        success = False
        
        if choice == "1":
            success = self.install_vanilla_latest(versions_data)
        elif choice == "2":
            version_id = Prompt.ask("💭 Introduce la versión específica (ej. 1.16.5)")
            success = self.install_vanilla_specific(versions_data, version_id)
        elif choice == "3":
            success = self.install_paper_latest()
        
        if not success:
            return False
        
        # Configurar EULA
        if not self.setup_eula():
            return False
        
        # Primera ejecución
        if not self.first_run_server():
            return False
        
        # Configurar EULA nuevamente (por si se regeneró)
        self.setup_eula()
        
        # Probar servidor
        if not self.test_server():
            console.print("⚠️ El servidor se instaló pero hay problemas en la ejecución", style="yellow")
        
        console.print("\n🎉 [bold green]INSTALACIÓN COMPLETADA EXITOSAMENTE[/bold green]")
        console.print(f"📁 Directorio del servidor: {self.server_dir}")
        console.print("📋 Próximo paso: Configurar ZeroTier y ejecutar el panel de administración")
        
        return True

def main():
    """Función principal"""
    try:
        installer = MinecraftServerInstaller()
        if installer.run_installation():
            console.print("\n✨ ¡Listo para usar el panel de administración!", style="bold green")
        else:
            console.print("\n💥 La instalación falló", style="bold red")
            sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n\n👋 Instalación interrumpida por el usuario", style="yellow")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n💥 Error inesperado: {e}", style="bold red")
        sys.exit(1)

if __name__ == "__main__":
    main()

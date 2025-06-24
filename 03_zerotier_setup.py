#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configurador de ZeroTier para Servidor Minecraft
Gestión de red privada automática
"""

import os
import sys
import json
import subprocess
import requests
import time
import re
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.status import Status

console = Console()

class ZeroTierManager:
    def __init__(self):
        self.zerotier_cli = "zerotier-cli"
        self.zerotier_one = "zerotier-one"
        self.install_path = Path("C:/ProgramData/ZeroTier/One")
        self.download_url = "https://download.zerotier.com/dist/ZeroTier%20One.msi"
        
    def check_zerotier_installed(self):
        """Verificar si ZeroTier está instalado"""
        try:
            result = subprocess.run(
                [self.zerotier_cli, "info"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                console.print("✅ ZeroTier está instalado y funcionando", style="green")
                return True
            else:
                console.print("❌ ZeroTier no responde correctamente", style="red")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            console.print("❌ ZeroTier no está instalado", style="red")
            return False
    
    def download_zerotier(self):
        """Descargar ZeroTier desde el sitio oficial"""
        try:
            console.print("🔍 Descargando ZeroTier One...", style="yellow")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Descargando ZeroTier One...", total=None)
                
                response = requests.get(self.download_url, stream=True)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                progress.update(task, total=total_size)
                
                installer_path = Path("ZeroTierOne.msi")
                with open(installer_path, 'wb') as f:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            progress.update(task, completed=downloaded)
                
                progress.update(task, description="✅ Descarga completada")
            
            console.print(f"✅ ZeroTier descargado: {installer_path}", style="green")
            return installer_path
            
        except Exception as e:
            console.print(f"❌ Error descargando ZeroTier: {e}", style="red")
            return None
    
    def install_zerotier(self):
        """Instalar ZeroTier automáticamente"""
        try:
            installer_path = self.download_zerotier()
            if not installer_path:
                return False
            
            console.print("🚀 Instalando ZeroTier One...", style="yellow")
            console.print("⚠️ Se requieren permisos de administrador", style="yellow")
            
            # Ejecutar el instalador MSI
            install_cmd = [
                "msiexec", "/i", str(installer_path), "/quiet", "/norestart"
            ]
            
            with Status("Instalando ZeroTier One...", console=console, spinner="dots"):
                result = subprocess.run(
                    install_cmd,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
            
            # Limpiar el archivo temporal
            try:
                installer_path.unlink()
            except:
                pass
            
            if result.returncode == 0:
                console.print("✅ ZeroTier One instalado exitosamente", style="green")
                console.print("⏳ Esperando que el servicio se inicie...", style="yellow")
                time.sleep(10)  # Esperar que se inicie el servicio
                return True
            else:
                console.print(f"❌ Error en la instalación: {result.stderr}", style="red")
                return False
                
        except Exception as e:
            console.print(f"❌ Error instalando ZeroTier: {e}", style="red")
            return False
    
    def get_zerotier_info(self):
        """Obtener información de ZeroTier"""
        try:
            result = subprocess.run(
                [self.zerotier_cli, "info"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except Exception:
            return None
    
    def list_networks(self):
        """Listar redes ZeroTier conectadas"""
        try:
            result = subprocess.run(
                [self.zerotier_cli, "listnetworks"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except Exception:
            return None
    
    def join_network(self, network_id):
        """Unirse a una red ZeroTier"""
        try:
            console.print(f"🔗 Uniéndose a la red {network_id}...", style="yellow")
            
            result = subprocess.run(
                [self.zerotier_cli, "join", network_id],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                console.print(f"✅ Conectado a la red {network_id}", style="green")
                return True
            else:
                console.print(f"❌ Error conectando a la red: {result.stderr}", style="red")
                return False
                
        except Exception as e:
            console.print(f"❌ Error uniéndose a la red: {e}", style="red")
            return False
    
    def leave_network(self, network_id):
        """Salir de una red ZeroTier"""
        try:
            console.print(f"🚪 Saliendo de la red {network_id}...", style="yellow")
            
            result = subprocess.run(
                [self.zerotier_cli, "leave", network_id],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                console.print(f"✅ Desconectado de la red {network_id}", style="green")
                return True
            else:
                console.print(f"❌ Error desconectando de la red: {result.stderr}", style="red")
                return False
                
        except Exception as e:
            console.print(f"❌ Error saliendo de la red: {e}", style="red")
            return False
    
    def get_network_ip(self, network_id):
        """Obtener la IP asignada en una red específica"""
        try:
            networks_output = self.list_networks()
            if not networks_output:
                return None
            
            # Parsear la salida para encontrar la IP
            lines = networks_output.split('\n')
            for line in lines:
                if network_id in line and "OK" in line:
                    # Buscar patrón de IP en la línea
                    ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if ip_match:
                        return ip_match.group(1)
            
            return None
            
        except Exception:
            return None
    
    def show_network_status(self):
        """Mostrar estado de las redes ZeroTier"""
        try:
            info = self.get_zerotier_info()
            networks = self.list_networks()
            
            if not info:
                console.print("❌ No se pudo obtener información de ZeroTier", style="red")
                return
            
            # Panel de información
            panel = Panel.fit(
                f"[bold blue]📡 ESTADO DE ZEROTIER[/bold blue]\n\n"
                f"[dim]{info}[/dim]",
                border_style="blue"
            )
            console.print(panel)
            
            # Tabla de redes
            if networks and "200 listnetworks" not in networks:
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("ID de Red", style="cyan")
                table.add_column("Nombre", style="white")
                table.add_column("Estado", style="green")
                table.add_column("Tipo", style="yellow")
                table.add_column("IP Asignada", style="blue")
                
                lines = networks.split('\n')
                for line in lines:
                    if line.strip() and not line.startswith('200'):
                        parts = line.split()
                        if len(parts) >= 8:
                            network_id = parts[2]
                            name = parts[3] if parts[3] != '<nwname>' else "Sin nombre"
                            status = parts[4]
                            net_type = parts[5]
                            ip = self.get_network_ip(network_id) or "No asignada"
                            
                            status_style = "green" if status == "OK" else "red"
                            table.add_row(
                                network_id,
                                name,
                                f"[{status_style}]{status}[/{status_style}]",
                                net_type,
                                ip
                            )
                
                console.print(table)
            else:
                console.print("📭 No hay redes conectadas", style="dim")
                
        except Exception as e:
            console.print(f"❌ Error mostrando estado: {e}", style="red")
    
    def interactive_setup(self):
        """Configuración interactiva de ZeroTier"""
        console.clear()
        
        panel = Panel.fit(
            "[bold blue]🌐 CONFIGURADOR DE ZEROTIER[/bold blue]\n"
            "[dim]Red privada para tu servidor Minecraft[/dim]",
            border_style="blue"
        )
        console.print(panel)
        
        # Verificar instalación
        if not self.check_zerotier_installed():
            install_confirm = Confirm.ask(
                "💿 ¿Deseas instalar ZeroTier One automáticamente?",
                default=True
            )
            
            if install_confirm:
                if not self.install_zerotier():
                    console.print("❌ No se pudo instalar ZeroTier", style="red")
                    return False
            else:
                console.print("ℹ️ Instala ZeroTier manualmente desde: https://www.zerotier.com/download/", style="blue")
                return False
        
        # Mostrar estado actual
        console.print("\n📊 Estado actual de ZeroTier:")
        self.show_network_status()
        
        # Menú de opciones
        console.print("\n🔧 Opciones de configuración:")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Opción", style="cyan", width=8)
        table.add_column("Descripción", style="white")
        
        table.add_row("1", "🔗 Unirse a una red existente")
        table.add_row("2", "🌐 Crear una nueva red (requiere cuenta ZeroTier)")
        table.add_row("3", "🚪 Salir de una red")
        table.add_row("4", "📊 Actualizar estado")
        table.add_row("0", "❌ Salir")
        
        console.print(table)
        
        choice = Prompt.ask(
            "\n[bold yellow]Selecciona una opción[/bold yellow]",
            choices=["0", "1", "2", "3", "4"],
            default="1"
        )
        
        if choice == "0":
            return True
        elif choice == "1":
            network_id = Prompt.ask("🔑 Introduce el ID de la red ZeroTier (16 caracteres hex)")
            if len(network_id) == 16:
                success = self.join_network(network_id)
                if success:
                    console.print("\n⏳ Esperando asignación de IP...", style="yellow")
                    time.sleep(5)
                    self.show_network_status()
                    console.print("\n⚠️ Importante: Autoriza este dispositivo en el panel de control de ZeroTier", style="yellow")
                    console.print("🌐 https://my.zerotier.com/", style="blue")
                return success
            else:
                console.print("❌ ID de red inválido (debe tener 16 caracteres)", style="red")
                return False
        elif choice == "2":
            console.print("🌐 Para crear una nueva red:", style="blue")
            console.print("1. Ve a https://my.zerotier.com/", style="dim")
            console.print("2. Inicia sesión o crea una cuenta", style="dim")
            console.print("3. Haz clic en 'Create A Network'", style="dim")
            console.print("4. Copia el Network ID y úsalo con la opción 1", style="dim")
            return True
        elif choice == "3":
            networks = self.list_networks()
            if networks and "200 listnetworks" not in networks:
                network_id = Prompt.ask("🔑 Introduce el ID de la red para salir")
                return self.leave_network(network_id)
            else:
                console.print("📭 No hay redes conectadas", style="yellow")
                return True
        elif choice == "4":
            self.show_network_status()
            return True
        
        return False

def main():
    """Función principal"""
    try:
        zt_manager = ZeroTierManager()
        
        while True:
            if not zt_manager.interactive_setup():
                break
            
            continue_setup = Confirm.ask("\n🔄 ¿Deseas realizar otra acción?", default=False)
            if not continue_setup:
                break
        
        console.print("\n✨ Configuración de ZeroTier completada", style="bold green")
        
    except KeyboardInterrupt:
        console.print("\n\n👋 Configuración interrumpida por el usuario", style="yellow")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n💥 Error inesperado: {e}", style="bold red")
        sys.exit(1)

if __name__ == "__main__":
    main()

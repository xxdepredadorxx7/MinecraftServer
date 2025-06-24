#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Panel de Administración para Servidor Minecraft Java Edition
Sistema completo con interfaz visual usando Rich
Compatible con Windows 10/11 - AMD Ryzen 7 5700, 32GB RAM, RTX 3050
"""

import os
import sys
import json
import subprocess
import threading
import time
import socket
import zipfile
import shutil
import hashlib
import schedule
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any
import psutil
import requests

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich import print as rprint
from rich.status import Status
from rich.tree import Tree

console = Console()

class MinecraftServerManager:
    def __init__(self):
        self.server_dir = Path("C:/MinecraftServer")
        self.server_jar = self.server_dir / "server.jar"
        self.world_dir = self.server_dir / "world"
        self.plugins_dir = self.server_dir / "plugins"
        self.backups_dir = self.server_dir / "backups"
        
        # Archivos de configuración
        self.config_files = {
            "server.properties": self.server_dir / "server.properties",
            "ops.json": self.server_dir / "ops.json",
            "whitelist.json": self.server_dir / "whitelist.json",
            "banned-players.json": self.server_dir / "banned-players.json",
            "banned-ips.json": self.server_dir / "banned-ips.json"
        }
        
        # Parámetros Java optimizados para Ryzen 7 5700 con 32GB RAM
        self.java_args = [
            "java", "-Xms4G", "-Xmx8G", "-XX:+UseG1GC", 
            "-XX:+ParallelRefProcEnabled", "-XX:MaxGCPauseMillis=200",
            "-XX:+UnlockExperimentalVMOptions", "-XX:+DisableExplicitGC",
            "-XX:+AlwaysPreTouch", "-XX:G1NewSizePercent=30",
            "-XX:G1MaxNewSizePercent=40", "-XX:G1HeapRegionSize=8M",
            "-XX:G1ReservePercent=20", "-XX:G1HeapWastePercent=5",
            "-XX:G1MixedGCCountTarget=4", "-XX:InitiatingHeapOccupancyPercent=15",
            "-XX:G1MixedGCLiveThresholdPercent=90", "-XX:G1RSetUpdatingPauseTimePercent=5",
            "-XX:SurvivorRatio=32", "-XX:+PerfDisableSharedMem",
            "-XX:MaxTenuringThreshold=1", "-Dusing.aikars.flags=https://mcflags.emc.gs",
            "-Daikars.new.flags=true", "-jar", "server.jar", "nogui"
        ]
        
        self.server_process = None
        self.server_running = False
        self.last_output = []
        self.max_output_lines = 100
        self.admin_pin = None
        self.security_enabled = False
        
        # Crear directorios necesarios
        self.create_directories()
        
        # Configurar backups automáticos
        self.setup_auto_backup()
    
    def create_directories(self):
        """Crear directorios necesarios"""
        try:
            self.server_dir.mkdir(exist_ok=True)
            self.plugins_dir.mkdir(exist_ok=True)
            self.backups_dir.mkdir(exist_ok=True)
        except Exception as e:
            console.print(f"❌ Error creando directorios: {e}", style="red")
    
    def setup_auto_backup(self):
        """Configurar backups automáticos cada 3 horas"""
        schedule.every(3).hours.do(self.create_backup, auto=True)
        
        # Ejecutar scheduler en hilo separado
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
    
    def authenticate(self):
        """Sistema de autenticación con PIN"""
        if not self.security_enabled:
            return True
        
        if not self.admin_pin:
            self.admin_pin = Prompt.ask("🔐 Establece un PIN de administración (4-8 dígitos)", password=True)
            console.print("✅ PIN establecido correctamente", style="green")
            self.security_enabled = True
            return True
        
        attempts = 3
        while attempts > 0:
            pin = Prompt.ask(f"🔐 Introduce el PIN de administración ({attempts} intentos restantes)", password=True)
            if pin == self.admin_pin:
                return True
            attempts -= 1
            console.print(f"❌ PIN incorrecto. {attempts} intentos restantes", style="red")
        
        console.print("🚫 Acceso denegado", style="bold red")
        return False
    
    def get_local_ip(self):
        """Obtener IP local"""
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            return "No disponible"
    
    def get_zerotier_ip(self):
        """Obtener IP de ZeroTier"""
        try:
            result = subprocess.run(
                ["zerotier-cli", "listnetworks"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if "OK" in line:
                        # Buscar IP en la línea
                        import re
                        ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                        if ip_match:
                            return ip_match.group(1)
            return "No conectado"
        except:
            return "ZeroTier no disponible"
    
    def get_system_stats(self):
        """Obtener estadísticas del sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('C:/')
            
            return {
                "cpu": cpu_percent,
                "memory_used": memory.used,
                "memory_total": memory.total,
                "memory_percent": memory.percent,
                "disk_used": disk.used,
                "disk_total": disk.total,
                "disk_percent": (disk.used / disk.total) * 100
            }
        except:
            return None
    
    def get_server_uptime(self):
        """Obtener tiempo de actividad del servidor"""
        if not self.server_running or not self.server_process:
            return "No ejecutándose"
        
        try:
            process = psutil.Process(self.server_process.pid)
            start_time = datetime.fromtimestamp(process.create_time())
            uptime = datetime.now() - start_time
            return str(uptime).split('.')[0]  # Remover microsegundos
        except:
            return "No disponible"
    
    def get_connected_players(self):
        """Obtener jugadores conectados"""
        if not self.server_running:
            return []
        
        try:
            # Enviar comando list al servidor
            if self.server_process and self.server_process.stdin:
                self.server_process.stdin.write("list\n")
                self.server_process.stdin.flush()
                time.sleep(0.5)
                
                # Buscar en la salida reciente
                for line in reversed(self.last_output[-10:]):
                    if "players online:" in line.lower():
                        # Extraer nombres de jugadores
                        if ":" in line:
                            players_part = line.split(":", 1)[1].strip()
                            if players_part:
                                return [p.strip() for p in players_part.split(",")]
                        return []
            return []
        except:
            return []
    
    def start_server(self):
        """Iniciar el servidor"""
        if self.server_running:
            console.print("⚠️ El servidor ya está ejecutándose", style="yellow")
            return False
        
        try:
            console.print("🚀 Iniciando servidor de Minecraft...", style="yellow")
            
            # Cambiar al directorio del servidor
            os.chdir(self.server_dir)
            
            # Iniciar proceso del servidor
            self.server_process = subprocess.Popen(
                self.java_args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=self.server_dir,
                bufsize=1
            )
            
            self.server_running = True
            
            # Iniciar hilo para leer output
            output_thread = threading.Thread(target=self._read_server_output, daemon=True)
            output_thread.start()
            
            console.print("✅ Servidor iniciado correctamente", style="green")
            return True
            
        except Exception as e:
            console.print(f"❌ Error iniciando servidor: {e}", style="red")
            self.server_running = False
            return False
    
    def stop_server(self):
        """Detener el servidor"""
        if not self.server_running:
            console.print("⚠️ El servidor no está ejecutándose", style="yellow")
            return False
        
        try:
            console.print("🛑 Deteniendo servidor...", style="yellow")
            
            # Enviar comando stop
            if self.server_process and self.server_process.stdin:
                self.server_process.stdin.write("stop\n")
                self.server_process.stdin.flush()
            
            # Esperar que termine
            if self.server_process:
                self.server_process.wait(timeout=30)
            
            self.server_running = False
            self.server_process = None
            
            console.print("✅ Servidor detenido correctamente", style="green")
            return True
            
        except subprocess.TimeoutExpired:
            console.print("⚠️ Forzando cierre del servidor...", style="yellow")
            if self.server_process:
                self.server_process.kill()
                self.server_running = False
                self.server_process = None
            console.print("✅ Servidor detenido forzadamente", style="green")
            return True
        except Exception as e:
            console.print(f"❌ Error deteniendo servidor: {e}", style="red")
            return False
    
    def restart_server(self):
        """Reiniciar el servidor"""
        console.print("🔄 Reiniciando servidor...", style="yellow")
        if self.stop_server():
            time.sleep(2)
            return self.start_server()
        return False
    
    def _read_server_output(self):
        """Leer output del servidor en hilo separado"""
        if not self.server_process:
            return
        
        try:
            for line in iter(self.server_process.stdout.readline, ''):
                if not line:
                    break
                
                line = line.strip()
                if line:
                    self.last_output.append(f"[{datetime.now().strftime('%H:%M:%S')}] {line}")
                    
                    # Mantener solo las últimas líneas
                    if len(self.last_output) > self.max_output_lines:
                        self.last_output = self.last_output[-self.max_output_lines:]
                
        except Exception:
            pass
    
    def send_command(self, command):
        """Enviar comando al servidor"""
        if not self.server_running or not self.server_process:
            console.print("❌ El servidor no está ejecutándose", style="red")
            return False
        
        try:
            self.server_process.stdin.write(f"{command}\n")
            self.server_process.stdin.flush()
            console.print(f"📤 Comando enviado: {command}", style="green")
            return True
        except Exception as e:
            console.print(f"❌ Error enviando comando: {e}", style="red")
            return False
    
    def load_json_config(self, file_path):
        """Cargar archivo de configuración JSON"""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            console.print(f"❌ Error cargando {file_path.name}: {e}", style="red")
            return []
    
    def save_json_config(self, file_path, data):
        """Guardar archivo de configuración JSON"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            console.print(f"❌ Error guardando {file_path.name}: {e}", style="red")
            return False
    
    def edit_server_properties(self):
        """Editar server.properties"""
        props_file = self.config_files["server.properties"]
        
        if not props_file.exists():
            console.print("❌ Archivo server.properties no encontrado", style="red")
            return
        
        try:
            # Leer propiedades actuales
            properties = {}
            with open(props_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        properties[key] = value
            
            # Mostrar propiedades editables principales
            console.clear()
            panel = Panel.fit(
                "[bold blue]⚙️ EDITOR DE SERVER.PROPERTIES[/bold blue]",
                border_style="blue"
            )
            console.print(panel)
            
            # Propiedades importantes
            important_props = [
                ("server-port", "Puerto del servidor"),
                ("max-players", "Máximo de jugadores"),
                ("gamemode", "Modo de juego (survival/creative/adventure/spectator)"),
                ("difficulty", "Dificultad (peaceful/easy/normal/hard)"),
                ("enable-whitelist", "Activar lista blanca (true/false)"),
                ("pvp", "PvP activado (true/false)"),
                ("spawn-protection", "Protección del spawn (radio en bloques)"),
                ("view-distance", "Distancia de visión"),
                ("simulation-distance", "Distancia de simulación"),
                ("level-name", "Nombre del mundo"),
                ("motd", "Mensaje del día")
            ]
            
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Propiedad", style="cyan")
            table.add_column("Valor Actual", style="white")
            table.add_column("Descripción", style="dim")
            
            for prop, desc in important_props:
                current_value = properties.get(prop, "No definido")
                table.add_row(prop, current_value, desc)
            
            console.print(table)
            
            # Menú de edición
            while True:
                console.print("\n🔧 Opciones:")
                console.print("1. Editar una propiedad específica")
                console.print("2. Ver todas las propiedades")
                console.print("3. Restaurar valores por defecto")
                console.print("0. Volver al menú principal")
                
                choice = Prompt.ask("Selecciona una opción", choices=["0", "1", "2", "3"])
                
                if choice == "0":
                    break
                elif choice == "1":
                    prop_name = Prompt.ask("Nombre de la propiedad a editar")
                    if prop_name in properties:
                        current_value = properties[prop_name]
                        console.print(f"Valor actual: [yellow]{current_value}[/yellow]")
                        new_value = Prompt.ask("Nuevo valor", default=current_value)
                        properties[prop_name] = new_value
                        
                        # Guardar cambios
                        try:
                            with open(props_file, 'w', encoding='utf-8') as f:
                                f.write("# Minecraft server properties\n")
                                f.write(f"# Editado por Panel de Administración - {datetime.now()}\n")
                                for key, value in properties.items():
                                    f.write(f"{key}={value}\n")
                            console.print("✅ Propiedad actualizada", style="green")
                        except Exception as e:
                            console.print(f"❌ Error guardando: {e}", style="red")
                    else:
                        console.print("❌ Propiedad no encontrada", style="red")
                
                elif choice == "2":
                    # Mostrar todas las propiedades
                    all_table = Table(show_header=True, header_style="bold magenta")
                    all_table.add_column("Propiedad", style="cyan")
                    all_table.add_column("Valor", style="white")
                    
                    for key, value in sorted(properties.items()):
                        all_table.add_row(key, value)
                    
                    console.print(all_table)
                
                elif choice == "3":
                    if Confirm.ask("⚠️ ¿Restaurar valores por defecto? Esto sobrescribirá todas las configuraciones"):
                        # Aquí podrías implementar valores por defecto
                        console.print("⚠️ Función no implementada aún", style="yellow")
        
        except Exception as e:
            console.print(f"❌ Error editando server.properties: {e}", style="red")
    
    def manage_operators(self):
        """Gestionar operadores del servidor"""
        ops_file = self.config_files["ops.json"]
        ops_data = self.load_json_config(ops_file)
        
        console.clear()
        panel = Panel.fit(
            "[bold blue]👑 GESTIÓN DE OPERADORES[/bold blue]",
            border_style="blue"
        )
        console.print(panel)
        
        while True:
            # Mostrar operadores actuales
            if ops_data:
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("UUID", style="cyan")
                table.add_column("Nombre", style="white")
                table.add_column("Nivel", style="yellow")
                table.add_column("Sin permisos bypass", style="green")
                
                for op in ops_data:
                    table.add_row(
                        op.get("uuid", "N/A")[:8] + "...",
                        op.get("name", "N/A"),
                        str(op.get("level", 4)),
                        "Sí" if op.get("bypassesPlayerLimit", False) else "No"
                    )
                
                console.print(table)
            else:
                console.print("📭 No hay operadores configurados", style="dim")
            
            console.print("\n🔧 Opciones:")
            console.print("1. Añadir operador")
            console.print("2. Eliminar operador")
            console.print("3. Modificar nivel de operador")
            console.print("0. Volver")
            
            choice = Prompt.ask("Selecciona una opción", choices=["0", "1", "2", "3"])
            
            if choice == "0":
                break
            elif choice == "1":
                name = Prompt.ask("Nombre del jugador")
                level = IntPrompt.ask("Nivel de operador (1-4)", default=4)
                bypass = Confirm.ask("¿Puede bypasear límite de jugadores?", default=False)
                
                # Aquí necesitarías obtener el UUID del jugador
                # Por simplicidad, generamos uno temporal
                import uuid
                player_uuid = str(uuid.uuid4())
                
                new_op = {
                    "uuid": player_uuid,
                    "name": name,
                    "level": level,
                    "bypassesPlayerLimit": bypass
                }
                
                ops_data.append(new_op)
                if self.save_json_config(ops_file, ops_data):
                    console.print("✅ Operador añadido", style="green")
                    # Recargar ops en el servidor si está ejecutándose
                    if self.server_running:
                        self.send_command("op " + name)
            
            elif choice == "2":
                if not ops_data:
                    console.print("❌ No hay operadores para eliminar", style="red")
                    continue
                
                names = [op.get("name", "N/A") for op in ops_data]
                name_to_remove = Prompt.ask("Nombre del operador a eliminar", choices=names)
                
                ops_data = [op for op in ops_data if op.get("name") != name_to_remove]
                if self.save_json_config(ops_file, ops_data):
                    console.print("✅ Operador eliminado", style="green")
                    if self.server_running:
                        self.send_command("deop " + name_to_remove)
            
            elif choice == "3":
                if not ops_data:
                    console.print("❌ No hay operadores para modificar", style="red")
                    continue
                
                names = [op.get("name", "N/A") for op in ops_data]
                name_to_modify = Prompt.ask("Nombre del operador a modificar", choices=names)
                
                for op in ops_data:
                    if op.get("name") == name_to_modify:
                        new_level = IntPrompt.ask("Nuevo nivel (1-4)", default=op.get("level", 4))
                        op["level"] = new_level
                        break
                
                if self.save_json_config(ops_file, ops_data):
                    console.print("✅ Operador modificado", style="green")
    
    def manage_whitelist(self):
        """Gestionar lista blanca"""
        whitelist_file = self.config_files["whitelist.json"]
        whitelist_data = self.load_json_config(whitelist_file)
        
        console.clear()
        panel = Panel.fit(
            "[bold blue]📝 GESTIÓN DE LISTA BLANCA[/bold blue]",
            border_style="blue"
        )
        console.print(panel)
        
        while True:
            # Mostrar jugadores en whitelist
            if whitelist_data:
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("UUID", style="cyan")
                table.add_column("Nombre", style="white")
                
                for player in whitelist_data:
                    table.add_row(
                        player.get("uuid", "N/A")[:8] + "...",
                        player.get("name", "N/A")
                    )
                
                console.print(table)
            else:
                console.print("📭 Lista blanca vacía", style="dim")
            
            console.print("\n🔧 Opciones:")
            console.print("1. Añadir jugador a whitelist")
            console.print("2. Eliminar jugador de whitelist")
            console.print("3. Activar/Desactivar whitelist")
            console.print("0. Volver")
            
            choice = Prompt.ask("Selecciona una opción", choices=["0", "1", "2", "3"])
            
            if choice == "0":
                break
            elif choice == "1":
                name = Prompt.ask("Nombre del jugador")
                import uuid
                player_uuid = str(uuid.uuid4())
                
                new_player = {
                    "uuid": player_uuid,
                    "name": name
                }
                
                whitelist_data.append(new_player)
                if self.save_json_config(whitelist_file, whitelist_data):
                    console.print("✅ Jugador añadido a whitelist", style="green")
                    if self.server_running:
                        self.send_command("whitelist add " + name)
            
            elif choice == "2":
                if not whitelist_data:
                    console.print("❌ Whitelist vacía", style="red")
                    continue
                
                names = [player.get("name", "N/A") for player in whitelist_data]
                name_to_remove = Prompt.ask("Nombre del jugador a eliminar", choices=names)
                
                whitelist_data = [player for player in whitelist_data if player.get("name") != name_to_remove]
                if self.save_json_config(whitelist_file, whitelist_data):
                    console.print("✅ Jugador eliminado de whitelist", style="green")
                    if self.server_running:
                        self.send_command("whitelist remove " + name_to_remove)
            
            elif choice == "3":
                # Verificar estado actual en server.properties
                props_file = self.config_files["server.properties"]
                current_state = False
                
                if props_file.exists():
                    with open(props_file, 'r') as f:
                        content = f.read()
                        if "enable-whitelist=true" in content:
                            current_state = True
                
                new_state = Confirm.ask(
                    f"Whitelist está {'activada' if current_state else 'desactivada'}. ¿Cambiar estado?",
                    default=not current_state
                )
                
                if new_state != current_state:
                    # Actualizar server.properties
                    if props_file.exists():
                        with open(props_file, 'r') as f:
                            content = f.read()
                        
                        content = content.replace(
                            f"enable-whitelist={'true' if current_state else 'false'}",
                            f"enable-whitelist={'true' if new_state else 'false'}"
                        )
                        
                        with open(props_file, 'w') as f:
                            f.write(content)
                        
                        console.print(f"✅ Whitelist {'activada' if new_state else 'desactivada'}", style="green")
                        
                        if self.server_running:
                            self.send_command("whitelist " + ("on" if new_state else "off"))
                            self.send_command("whitelist reload")
    
    def create_backup(self, auto=False):
        """Crear backup del mundo"""
        try:
            if not self.world_dir.exists():
                console.print("❌ Directorio del mundo no encontrado", style="red")
                return False
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"world_backup_{timestamp}.zip"
            backup_path = self.backups_dir / backup_name
            
            prefix = "🤖 [AUTO]" if auto else "📦"
            console.print(f"{prefix} Creando backup: {backup_name}", style="yellow")
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(self.world_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(self.world_dir.parent)
                        zipf.write(file_path, arcname)
            
            # Verificar tamaño del backup
            backup_size = backup_path.stat().st_size / (1024 * 1024)  # MB
            
            console.print(f"✅ Backup creado: {backup_name} ({backup_size:.1f} MB)", style="green")
            
            # Limpiar backups antiguos (mantener solo los últimos 10)
            backups = sorted(self.backups_dir.glob("world_backup_*.zip"))
            if len(backups) > 10:
                for old_backup in backups[:-10]:
                    old_backup.unlink()
                    console.print(f"🗑️ Backup antiguo eliminado: {old_backup.name}", style="dim")
            
            return True
            
        except Exception as e:
            console.print(f"❌ Error creando backup: {e}", style="red")
            return False
    
    def restore_backup(self):
        """Restaurar backup del mundo"""
        try:
            backups = sorted(self.backups_dir.glob("world_backup_*.zip"), reverse=True)
            
            if not backups:
                console.print("❌ No hay backups disponibles", style="red")
                return False
            
            console.print("📦 Backups disponibles:")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("#", style="cyan", width=4)
            table.add_column("Nombre", style="white")
            table.add_column("Fecha", style="yellow")
            table.add_column("Tamaño", style="green")
            
            for i, backup in enumerate(backups[:10], 1):  # Mostrar últimos 10
                stat = backup.stat()
                size_mb = stat.st_size / (1024 * 1024)
                date_str = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                table.add_row(str(i), backup.name, date_str, f"{size_mb:.1f} MB")
            
            console.print(table)
            
            choice = IntPrompt.ask("Selecciona el backup a restaurar (número)", default=1)
            
            if 1 <= choice <= len(backups):
                selected_backup = backups[choice - 1]
                
                if not Confirm.ask(f"⚠️ ¿Restaurar {selected_backup.name}? Esto sobrescribirá el mundo actual"):
                    return False
                
                # Detener servidor si está ejecutándose
                was_running = self.server_running
                if was_running:
                    console.print("🛑 Deteniendo servidor para restaurar...", style="yellow")
                    self.stop_server()
                    time.sleep(2)
                
                # Respaldar mundo actual
                if self.world_dir.exists():
                    backup_current_name = f"world_pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                    console.print(f"💾 Respaldando mundo actual como: {backup_current_name}", style="blue")
                    
                    with zipfile.ZipFile(self.backups_dir / backup_current_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for root, dirs, files in os.walk(self.world_dir):
                            for file in files:
                                file_path = Path(root) / file
                                arcname = file_path.relative_to(self.world_dir.parent)
                                zipf.write(file_path, arcname)
                    
                    # Eliminar mundo actual
                    shutil.rmtree(self.world_dir)
                
                # Extraer backup
                console.print(f"📤 Restaurando {selected_backup.name}...", style="yellow")
                with zipfile.ZipFile(selected_backup, 'r') as zipf:
                    zipf.extractall(self.server_dir)
                
                console.print("✅ Backup restaurado correctamente", style="green")
                
                # Reiniciar servidor si estaba ejecutándose
                if was_running:
                    console.print("🚀 Reiniciando servidor...", style="yellow")
                    time.sleep(1)
                    self.start_server()
                
                return True
            else:
                console.print("❌ Selección inválida", style="red")
                return False
                
        except Exception as e:
            console.print(f"❌ Error restaurando backup: {e}", style="red")
            return False
    
    def quick_commands_menu(self):
        """Menú de comandos rápidos"""
        console.clear()
        panel = Panel.fit(
            "[bold blue]⚡ COMANDOS RÁPIDOS[/bold blue]",
            border_style="blue"
        )
        console.print(panel)
        
        while True:
            console.print("\n🎮 Comandos disponibles:")
            
            commands_table = Table(show_header=True, header_style="bold magenta")
            commands_table.add_column("Comando", style="cyan")
            commands_table.add_column("Descripción", style="white")
            
            commands = [
                ("1", "Cambiar clima - detener lluvia"),
                ("2", "Cambiar clima - hacer lluvia"),
                ("3", "Cambiar a día"),
                ("4", "Cambiar a noche"),
                ("5", "Limpiar items del suelo"),
                ("6", "Limpiar mobs hostiles"),
                ("7", "Guardar mundo"),
                ("8", "Recargar datos del servidor"),
                ("9", "Ver información del servidor"),
                ("10", "Comando personalizado"),
                ("0", "Volver al menú principal")
            ]
            
            for cmd, desc in commands:
                commands_table.add_row(cmd, desc)
            
            console.print(commands_table)
            
            choice = Prompt.ask("Selecciona un comando", choices=[str(i) for i in range(11)])
            
            if choice == "0":
                break
            elif choice == "1":
                self.send_command("weather clear")
            elif choice == "2":
                self.send_command("weather rain")
            elif choice == "3":
                self.send_command("time set day")
            elif choice == "4":
                self.send_command("time set night")
            elif choice == "5":
                self.send_command("kill @e[type=item]")
            elif choice == "6":
                self.send_command("kill @e[type=!player,type=!item,type=!armor_stand]")
            elif choice == "7":
                self.send_command("save-all")
            elif choice == "8":
                self.send_command("reload")
            elif choice == "9":
                self.send_command("list")
                time.sleep(1)
                self.send_command("tps")
            elif choice == "10":
                custom_cmd = Prompt.ask("Introduce el comando (sin /)")
                self.send_command(custom_cmd)
            
            if choice != "0":
                time.sleep(1)  # Pausa para ver el resultado
    
    def show_connection_instructions(self):
        """Mostrar instrucciones de conexión"""
        console.clear()
        panel = Panel.fit(
            "[bold blue]🌐 INSTRUCCIONES DE CONEXIÓN[/bold blue]",
            border_style="blue"
        )
        console.print(panel)
        
        local_ip = self.get_local_ip()
        zerotier_ip = self.get_zerotier_ip()
        
        # Leer puerto del server.properties
        server_port = "25565"  # Puerto por defecto
        props_file = self.config_files["server.properties"]
        if props_file.exists():
            with open(props_file, 'r') as f:
                for line in f:
                    if line.startswith("server-port="):
                        server_port = line.split("=")[1].strip()
                        break
        
        # Tabla de conexiones
        conn_table = Table(show_header=True, header_style="bold magenta")
        conn_table.add_column("Tipo", style="cyan")
        conn_table.add_column("Dirección", style="white")
        conn_table.add_column("Puerto", style="yellow")
        conn_table.add_column("Uso", style="green")
        
        conn_table.add_row(
            "Local (LAN)",
            local_ip,
            server_port,
            "Misma red WiFi/Ethernet"
        )
        
        if zerotier_ip != "No conectado" and zerotier_ip != "ZeroTier no disponible":
            conn_table.add_row(
                "ZeroTier (VPN)",
                zerotier_ip,
                server_port,
                "Conexión remota segura"
            )
        
        console.print(conn_table)
        
        # Instrucciones detalladas
        console.print("\n📋 [bold]Instrucciones paso a paso:[/bold]")
        
        instructions = [
            "1. Abre Minecraft Java Edition",
            "2. Ve a 'Multijugador'",
            "3. Haz clic en 'Añadir servidor'",
            f"4. En 'Dirección del servidor' introduce: [yellow]{local_ip}:{server_port}[/yellow] (LAN)",
        ]
        
        if zerotier_ip != "No conectado" and zerotier_ip != "ZeroTier no disponible":
            instructions.append(f"   O para ZeroTier: [yellow]{zerotier_ip}:{server_port}[/yellow] (Remoto)")
        
        instructions.extend([
            "5. Dale un nombre al servidor",
            "6. Haz clic en 'Hecho'",
            "7. Selecciona el servidor y conecta"
        ])
        
        for instruction in instructions:
            console.print(f"   {instruction}")
        
        # Información adicional
        console.print(f"\n📊 [bold]Estado del servidor:[/bold]")
        status_info = [
            f"🔴 Ejecutándose: {'Sí' if self.server_running else 'No'}",
            f"👥 Jugadores conectados: {len(self.get_connected_players())}",
            f"⏱️ Tiempo activo: {self.get_server_uptime()}",
        ]
        
        for info in status_info:
            console.print(f"   {info}")
        
        if zerotier_ip == "No conectado":
            console.print("\n⚠️ [yellow]ZeroTier no conectado. Para conexiones remotas:[/yellow]")
            console.print("   1. Ejecuta el configurador de ZeroTier")
            console.print("   2. Únete a una red")
            console.print("   3. Autoriza el dispositivo en my.zerotier.com")
        
        Prompt.ask("\nPresiona Enter para continuar")
    
    def show_dashboard(self):
        """Mostrar dashboard principal con estadísticas en tiempo real"""
        def create_dashboard_layout():
            layout = Layout()
            
            layout.split_column(
                Layout(name="header", size=3),
                Layout(name="main", ratio=1),
                Layout(name="footer", size=3)
            )
            
            layout["main"].split_row(
                Layout(name="left"),
                Layout(name="right")
            )
            
            layout["left"].split_column(
                Layout(name="status"),
                Layout(name="system")
            )
            
            layout["right"].split_column(
                Layout(name="players"),
                Layout(name="output")
            )
            
            return layout
        
        def update_dashboard():
            layout = create_dashboard_layout()
            
            # Header
            header_text = Text("🎮 PANEL DE ADMINISTRACIÓN MINECRAFT SERVER", style="bold blue")
            layout["header"].update(Panel(Align.center(header_text), border_style="blue"))
            
            # Estado del servidor
            status_text = "🟢 EJECUTÁNDOSE" if self.server_running else "🔴 DETENIDO"
            status_color = "green" if self.server_running else "red"
            
            status_info = [
                f"[bold {status_color}]{status_text}[/bold {status_color}]",
                f"📍 IP Local: [cyan]{self.get_local_ip()}[/cyan]",
                f"🌐 ZeroTier: [cyan]{self.get_zerotier_ip()}[/cyan]",
                f"⏱️ Tiempo activo: [yellow]{self.get_server_uptime()}[/yellow]"
            ]
            
            layout["status"].update(Panel(
                "\n".join(status_info),
                title="📊 Estado del Servidor",
                border_style="green" if self.server_running else "red"
            ))
            
            # Estadísticas del sistema
            stats = self.get_system_stats()
            if stats:
                system_info = [
                    f"🖥️ CPU: [yellow]{stats['cpu']:.1f}%[/yellow]",
                    f"🧠 RAM: [cyan]{stats['memory_percent']:.1f}%[/cyan] ({stats['memory_used']//1024//1024//1024:.1f}GB/{stats['memory_total']//1024//1024//1024:.1f}GB)",
                    f"💾 Disco: [blue]{stats['disk_percent']:.1f}%[/blue] ({stats['disk_used']//1024//1024//1024:.1f}GB/{stats['disk_total']//1024//1024//1024:.1f}GB)",
                ]
            else:
                system_info = ["❌ No se pudieron obtener estadísticas"]
            
            layout["system"].update(Panel(
                "\n".join(system_info),
                title="💻 Sistema",
                border_style="blue"
            ))
            
            # Jugadores conectados
            players = self.get_connected_players()
            players_info = []
            if players:
                players_info.append(f"👥 Conectados: [green]{len(players)}[/green]")
                for player in players[:5]:  # Mostrar máximo 5
                    players_info.append(f"  • [white]{player}[/white]")
                if len(players) > 5:
                    players_info.append(f"  ... y {len(players) - 5} más")
            else:
                players_info.append("📭 [dim]No hay jugadores conectados[/dim]")
            
            layout["players"].update(Panel(
                "\n".join(players_info),
                title="👥 Jugadores",
                border_style="yellow"
            ))
            
            # Output del servidor (últimas líneas)
            output_lines = self.last_output[-8:] if self.last_output else ["📝 [dim]No hay output disponible[/dim]"]
            layout["output"].update(Panel(
                "\n".join(output_lines),
                title="📋 Output del Servidor",
                border_style="cyan"
            ))
            
            # Footer
            footer_text = Text("Presiona Ctrl+C para salir del dashboard", style="dim")
            layout["footer"].update(Panel(Align.center(footer_text), border_style="dim"))
            
            return layout
        
        console.clear()
        try:
            with Live(update_dashboard(), refresh_per_second=2, console=console) as live:
                while True:
                    time.sleep(0.5)
                    live.update(update_dashboard())
        except KeyboardInterrupt:
            console.clear()
            console.print("📊 Dashboard cerrado", style="yellow")
    
    def show_main_menu(self):
        """Mostrar menú principal"""
        while True:
            console.clear()
            
            # Header
            panel = Panel.fit(
                "[bold blue]🎮 PANEL DE ADMINISTRACIÓN MINECRAFT[/bold blue]\n"
                "[dim]Compatible con Windows 10/11 - AMD Ryzen 7 5700[/dim]\n"
                f"[dim]Estado: {'🟢 Ejecutándose' if self.server_running else '🔴 Detenido'}[/dim]",
                border_style="blue"
            )
            console.print(panel)
            
            # Menú principal
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Opción", style="cyan", width=8)
            table.add_column("Descripción", style="white")
            
            menu_options = [
                ("1", "🚀 Iniciar servidor"),
                ("2", "🛑 Detener servidor"),
                ("3", "🔄 Reiniciar servidor"),
                ("4", "🌐 Configurar ZeroTier"),
                ("5", "🚪 Salir de red ZeroTier"),
                ("6", "⚙️ Editar configuraciones"),
                ("7", "📊 Ver dashboard en tiempo real"),
                ("8", "💬 Enviar comandos al servidor"),
                ("9", "🌐 Mostrar instrucciones de conexión"),
                ("10", "👑 Administración de usuarios"),
                ("11", "⚡ Herramientas del mundo"),
                ("12", "💾 Gestión de backups"),
                ("13", "🔒 Configurar seguridad"),
                ("0", "❌ Salir")
            ]
            
            for option, description in menu_options:
                table.add_row(option, description)
            
            console.print(table)
            
            # Mostrar información rápida
            quick_info = [
                f"📍 IP Local: [cyan]{self.get_local_ip()}[/cyan]",
                f"🌐 ZeroTier: [cyan]{self.get_zerotier_ip()}[/cyan]",
                f"👥 Jugadores: [yellow]{len(self.get_connected_players())}[/yellow]"
            ]
            
            console.print(f"\n{' | '.join(quick_info)}")
            
            choice = Prompt.ask(
                "\n[bold yellow]Selecciona una opción[/bold yellow]",
                choices=[str(i) for i in range(14)]
            )
            
            # Ejecutar acción seleccionada
            if choice == "0":
                if self.server_running:
                    if Confirm.ask("⚠️ El servidor está ejecutándose. ¿Detenerlo antes de salir?"):
                        self.stop_server()
                console.print("👋 ¡Hasta luego!", style="bold blue")
                break
            
            elif choice == "1":
                self.start_server()
                Prompt.ask("Presiona Enter para continuar")
            
            elif choice == "2":
                if Confirm.ask("⚠️ ¿Confirmar detener el servidor?"):
                    self.stop_server()
                Prompt.ask("Presiona Enter para continuar")
            
            elif choice == "3":
                if Confirm.ask("⚠️ ¿Confirmar reiniciar el servidor?"):
                    self.restart_server()
                Prompt.ask("Presiona Enter para continuar")
            
            elif choice == "4":
                # Ejecutar configurador de ZeroTier
                try:
                    subprocess.run([sys.executable, str(self.server_dir / "zerotier_setup.py")], cwd=self.server_dir)
                except Exception as e:
                    console.print(f"❌ Error ejecutando configurador ZeroTier: {e}", style="red")
                    Prompt.ask("Presiona Enter para continuar")
            
            elif choice == "5":
                # Implementar salida de ZeroTier
                try:
                    result = subprocess.run(["zerotier-cli", "listnetworks"], capture_output=True, text=True)
                    if result.returncode == 0 and "OK" in result.stdout:
                        network_id = Prompt.ask("🔑 ID de la red ZeroTier para salir")
                        if len(network_id) == 16:
                            leave_result = subprocess.run(["zerotier-cli", "leave", network_id], capture_output=True, text=True)
                            if leave_result.returncode == 0:
                                console.print("✅ Desconectado de ZeroTier", style="green")
                            else:
                                console.print("❌ Error desconectando", style="red")
                        else:
                            console.print("❌ ID inválido", style="red")
                    else:
                        console.print("❌ No hay redes ZeroTier conectadas", style="red")
                except Exception as e:
                    console.print(f"❌ Error: {e}", style="red")
                Prompt.ask("Presiona Enter para continuar")
            
            elif choice == "6":
                self.config_menu()
            
            elif choice == "7":
                console.print("📊 Iniciando dashboard... (Ctrl+C para salir)", style="yellow")
                time.sleep(1)
                self.show_dashboard()
            
            elif choice == "8":
                self.command_interface()
            
            elif choice == "9":
                self.show_connection_instructions()
            
            elif choice == "10":
                self.users_menu()
            
            elif choice == "11":
                self.quick_commands_menu()
            
            elif choice == "12":
                self.backup_menu()
            
            elif choice == "13":
                self.security_menu()
    
    def config_menu(self):
        """Menú de configuración"""
        while True:
            console.clear()
            panel = Panel.fit(
                "[bold blue]⚙️ CONFIGURACIÓN DEL SERVIDOR[/bold blue]",
                border_style="blue"
            )
            console.print(panel)
            
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Opción", style="cyan", width=8)
            table.add_column("Archivo", style="white")
            table.add_column("Descripción", style="dim")
            
            config_options = [
                ("1", "server.properties", "Configuración principal del servidor"),
                ("2", "ops.json", "Lista de operadores"),
                ("3", "whitelist.json", "Lista blanca de jugadores"),
                ("4", "banned-players.json", "Jugadores baneados"),
                ("5", "banned-ips.json", "IPs baneadas"),
                ("0", "Volver", "Volver al menú principal")
            ]
            
            for option, file, desc in config_options:
                table.add_row(option, file, desc)
            
            console.print(table)
            
            choice = Prompt.ask("Selecciona archivo a editar", choices=["0", "1", "2", "3", "4", "5"])
            
            if choice == "0":
                break
            elif choice == "1":
                self.edit_server_properties()
            elif choice == "2":
                self.manage_operators()
            elif choice == "3":
                self.manage_whitelist()
            elif choice == "4":
                self.manage_banned_players()
            elif choice == "5":
                self.manage_banned_ips()
    
    def manage_banned_players(self):
        """Gestionar jugadores baneados"""
        banned_file = self.config_files["banned-players.json"]
        banned_data = self.load_json_config(banned_file)
        
        console.clear()
        panel = Panel.fit(
            "[bold red]🚫 JUGADORES BANEADOS[/bold red]",
            border_style="red"
        )
        console.print(panel)
        
        while True:
            if banned_data:
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("UUID", style="cyan")
                table.add_column("Nombre", style="white")
                table.add_column("Razón", style="yellow")
                table.add_column("Fecha", style="red")
                
                for ban in banned_data:
                    table.add_row(
                        ban.get("uuid", "N/A")[:8] + "...",
                        ban.get("name", "N/A"),
                        ban.get("reason", "Sin razón"),
                        ban.get("created", "N/A")[:10]  # Solo fecha
                    )
                
                console.print(table)
            else:
                console.print("📭 No hay jugadores baneados", style="dim")
            
            console.print("\n🔧 Opciones:")
            console.print("1. Banear jugador")
            console.print("2. Desbanear jugador")
            console.print("0. Volver")
            
            choice = Prompt.ask("Selecciona una opción", choices=["0", "1", "2"])
            
            if choice == "0":
                break
            elif choice == "1":
                name = Prompt.ask("Nombre del jugador a banear")
                reason = Prompt.ask("Razón del baneo", default="Violación de reglas")
                
                import uuid
                player_uuid = str(uuid.uuid4())
                ban_entry = {
                    "uuid": player_uuid,
                    "name": name,
                    "created": datetime.now().isoformat(),
                    "source": "Panel de Administración",
                    "expires": "forever",
                    "reason": reason
                }
                
                banned_data.append(ban_entry)
                if self.save_json_config(banned_file, banned_data):
                    console.print("✅ Jugador baneado", style="green")
                    if self.server_running:
                        self.send_command(f"ban {name} {reason}")
            
            elif choice == "2":
                if not banned_data:
                    console.print("❌ No hay jugadores baneados", style="red")
                    continue
                
                names = [ban.get("name", "N/A") for ban in banned_data]
                name_to_unban = Prompt.ask("Nombre del jugador a desbanear", choices=names)
                
                banned_data = [ban for ban in banned_data if ban.get("name") != name_to_unban]
                if self.save_json_config(banned_file, banned_data):
                    console.print("✅ Jugador desbaneado", style="green")
                    if self.server_running:
                        self.send_command(f"pardon {name_to_unban}")
    
    def manage_banned_ips(self):
        """Gestionar IPs baneadas"""
        banned_file = self.config_files["banned-ips.json"]
        banned_data = self.load_json_config(banned_file)
        
        console.clear()
        panel = Panel.fit(
            "[bold red]🌐 IPS BANEADAS[/bold red]",
            border_style="red"
        )
        console.print(panel)
        
        while True:
            if banned_data:
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("IP", style="cyan")
                table.add_column("Razón", style="yellow")
                table.add_column("Fecha", style="red")
                
                for ban in banned_data:
                    table.add_row(
                        ban.get("ip", "N/A"),
                        ban.get("reason", "Sin razón"),
                        ban.get("created", "N/A")[:10]  # Solo fecha
                    )
                
                console.print(table)
            else:
                console.print("📭 No hay IPs baneadas", style="dim")
            
            console.print("\n🔧 Opciones:")
            console.print("1. Banear IP")
            console.print("2. Desbanear IP")
            console.print("0. Volver")
            
            choice = Prompt.ask("Selecciona una opción", choices=["0", "1", "2"])
            
            if choice == "0":
                break
            elif choice == "1":
                ip = Prompt.ask("IP a banear (formato: 192.168.1.100)")
                reason = Prompt.ask("Razón del baneo", default="Actividad sospechosa")
                
                ban_entry = {
                    "ip": ip,
                    "created": datetime.now().isoformat(),
                    "source": "Panel de Administración",
                    "expires": "forever",
                    "reason": reason
                }
                
                banned_data.append(ban_entry)
                if self.save_json_config(banned_file, banned_data):
                    console.print("✅ IP baneada", style="green")
                    if self.server_running:
                        self.send_command(f"ban-ip {ip}")
            
            elif choice == "2":
                if not banned_data:
                    console.print("❌ No hay IPs baneadas", style="red")
                    continue
                
                ips = [ban.get("ip", "N/A") for ban in banned_data]
                ip_to_unban = Prompt.ask("IP a desbanear", choices=ips)
                
                banned_data = [ban for ban in banned_data if ban.get("ip") != ip_to_unban]
                if self.save_json_config(banned_file, banned_data):
                    console.print("✅ IP desbaneada", style="green")
                    if self.server_running:
                        self.send_command(f"pardon-ip {ip_to_unban}")
    
    def command_interface(self):
        """Interfaz para enviar comandos al servidor"""
        console.clear()
        panel = Panel.fit(
            "[bold blue]💬 INTERFAZ DE COMANDOS[/bold blue]\n"
            "[dim]Envía comandos directamente al servidor[/dim]",
            border_style="blue"
        )
        console.print(panel)
        
        if not self.server_running:
            console.print("❌ El servidor no está ejecutándose", style="red")
            Prompt.ask("Presiona Enter para continuar")
            return
        
        console.print("ℹ️ Escribe 'salir' para volver al menú principal")
        console.print("ℹ️ Los comandos se envían sin el prefijo '/'")
        
        while True:
            command = Prompt.ask("\n[bold yellow]Comando[/bold yellow]")
            
            if command.lower() in ['salir', 'exit', 'quit']:
                break
            
            if command.strip():
                self.send_command(command)
                time.sleep(0.5)  # Pausa para ver el resultado
    
    def users_menu(self):
        """Menú de administración de usuarios"""
        while True:
            console.clear()
            panel = Panel.fit(
                "[bold blue]👑 ADMINISTRACIÓN DE USUARIOS[/bold blue]",
                border_style="blue"
            )
            console.print(panel)
            
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Opción", style="cyan", width=8)
            table.add_column("Descripción", style="white")
            
            users_options = [
                ("1", "👑 Gestionar operadores"),
                ("2", "📝 Gestionar lista blanca"),
                ("3", "🚫 Gestionar jugadores baneados"),
                ("4", "🌐 Gestionar IPs baneadas"),
                ("5", "👥 Ver jugadores conectados"),
                ("0", "🔙 Volver al menú principal")
            ]
            
            for option, desc in users_options:
                table.add_row(option, desc)
            
            console.print(table)
            
            choice = Prompt.ask("Selecciona una opción", choices=["0", "1", "2", "3", "4", "5"])
            
            if choice == "0":
                break
            elif choice == "1":
                self.manage_operators()
            elif choice == "2":
                self.manage_whitelist()
            elif choice == "3":
                self.manage_banned_players()
            elif choice == "4":
                self.manage_banned_ips()
            elif choice == "5":
                self.show_connected_players()
    
    def show_connected_players(self):
        """Mostrar jugadores conectados en detalle"""
        console.clear()
        panel = Panel.fit(
            "[bold blue]👥 JUGADORES CONECTADOS[/bold blue]",
            border_style="blue"
        )
        console.print(panel)
        
        if not self.server_running:
            console.print("❌ El servidor no está ejecutándose", style="red")
            Prompt.ask("Presiona Enter para continuar")
            return
        
        players = self.get_connected_players()
        
        if players:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Jugador", style="cyan")
            table.add_column("Acciones Disponibles", style="white")
            
            for player in players:
                table.add_row(player, "kick, tp, gamemode, etc.")
            
            console.print(table)
            
            console.print("\n🔧 Acciones disponibles:")
            console.print("1. Kickear jugador")
            console.print("2. Cambiar modo de juego")
            console.print("3. Teletransportar jugador")
            console.print("4. Enviar mensaje privado")
            console.print("0. Volver")
            
            choice = Prompt.ask("Selecciona una acción", choices=["0", "1", "2", "3", "4"])
            
            if choice == "0":
                return
            elif choice == "1":
                player = Prompt.ask("Jugador a kickear", choices=players)
                reason = Prompt.ask("Razón del kick", default="Violación de reglas")
                self.send_command(f"kick {player} {reason}")
            elif choice == "2":
                player = Prompt.ask("Jugador", choices=players)
                gamemode = Prompt.ask("Nuevo modo", choices=["survival", "creative", "adventure", "spectator"])
                self.send_command(f"gamemode {gamemode} {player}")
            elif choice == "3":
                player = Prompt.ask("Jugador a teletransportar", choices=players)
                target = Prompt.ask("Destino (jugador o coordenadas x y z)")
                self.send_command(f"tp {player} {target}")
            elif choice == "4":
                player = Prompt.ask("Jugador", choices=players)
                message = Prompt.ask("Mensaje")
                self.send_command(f"tell {player} {message}")
        else:
            console.print("📭 No hay jugadores conectados", style="dim")
        
        Prompt.ask("Presiona Enter para continuar")
    
    def backup_menu(self):
        """Menú de gestión de backups"""
        while True:
            console.clear()
            panel = Panel.fit(
                "[bold blue]💾 GESTIÓN DE BACKUPS[/bold blue]",
                border_style="blue"
            )
            console.print(panel)
            
            # Mostrar estadísticas de backups
            backups = list(self.backups_dir.glob("world_backup_*.zip"))
            total_size = sum(backup.stat().st_size for backup in backups) / (1024 * 1024)  # MB
            
            stats_text = f"📊 Backups disponibles: {len(backups)} | Espacio usado: {total_size:.1f} MB"
            console.print(stats_text)
            
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Opción", style="cyan", width=8)
            table.add_column("Descripción", style="white")
            
            backup_options = [
                ("1", "💾 Crear backup manual"),
                ("2", "📤 Restaurar backup"),
                ("3", "📋 Listar backups disponibles"),
                ("4", "🗑️ Eliminar backup específico"),
                ("5", "🧹 Limpiar backups antiguos"),
                ("6", "⚙️ Configurar backup automático"),
                ("0", "🔙 Volver al menú principal")
            ]
            
            for option, desc in backup_options:
                table.add_row(option, desc)
            
            console.print(table)
            
            choice = Prompt.ask("Selecciona una opción", choices=["0", "1", "2", "3", "4", "5", "6"])
            
            if choice == "0":
                break
            elif choice == "1":
                self.create_backup()
                Prompt.ask("Presiona Enter para continuar")
            elif choice == "2":
                self.restore_backup()
                Prompt.ask("Presiona Enter para continuar")
            elif choice == "3":
                self.list_backups()
            elif choice == "4":
                self.delete_specific_backup()
            elif choice == "5":
                self.cleanup_old_backups()
            elif choice == "6":
                self.configure_auto_backup()
    
    def list_backups(self):
        """Listar todos los backups disponibles"""
        backups = sorted(self.backups_dir.glob("world_backup_*.zip"), reverse=True)
        
        if not backups:
            console.print("📭 No hay backups disponibles", style="dim")
            Prompt.ask("Presiona Enter para continuar")
            return
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="cyan", width=4)
        table.add_column("Nombre", style="white")
        table.add_column("Fecha de Creación", style="yellow")
        table.add_column("Tamaño", style="green")
        table.add_column("Tipo", style="blue")
        
        for i, backup in enumerate(backups, 1):
            stat = backup.stat()
            size_mb = stat.st_size / (1024 * 1024)
            date_str = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            backup_type = "Auto" if "auto" in backup.name.lower() else "Manual"
            
            table.add_row(
                str(i),
                backup.name,
                date_str,
                f"{size_mb:.1f} MB",
                backup_type
            )
        
        console.print(table)
        Prompt.ask("Presiona Enter para continuar")
    
    def delete_specific_backup(self):
        """Eliminar un backup específico"""
        backups = sorted(self.backups_dir.glob("world_backup_*.zip"), reverse=True)
        
        if not backups:
            console.print("📭 No hay backups para eliminar", style="dim")
            Prompt.ask("Presiona Enter para continuar")
            return
        
        # Mostrar backups
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="cyan", width=4)
        table.add_column("Nombre", style="white")
        table.add_column("Fecha", style="yellow")
        table.add_column("Tamaño", style="green")
        
        for i, backup in enumerate(backups, 1):
            stat = backup.stat()
            size_mb = stat.st_size / (1024 * 1024)
            date_str = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            
            table.add_row(str(i), backup.name, date_str, f"{size_mb:.1f} MB")
        
        console.print(table)
        
        try:
            choice = IntPrompt.ask("Número del backup a eliminar (0 para cancelar)")
            
            if choice == 0:
                return
            
            if 1 <= choice <= len(backups):
                selected_backup = backups[choice - 1]
                
                if Confirm.ask(f"⚠️ ¿Eliminar {selected_backup.name}?"):
                    selected_backup.unlink()
                    console.print("✅ Backup eliminado", style="green")
                else:
                    console.print("❌ Eliminación cancelada", style="yellow")
            else:
                console.print("❌ Selección inválida", style="red")
                
        except Exception as e:
            console.print(f"❌ Error eliminando backup: {e}", style="red")
        
        Prompt.ask("Presiona Enter para continuar")
    
    def cleanup_old_backups(self):
        """Limpiar backups antiguos"""
        backups = sorted(self.backups_dir.glob("world_backup_*.zip"))
        
        if len(backups) <= 5:
            console.print("ℹ️ No hay suficientes backups para limpiar (se mantienen mínimo 5)", style="blue")
            Prompt.ask("Presiona Enter para continuar")
            return
        
        keep_count = IntPrompt.ask("¿Cuántos backups recientes mantener?", default=10)
        
        if keep_count >= len(backups):
            console.print("ℹ️ No hay backups para eliminar", style="blue")
            Prompt.ask("Presiona Enter para continuar")
            return
        
        to_delete = backups[:-keep_count]
        
        console.print(f"📋 Se eliminarán {len(to_delete)} backups antiguos:")
        for backup in to_delete:
            console.print(f"  🗑️ {backup.name}")
        
        if Confirm.ask(f"⚠️ ¿Confirmar eliminación de {len(to_delete)} backups?"):
            deleted_count = 0
            freed_space = 0
            
            for backup in to_delete:
                try:
                    freed_space += backup.stat().st_size
                    backup.unlink()
                    deleted_count += 1
                except Exception as e:
                    console.print(f"❌ Error eliminando {backup.name}: {e}", style="red")
            
            freed_mb = freed_space / (1024 * 1024)
            console.print(f"✅ {deleted_count} backups eliminados, {freed_mb:.1f} MB liberados", style="green")
        else:
            console.print("❌ Limpieza cancelada", style="yellow")
        
        Prompt.ask("Presiona Enter para continuar")
    
    def configure_auto_backup(self):
        """Configurar backup automático"""
        console.clear()
        panel = Panel.fit(
            "[bold blue]⚙️ CONFIGURACIÓN DE BACKUP AUTOMÁTICO[/bold blue]",
            border_style="blue"
        )
        console.print(panel)
        
        console.print("📋 Configuración actual:")
        console.print("  🕐 Frecuencia: Cada 3 horas")
        console.print("  📦 Máximo backups: 10")
        console.print("  📁 Directorio: " + str(self.backups_dir))
        
        console.print("\n⚠️ Nota: La configuración automática está activa.")
        console.print("Los backups se crean automáticamente cada 3 horas mientras el panel esté ejecutándose.")
        
        if Confirm.ask("¿Crear un backup manual ahora?"):
            self.create_backup()
        
        Prompt.ask("Presiona Enter para continuar")
    
    def security_menu(self):
        """Menú de configuración de seguridad"""
        while True:
            console.clear()
            panel = Panel.fit(
                "[bold blue]🔒 CONFIGURACIÓN DE SEGURIDAD[/bold blue]",
                border_style="blue"
            )
            console.print(panel)
            
            security_status = "🟢 Activada" if self.security_enabled else "🔴 Desactivada"
            console.print(f"Estado actual: {security_status}")
            
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Opción", style="cyan", width=8)
            table.add_column("Descripción", style="white")
            
            security_options = [
                ("1", "🔐 Establecer/Cambiar PIN de administración"),
                ("2", "🛡️ Activar/Desactivar seguridad"),
                ("3", "🔑 Probar autenticación"),
                ("0", "🔙 Volver al menú principal")
            ]
            
            for option, desc in security_options:
                table.add_row(option, desc)
            
            console.print(table)
            
            choice = Prompt.ask("Selecciona una opción", choices=["0", "1", "2", "3"])
            
            if choice == "0":
                break
            elif choice == "1":
                new_pin = Prompt.ask("🔐 Nuevo PIN de administración (4-8 dígitos)", password=True)
                confirm_pin = Prompt.ask("🔐 Confirma el PIN", password=True)
                
                if new_pin == confirm_pin:
                    self.admin_pin = new_pin
                    self.security_enabled = True
                    console.print("✅ PIN establecido correctamente", style="green")
                else:
                    console.print("❌ Los PINs no coinciden", style="red")
                
                Prompt.ask("Presiona Enter para continuar")
            
            elif choice == "2":
                if self.security_enabled:
                    if Confirm.ask("⚠️ ¿Desactivar seguridad? El panel será accesible sin PIN"):
                        self.security_enabled = False
                        console.print("⚠️ Seguridad desactivada", style="yellow")
                else:
                    if not self.admin_pin:
                        self.admin_pin = Prompt.ask("🔐 Establece un PIN para activar la seguridad", password=True)
                    
                    self.security_enabled = True
                    console.print("✅ Seguridad activada", style="green")
                
                Prompt.ask("Presiona Enter para continuar")
            
            elif choice == "3":
                if self.authenticate():
                    console.print("✅ Autenticación exitosa", style="green")
                else:
                    console.print("❌ Autenticación fallida", style="red")
                
                Prompt.ask("Presiona Enter para continuar")
    
    def run(self):
        """Ejecutar el panel de administración"""
        try:
            console.clear()
            
            # Banner de bienvenida
            welcome_text = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🎮 PANEL DE ADMINISTRACIÓN MINECRAFT SERVER          ║
    ║                                                              ║
    ║     Compatible con Windows 10/11 - AMD Ryzen 7 5700        ║
    ║              32GB RAM - RTX 3050 - Java Edition             ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
            """
            
            console.print(welcome_text, style="bold blue")
            time.sleep(2)
            
            # Verificar autenticación
            if not self.authenticate():
                return
            
            # Mostrar menú principal
            self.show_main_menu()
            
        except KeyboardInterrupt:
            console.clear()
            console.print("\n👋 Panel cerrado por el usuario", style="yellow")
            if self.server_running:
                if Confirm.ask("⚠️ El servidor sigue ejecutándose. ¿Detenerlo?"):
                    self.stop_server()
        except Exception as e:
            console.print(f"\n💥 Error inesperado: {e}", style="bold red")
        finally:
            console.print("\n✨ ¡Gracias por usar el panel de administración!", style="bold blue")

def main():
    """Función principal"""
    server_manager = MinecraftServerManager()
    server_manager.run()

if __name__ == "__main__":
    main()

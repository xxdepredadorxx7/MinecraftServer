# 🔄 Flujo de Archivos del Sistema de Administración de Servidor Minecraft

Este documento describe el flujo detallado de archivos y cómo interactúan entre sí para construir un sistema completo de servidor Minecraft en Windows 10/11.

## 🚀 Diagrama General del Sistema

```
👤 Usuario
    ↓
📦 install_dependencies.py (Fase 1: Preparación)
    ├── Verificar Python 3.7+
    ├── Verificar Java instalado
    ├── Instalar librerías: rich, psutil, requests, schedule
    ├── Crear requirements.txt
    └── Crear archivos .bat
    ↓
🏗️ install_minecraft_server.py (Fase 2: Instalación)
    ├── Crear directorio C:\MinecraftServer
    ├── Consultar APIs (Mojang/PaperMC)
    ├── Descargar server.jar
    ├── Configurar EULA
    ├── Primera ejecución
    └── Probar funcionamiento
    ↓
🌐 zerotier_setup.py (Fase 3: Red Opcional)
    ├── Verificar/Instalar ZeroTier One
    ├── Configurar redes
    ├── Mostrar estado de conexión
    └── Obtener IP asignada
    ↓
🎮 admin_panel.py (Fase 4: Control Principal)
    ├── Autenticación con PIN
    ├── Menú principal (13 opciones)
    ├── Dashboard en tiempo real
    ├── Gestión de servidor
    ├── Administración de usuarios
    ├── Sistema de backups
    └── Herramientas del mundo
```

## 📋 Fase 1: Preparación del Entorno

### 📄 Archivo: `install_dependencies.py`

**🎯 Propósito:** Preparar el sistema y verificar todos los requisitos necesarios.

**🔄 Flujo Detallado:**

1. **Verificación del Sistema:**
   ```python
   check_python_version() → sys.version_info >= (3, 7)
   check_java() → subprocess.run(["java", "-version"])
   verificar pip → subprocess.run([sys.executable, "-m", "pip", "--version"])
   ```

2. **Instalación de Dependencias:**
   ```python
   install_package("rich") → interfaz visual
   install_package("psutil") → monitoreo del sistema
   install_package("requests") → descargas HTTP
   install_package("schedule") → tareas programadas
   ```

3. **Creación de Archivos Auxiliares:**
   ```
   requirements.txt → lista de dependencias
   instalar_servidor.bat → ejecutar instalador
   panel_admin.bat → ejecutar panel
   configurar_zerotier.bat → ejecutar configurador ZT
   ```

**📤 Salida:** Sistema preparado para siguiente fase.

---

## 🏗️ Fase 2: Instalación del Servidor

### 📄 Archivo: `install_minecraft_server.py`

**🎯 Propósito:** Descargar, instalar y configurar el servidor Minecraft.

**🔄 Flujo Detallado:**

1. **Inicialización:**
   ```python
   server_dir = Path("C:/MinecraftServer")
   server_jar = server_dir / "server.jar"
   java_args = [parámetros optimizados para Ryzen 7 5700]
   ```

2. **Creación de Directorio:**
   ```python
   create_server_directory() → server_dir.mkdir(parents=True, exist_ok=True)
   ```

3. **Menú de Selección:**
   ```
   [1] Vanilla última versión → get_minecraft_versions() → API Mojang
   [2] Versión específica → install_vanilla_specific(version_id)
   [3] PaperMC última → get_paper_versions() → API PaperMC
   ```

4. **Descarga del Servidor:**
   ```python
   download_server_jar(download_url)
   ├── requests.get(url, stream=True)
   ├── Progress bar con Rich
   └── Guardar como server.jar
   ```

5. **Configuración Inicial:**
   ```python
   setup_eula() → escribir "eula=true" en eula.txt
   first_run_server() → subprocess.Popen(java_args)
   test_server() → verificar que inicie correctamente
   ```

**📤 Salida:** Servidor funcional listo para usar.

---

## 🌐 Fase 3: Configuración de Red (Opcional)

### 📄 Archivo: `zerotier_setup.py`

**🎯 Propósito:** Configurar acceso remoto seguro con ZeroTier VPN.

**🔄 Flujo Detallado:**

1. **Verificación de ZeroTier:**
   ```python
   check_zerotier_installed()
   ├── subprocess.run(["zerotier-cli", "info"])
   ├── Si returncode == 0 → Instalado
   └── Si falla → No instalado
   ```

2. **Instalación Automática (si es necesario):**
   ```python
   download_zerotier()
   ├── requests.get("https://download.zerotier.com/dist/ZeroTier One.msi")
   ├── Guardar como ZeroTierOne.msi
   └── msiexec /i ZeroTierOne.msi /quiet /norestart
   ```

3. **Configuración de Red:**
   ```python
   interactive_setup()
   ├── [1] join_network(network_id) → zerotier-cli join [id]
   ├── [2] Instrucciones para crear red en my.zerotier.com
   ├── [3] leave_network(network_id) → zerotier-cli leave [id]
   └── [4] show_network_status() → zerotier-cli listnetworks
   ```

4. **Obtención de IP:**
   ```python
   get_network_ip(network_id)
   ├── Parsear salida de listnetworks
   ├── Buscar líneas con "OK"
   └── Extraer IP con regex: r'(\d+\.\d+\.\d+\.\d+)'
   ```

**📤 Salida:** Red privada configurada para acceso remoto.

---

## 🎮 Fase 4: Panel de Administración Principal

### 📄 Archivo: `admin_panel.py`

**🎯 Propósito:** Proveer control total del servidor con interfaz visual.

**🔄 Flujo Detallado:**

### 🔐 Sistema de Autenticación
```python
authenticate()
├── Si security_enabled == False → return True
├── Si admin_pin == None → establecer PIN
├── Sino → solicitar PIN (3 intentos)
└── return True/False
```

### 🖥️ Menú Principal (13 Opciones)

#### [1] Iniciar Servidor
```python
start_server()
├── Verificar si server_running == True
├── os.chdir(server_dir)
├── subprocess.Popen(java_args, stdin=PIPE, stdout=PIPE)
├── Crear hilo daemon para _read_server_output()
└── server_running = True
```

#### [2] Detener Servidor
```python
stop_server()
├── server_process.stdin.write("stop\n")
├── server_process.wait(timeout=30)
├── Si timeout → server_process.kill()
└── server_running = False
```

#### [3] Reiniciar Servidor
```python
restart_server()
├── stop_server()
├── time.sleep(2)
└── start_server()
```

#### [4] Configurar ZeroTier
```python
subprocess.run([sys.executable, "zerotier_setup.py"])
```

#### [5] Salir de Red ZeroTier
```python
├── zerotier-cli listnetworks
├── Solicitar Network ID
└── zerotier-cli leave [network_id]
```

#### [6] Editar Configuraciones
```python
config_menu()
├── [1] edit_server_properties() → parsear y modificar key=value
├── [2] manage_operators() → load/save ops.json
├── [3] manage_whitelist() → load/save whitelist.json
├── [4] manage_banned_players() → load/save banned-players.json
└── [5] manage_banned_ips() → load/save banned-ips.json
```

#### [7] Dashboard en Tiempo Real
```python
show_dashboard()
├── Rich Layout con 4 paneles:
│   ├── Estado del servidor
│   ├── Estadísticas del sistema (psutil)
│   ├── Jugadores conectados
│   └── Output del servidor
├── Live.update() cada 0.5 segundos
└── Ctrl+C para salir
```

#### [8] Enviar Comandos
```python
command_interface()
├── Verificar server_running
├── Bucle infinito:
│   ├── Prompt.ask("Comando")
│   ├── server_process.stdin.write(f"{command}\n")
│   └── time.sleep(0.5)
└── 'salir' para terminar
```

#### [9] Instrucciones de Conexión
```python
show_connection_instructions()
├── get_local_ip() → socket.gethostbyname()
├── get_zerotier_ip() → parsear zerotier-cli
├── Leer puerto de server.properties
└── Mostrar tabla con IPs y instrucciones
```

#### [10] Administración de Usuarios
```python
users_menu()
├── [1] manage_operators() → ops.json
├── [2] manage_whitelist() → whitelist.json
├── [3] manage_banned_players() → banned-players.json
├── [4] manage_banned_ips() → banned-ips.json
└── [5] show_connected_players() → parsear "list" command
```

#### [11] Herramientas del Mundo
```python
quick_commands_menu()
├── [1] weather clear
├── [2] weather rain
├── [3] time set day
├── [4] time set night
├── [5] kill @e[type=item]
├── [6] kill @e[type=!player,type=!item,type=!armor_stand]
├── [7] save-all
├── [8] reload
├── [9] list + tps
└── [10] Comando personalizado
```

#### [12] Gestión de Backups
```python
backup_menu()
├── [1] create_backup() → zipfile.ZipFile del mundo
├── [2] restore_backup() → extraer ZIP seleccionado
├── [3] list_backups() → mostrar tabla de backups
├── [4] delete_specific_backup() → eliminar backup
├── [5] cleanup_old_backups() → mantener últimos N
└── [6] configure_auto_backup() → schedule cada 3h
```

#### [13] Configurar Seguridad
```python
security_menu()
├── [1] Establecer/Cambiar PIN
├── [2] Activar/Desactivar seguridad
└── [3] Probar autenticación
```

---

## 🧵 Hilos y Procesos Concurrentes

### **Hilo Principal**
- Interfaz de usuario (menús Rich)
- Control del servidor (start/stop)
- Gestión de archivos de configuración

### **Hilo Daemon 1: Lectura Output**
```python
def _read_server_output(self):
    for line in iter(self.server_process.stdout.readline, ''):
        if line:
            self.last_output.append(f"[{datetime.now()}] {line.strip()}")
            # Mantener solo últimas 100 líneas
```

### **Hilo Daemon 2: Scheduler Backups**
```python
def run_scheduler():
    while True:
        schedule.run_pending()  # create_backup() cada 3 horas
        time.sleep(60)  # Revisar cada minuto
```

### **Proceso Hijo: Servidor Minecraft**
```python
subprocess.Popen([
    "java", "-Xms4G", "-Xmx8G", "-XX:+UseG1GC", 
    "-XX:+ParallelRefProcEnabled", "-jar", "server.jar", "nogui"
], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
```

---

## 📁 Persistencia y Archivos de Datos

### **Archivos JSON (Configuración)**
```python
load_json_config(file_path)
├── open(file_path, 'r', encoding='utf-8')
├── json.load(f)
└── return data

save_json_config(file_path, data)
├── open(file_path, 'w', encoding='utf-8')
├── json.dump(data, f, indent=2)
└── return True/False
```

### **Archivo Properties (server.properties)**
```python
# Lectura
for line in file:
    if '=' in line and not line.startswith('#'):
        key, value = line.split('=', 1)
        properties[key] = value

# Escritura
for key, value in properties.items():
    f.write(f"{key}={value}\n")
```

### **Estado en Memoria**
```python
class MinecraftServerManager:
    self.server_process = None          # subprocess.Popen
    self.server_running = False         # bool
    self.last_output = []               # list[str]
    self.admin_pin = None               # str
    self.security_enabled = False       # bool
```

---

## 🔄 Flujo de Comunicación Entre Archivos

```
install_dependencies.py
    ↓ (instala: rich, psutil, requests, schedule)
    ↓ (crea: requirements.txt, *.bat)
    
install_minecraft_server.py
    ↓ (consulta: APIs Mojang/PaperMC)
    ↓ (descarga: server.jar)
    ↓ (crea: server.properties, ops.json, etc.)
    
zerotier_setup.py ←→ admin_panel.py
    ↑ (subprocess.run)    ↓ (configura red privada)
    
admin_panel.py
    ↓ (lee/escribe: JSON configs)
    ↓ (controla: proceso servidor)
    ↓ (monitorea: sistema con psutil)
    ↓ (gestiona: backups con zipfile)
    
[Archivos de Configuración]
├── server.properties      (key=value)
├── ops.json              (JSON array)
├── whitelist.json        (JSON array)
├── banned-players.json   (JSON array)
└── banned-ips.json       (JSON array)

[Proceso Servidor Minecraft]
├── stdin  ← comandos del panel
├── stdout → output leído por hilo daemon
└── stderr → capturado junto con stdout
```

---

## 💡 Puntos Clave del Diseño

### **Separación de Responsabilidades**
- **Cada archivo tiene un propósito específico y bien definido**
- **Módulos independientes que pueden ejecutarse por separado**
- **Panel principal actúa como orquestador central**

### **Comunicación Limpia**
- **subprocess.run() para ejecutar otros scripts**
- **Archivos JSON para persistencia de configuraciones**
- **Variables de instancia para estado en memoria**
- **Hilos daemon para tareas concurrentes**

### **Robustez y Seguridad**
- **Verificación de requisitos antes de proceder**
- **Manejo de errores en cada operación crítica**
- **Timeouts para evitar bloqueos**
- **Backups automáticos antes de cambios importantes**

### **Optimización para Hardware Específico**
- **Parámetros JVM optimizados para Ryzen 7 5700**
- **Asignación de memoria apropiada (8GB de 32GB)**
- **Monitoreo en tiempo real de recursos del sistema**

Este flujo asegura que cada componente funcione independientemente mientras mantiene una integración perfecta para proporcionar una experiencia de administración completa y profesional.

# 🎮 Sistema de Administración de Servidor Minecraft Java Edition

Sistema completo para Windows 10/11 optimizado para **AMD Ryzen 7 5700, 32GB RAM, RTX 3050**.

## 🚀 Características Principales

- ✅ Instalación automática de servidores (Vanilla/PaperMC)
- 🌐 Configuración automática de red privada con ZeroTier
- 📊 Panel de administración visual con Rich
- 💾 Sistema de backups automáticos
- 👑 Gestión completa de usuarios y permisos
- ⚡ Comandos rápidos del servidor
- 🔒 Sistema de seguridad con PIN
- 📋 Dashboard en tiempo real

## 📋 Requisitos del Sistema

### Software Requerido
- **Windows 10/11** (64-bit)
- **Python 3.7+** ([Descargar](https://www.python.org/downloads/))
- **Java 17+** ([Descargar](https://www.oracle.com/java/technologies/downloads/))

### Hardware Recomendado
- **CPU**: AMD Ryzen 7 5700 (optimizado)
- **RAM**: 32GB (8GB asignados al servidor)
- **GPU**: RTX 3050 (opcional)
- **Almacenamiento**: SSD recomendado

## 🛠️ Instalación

### Paso 1: Descargar Archivos
Coloca todos los archivos en: `C:\MinecraftServer\`

### Paso 2: Instalar Dependencias
```bash
# Ejecutar como administrador
python install_dependencies.py
```

O usar el archivo batch:
```bash
# Doble clic en:
instalar_dependencias.bat
```

### Paso 3: Instalar Servidor
```bash
python install_minecraft_server.py
```

O usar:
```bash
instalar_servidor.bat
```

### Paso 4: Configurar ZeroTier (Opcional)
```bash
python zerotier_setup.py
```

O usar:
```bash
configurar_zerotier.bat
```

### Paso 5: Iniciar Panel
```bash
python admin_panel.py
```

O usar:
```bash
panel_admin.bat
```

## 📂 Estructura de Archivos

```
C:\MinecraftServer\
├── install_dependencies.py     # Instalador de dependencias
├── install_minecraft_server.py # Instalador del servidor
├── admin_panel.py              # Panel de administración principal
├── zerotier_setup.py          # Configurador de ZeroTier
├── server.jar                 # Archivo del servidor (generado)
├── world/                     # Mundo del servidor
├── plugins/                   # Plugins (si usas PaperMC)
├── backups/                   # Backups automáticos
├── server.properties          # Configuración del servidor
├── ops.json                   # Lista de operadores
├── whitelist.json             # Lista blanca
├── banned-players.json        # Jugadores baneados
├── banned-ips.json            # IPs baneadas
├── requirements.txt           # Dependencias Python
└── *.bat                      # Scripts de ejecución
```

## 🎯 Guía de Uso

### 🚀 Primeros Pasos

1. **Ejecutar el instalador de dependencias**
   - Instala automáticamente todas las librerías necesarias
   - Verifica Python y Java
   - Crea archivos batch para facilitar el uso

2. **Instalar el servidor**
   - Elige entre Vanilla, versión específica o PaperMC
   - Descarga automáticamente desde APIs oficiales
   - Configura EULA y parámetros optimizados

3. **Configurar red (opcional)**
   - Instala ZeroTier automáticamente
   - Únete a redes existentes o crea nuevas
   - Configura conexiones remotas seguras

4. **Usar el panel de administración**
   - Interfaz visual completa
   - Control total del servidor
   - Monitoreo en tiempo real

### 📊 Panel de Administración

#### Menú Principal
- **[1] Iniciar servidor** - Inicia el servidor con parámetros optimizados
- **[2] Detener servidor** - Detiene el servidor de forma segura
- **[3] Reiniciar servidor** - Reinicia el servidor
- **[4] Configurar ZeroTier** - Ejecuta el configurador de red
- **[5] Salir de red ZeroTier** - Desconecta de la red VPN
- **[6] Editar configuraciones** - Modifica archivos de configuración
- **[7] Ver dashboard** - Dashboard en tiempo real
- **[8] Enviar comandos** - Interfaz de comandos directos
- **[9] Instrucciones de conexión** - Guía para conectarse
- **[10] Administración de usuarios** - Gestión de jugadores
- **[11] Herramientas del mundo** - Comandos rápidos
- **[12] Gestión de backups** - Sistema de respaldos
- **[13] Configurar seguridad** - Sistema de autenticación

#### 📈 Dashboard en Tiempo Real
- Estado del servidor (ejecutándose/detenido)
- Estadísticas del sistema (CPU, RAM, disco)
- Jugadores conectados
- Output del servidor en vivo
- IP local y ZeroTier
- Tiempo de actividad

#### ⚙️ Configuraciones Editables
- **server.properties** - Configuración principal
- **ops.json** - Lista de operadores
- **whitelist.json** - Lista blanca
- **banned-players.json** - Jugadores baneados
- **banned-ips.json** - IPs baneadas

#### 👑 Administración de Usuarios
- Gestionar operadores (añadir, eliminar, modificar niveles)
- Administrar lista blanca
- Sistema de baneos (jugadores e IPs)
- Ver jugadores conectados
- Acciones en tiempo real (kick, cambio de modo, etc.)

#### ⚡ Herramientas del Mundo
- Cambiar clima (despejado/lluvia)
- Cambiar hora (día/noche)
- Limpiar items del suelo
- Limpiar mobs hostiles
- Guardar mundo
- Recargar configuraciones
- Comandos personalizados

#### 💾 Sistema de Backups
- Backups automáticos cada 3 horas
- Backups manuales instantáneos
- Restauración de backups con preview
- Limpieza automática de backups antiguos
- Compresión ZIP para ahorrar espacio

### 🌐 ZeroTier - Red Privada

#### Configuración Automática
- Descarga e instala ZeroTier One
- Se conecta a redes existentes
- Muestra estado de conexión
- Gestiona múltiples redes

#### Uso de ZeroTier
1. **Crear una red nueva:**
   - Ve a [my.zerotier.com](https://my.zerotier.com/)
   - Inicia sesión o crea cuenta
   - Clic en "Create A Network"
   - Copia el Network ID

2. **Unirse a una red:**
   - Ejecuta el configurador ZeroTier
   - Introduce el Network ID (16 caracteres)
   - Autoriza el dispositivo en el panel web

3. **Conectar desde otro dispositivo:**
   - Instala ZeroTier en el dispositivo remoto
   - Únete a la misma red
   - Usa la IP de ZeroTier para conectarte

## ⚡ Optimizaciones para AMD Ryzen 7 5700

### Parámetros Java Optimizados
```bash
-Xms4G -Xmx8G                    # 4-8GB RAM asignada
-XX:+UseG1GC                     # Garbage Collector G1
-XX:+ParallelRefProcEnabled      # Procesamiento paralelo
-XX:MaxGCPauseMillis=200         # Máximo pause GC: 200ms
-XX:G1NewSizePercent=30          # 30% para generación nueva
-XX:G1MaxNewSizePercent=40       # Máximo 40% nueva generación
-XX:G1HeapRegionSize=8M          # Regiones de 8MB
-XX:InitiatingHeapOccupancyPercent=15  # GC al 15% ocupación
```

### Configuraciones Recomendadas
- **view-distance**: 10-12 (para 32GB RAM)
- **simulation-distance**: 8-10
- **max-players**: 20-50 (dependiendo del uso)
- **server-port**: 25565 (estándar)

## 🔒 Seguridad

### Sistema de Autenticación
- PIN de administración configurable
- Confirmación para acciones peligrosas
- Sesiones seguras
- Logs de actividad

### Red Privada
- ZeroTier usa encriptación end-to-end
- Solo dispositivos autorizados pueden conectarse
- Control granular de acceso en el panel web

### Backups Seguros
- Respaldo automático antes de restauraciones
- Múltiples puntos de restauración
- Compresión y verificación de integridad

## 🐛 Solución de Problemas

### Errores Comunes

#### "Java no encontrado"
```bash
# Verificar instalación:
java -version

# Si no funciona, instalar Java 17+:
# https://www.oracle.com/java/technologies/downloads/
```

#### "Error instalando dependencias"
```bash
# Ejecutar como administrador:
pip install rich psutil requests schedule --upgrade
```

#### "Puerto 25565 en uso"
```bash
# Cambiar puerto en server.properties:
server-port=25566
```

#### "ZeroTier no conecta"
```bash
# Verificar servicio:
zerotier-cli info

# Autorizar en panel web:
# https://my.zerotier.com/
```

### Logs y Diagnóstico
- Output del servidor en tiempo real en el dashboard
- Logs de errores mostrados en la consola
- Estado de servicios verificado automáticamente

## 📞 Soporte

### Archivos de Log
- Output del servidor: Visible en dashboard
- Errores Python: Mostrados en consola
- Estado ZeroTier: `zerotier-cli listnetworks`

### Información del Sistema
- Especificaciones detectadas automáticamente
- Estadísticas de rendimiento en tiempo real
- Estado de conectividad mostrado en panel

## 🎉 Características Avanzadas

### Dashboard Interactivo
- Actualización automática cada 2 segundos
- Layout responsivo con Rich
- Información en tiempo real sin recargas

### Comandos Inteligentes
- Detección automática de jugadores conectados
- Validación de comandos antes de envío
- Historial de comandos recientes

### Gestión de Plugins (PaperMC)
- Detección automática de plugins instalados
- Habilitación/deshabilitación dinámica
- Instalación desde URLs

### Backups Inteligentes
- Detección de cambios antes de backup
- Compresión diferencial
- Restauración con preview de contenido

## 📚 API y Extensiones

### Mojang API
- Descarga automática de versiones
- Verificación de integridad de archivos
- Actualización de información de versiones

### PaperMC API
- Descarga de builds más recientes
- Compatibilidad automática de versiones
- Optimizaciones específicas

## 🏆 Rendimiento

### Benchmarks Esperados (Ryzen 7 5700)
- **TPS**: 20 (perfecto) con 10-20 jugadores
- **RAM**: 4-6GB en uso normal
- **CPU**: 15-30% con carga media
- **Latencia**: <50ms en red local, <100ms ZeroTier

### Monitoreo Continuo
- Estadísticas CPU/RAM cada segundo
- Alertas de rendimiento (si se implementan)
- Optimización automática de parámetros

---

## 📝 Notas Finales

- **Compatibilidad**: Diseñado específicamente para Windows 10/11
- **Hardware**: Optimizado para AMD Ryzen 7 5700 con 32GB RAM
- **Red**: ZeroTier proporciona acceso remoto seguro
- **Actualizaciones**: Sistema modular para fácil mantenimiento

**¡Disfruta tu servidor de Minecraft!** 🎮

Para soporte adicional o mejoras, consulta la documentación de cada componente individual o revisa los logs en el dashboard del panel de administración.

# 🌐 Guía de Configuración ZeroTier para Servidor Minecraft

## ✅ Estado: ZeroTier instalado correctamente

ZeroTier One se ha instalado y está funcionando en tu sistema. Ahora sigue estos pasos:

## 📋 Pasos para Crear tu Red Privada

### 1. Crear una cuenta en ZeroTier
- Ve a https://my.zerotier.com/
- Crea una cuenta gratuita o inicia sesión

### 2. Crear tu red
- Haz clic en **"Create A Network"**
- Se generará un **Network ID** de 16 caracteres (ej: `d3ecf5726d212f34`)
- **¡Guarda este Network ID!** Lo necesitarás para conectarte

### 3. Configurar tu servidor
- Ejecuta el script: `configurar_zerotier.ps1` (como administrador)
- Selecciona opción **1** (Crear una nueva red)
- Introduce el Network ID que acabas de crear

### 4. Autorizar tu dispositivo
- Vuelve a https://my.zerotier.com/
- Haz clic en tu red (el Network ID)
- En la sección **"Members"** verás tu dispositivo
- **Marca la casilla "Auth"** para autorizarlo
- Opcional: Asigna una IP fija en la casilla IP

### 5. Obtener tu IP de ZeroTier
- En el script, selecciona opción **3** (Ver estado actual)
- Anota tu **IP de ZeroTier** (ej: `172.25.0.100`)
- Esta es la IP que usarán tus amigos para conectarse

## 👥 Para que tus amigos se conecten

### Pasos para cada amigo:

1. **Instalar ZeroTier One**
   - Descargar desde: https://www.zerotier.com/download
   - Instalar el programa

2. **Unirse a tu red**
   - Abrir ZeroTier One
   - Hacer clic en "Join Network"
   - Introducir tu **Network ID**

3. **Autorización** (tú debes hacer esto)
   - Ve a https://my.zerotier.com/
   - Entra a tu red
   - Busca el nuevo dispositivo en "Members"
   - **Marca "Auth"** para autorizarlo

4. **Conectarse al servidor**
   - Abrir Minecraft
   - Agregar servidor
   - **IP del servidor**: Tu IP de ZeroTier + `:25565`
   - Ejemplo: `172.25.0.100:25565`

## 🔧 Scripts disponibles

- `configurar_zerotier.ps1` - Configurador principal (ejecutar como admin)
- `configurar_zerotier_manual.bat` - Configurador alternativo

## 📊 Verificar estado

Para verificar que todo funciona:
1. Ejecuta el script `configurar_zerotier.ps1`
2. Selecciona opción **3** (Ver estado actual)
3. Verifica que veas:
   - ✅ CONECTADO
   - Una IP asignada
   - Estado "OK"

## 🎮 Información del servidor

- **Puerto del servidor**: 25565 (por defecto)
- **Versión de Minecraft**: 1.21.6
- **Modo**: Survival
- **Dificultad**: Easy

## 🛠️ Solución de problemas

### ❌ "Sin IP asignada"
- Ve a my.zerotier.com
- Verifica que marcaste "Auth" en tu dispositivo

### ❌ "Error conectando a la API"
- Ejecuta el script como administrador
- Verifica que ZeroTier One esté corriendo

### ❌ Amigos no pueden conectarse
- Verifica que autorizaste sus dispositivos
- Confirma que usan la IP correcta con puerto :25565
- Asegúrate que el servidor Minecraft esté corriendo

## 📞 Información de contacto

Tu **Network ID**: `[Completar después de crear la red]`
Tu **IP de ZeroTier**: `[Completar después de autorizar]`

## 🎉 ¡Una vez configurado!

1. Comparte tu **Network ID** con tus amigos
2. Autoriza sus dispositivos en my.zerotier.com
3. Dales tu **IP de ZeroTier:25565**
4. ¡Disfruten jugando!

---

💡 **Tip**: ZeroTier crea una red privada virtual, así que es como si todos estuvieran en la misma red local, pero a través de Internet. Es seguro y fácil de usar.

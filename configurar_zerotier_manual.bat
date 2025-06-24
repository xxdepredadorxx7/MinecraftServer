@echo off
title Configurador de ZeroTier para Servidor Minecraft
color 0A

echo.
echo ========================================
echo    CONFIGURADOR DE ZEROTIER
echo    Para Servidor Minecraft
echo ========================================
echo.

echo Verificando si ZeroTier esta instalado...
zerotier-cli info >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ ZeroTier ya esta instalado
    goto :configurar
) else (
    echo ❌ ZeroTier no esta instalado
    goto :instalar
)

:instalar
echo.
echo 📥 Descargando ZeroTier One...
echo Por favor espera mientras se descarga...

powershell -Command "Invoke-WebRequest -Uri 'https://download.zerotier.com/dist/ZeroTier%%20One.msi' -OutFile 'ZeroTierOne.msi'"

if exist "ZeroTierOne.msi" (
    echo ✅ Descarga completada
    echo.
    echo 🚀 Instalando ZeroTier One...
    echo ⚠️  Se requieren permisos de administrador
    echo    Acepta todas las ventanas que aparezcan
    
    msiexec /i "ZeroTierOne.msi" /quiet /norestart
    
    echo ✅ Instalacion completada
    echo ⏳ Esperando que el servicio se inicie...
    timeout /t 15 /nobreak
    
    del "ZeroTierOne.msi" >nul 2>&1
) else (
    echo ❌ Error descargando ZeroTier
    pause
    exit /b 1
)

:configurar
echo.
echo 🔍 Informacion de ZeroTier:
zerotier-cli info

echo.
echo 📋 Tu ID de ZeroTier:
for /f "tokens=3" %%a in ('zerotier-cli info') do echo    %%a

echo.
echo 📶 Redes conectadas actualmente:
zerotier-cli listnetworks

echo.
echo ========================================
echo    CONFIGURACION DE RED
echo ========================================
echo.
echo Opciones disponibles:
echo   1. Crear una nueva red (recomendado)
echo   2. Unirse a una red existente
echo   3. Ver estado actual
echo   4. Salir
echo.

set /p opcion="Selecciona una opcion (1-4): "

if "%opcion%"=="1" goto :crear_red
if "%opcion%"=="2" goto :unirse_red  
if "%opcion%"=="3" goto :ver_estado
if "%opcion%"=="4" goto :fin
goto :configurar

:crear_red
echo.
echo 🌐 Para crear una nueva red:
echo.
echo 1. Ve a https://my.zerotier.com/
echo 2. Crea una cuenta o inicia sesion
echo 3. Haz clic en "Create A Network"
echo 4. Copia el Network ID que se genera
echo 5. Vuelve aqui y pegalo
echo.
set /p network_id="Introduce el Network ID de tu nueva red: "

if "%network_id%"=="" (
    echo ❌ Network ID no puede estar vacio
    goto :crear_red
)

echo.
echo 🔗 Uniendose a la red %network_id%...
zerotier-cli join %network_id%

if %errorlevel% equ 0 (
    echo ✅ Conectado a la red %network_id%
    echo.
    echo 📋 IMPORTANTE: 
    echo    1. Ve a https://my.zerotier.com/
    echo    2. Haz clic en tu red
    echo    3. Busca tu dispositivo en "Members"
    echo    4. Marca la casilla "Auth" para autorizar tu conexion
    echo    5. Opcional: Asigna una IP fija
    echo.
    echo 📶 Comparte este Network ID con tus amigos: %network_id%
) else (
    echo ❌ Error conectando a la red
)
goto :ver_estado

:unirse_red
echo.
set /p network_id="Introduce el Network ID al que quieres unirte: "

if "%network_id%"=="" (
    echo ❌ Network ID no puede estar vacio
    goto :unirse_red
)

echo.
echo 🔗 Uniendose a la red %network_id%...
zerotier-cli join %network_id%

if %errorlevel% equ 0 (
    echo ✅ Solicitud de conexion enviada
    echo ⚠️  El administrador de la red debe autorizarte
) else (
    echo ❌ Error conectando a la red
)
goto :ver_estado

:ver_estado
echo.
echo 📊 Estado actual de ZeroTier:
echo.
echo Tu ID: 
for /f "tokens=3" %%a in ('zerotier-cli info') do echo    %%a
echo.
echo Redes conectadas:
zerotier-cli listnetworks
echo.
echo IP de ZeroTier asignada:
for /f "tokens=9" %%a in ('zerotier-cli listnetworks ^| findstr "OK"') do echo    %%a
echo.
pause
goto :configurar

:fin
echo.
echo ✅ Configuracion de ZeroTier completada
echo.
echo 📋 RESUMEN PARA CONECTARSE AL SERVIDOR:
echo.
echo 1. Tu IP de ZeroTier:
for /f "tokens=9" %%a in ('zerotier-cli listnetworks ^| findstr "OK"') do echo    %%a:25565
echo.
echo 2. Tus amigos deben:
echo    - Instalar ZeroTier One
echo    - Unirse a tu red con el Network ID
echo    - Ser autorizados por ti en my.zerotier.com
echo    - Conectarse a tu IP de ZeroTier:25565
echo.
echo 🎮 ¡Listo para jugar!
echo.
pause

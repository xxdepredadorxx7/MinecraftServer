# Script para verificar ZeroTier específicamente para la red d3ecf5726d212f34

Write-Host "========================================" -ForegroundColor Green
Write-Host "   VERIFICADOR DE ZEROTIER" -ForegroundColor Green
Write-Host "   Red: d3ecf5726d212f34" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Verificar si ZeroTier está corriendo
$service = Get-Service "ZeroTierOneService" -ErrorAction SilentlyContinue
if (-not $service -or $service.Status -ne 'Running') {
    Write-Host "❌ ZeroTier no está corriendo" -ForegroundColor Red
    exit 1
} else {
    Write-Host "✅ Servicio ZeroTier está corriendo" -ForegroundColor Green
}

# Leer el token de autenticación
$tokenPath = "C:\ProgramData\ZeroTier\One\authtoken.secret"
if (-not (Test-Path $tokenPath)) {
    Write-Host "❌ No se encontró el token de autenticación" -ForegroundColor Red
    Write-Host "   Asegúrate de ejecutar como administrador" -ForegroundColor Yellow
    exit 1
}

try {
    $authToken = Get-Content $tokenPath -Raw | ForEach-Object { $_.Trim() }
    Write-Host "✅ Token de autenticación obtenido" -ForegroundColor Green
} catch {
    Write-Host "❌ Error leyendo el token. Ejecuta como administrador" -ForegroundColor Red
    exit 1
}

# Headers para la API
$headers = @{
    "X-ZT1-Auth" = $authToken
    "Content-Type" = "application/json"
}

# Obtener información general del nodo
Write-Host ""
Write-Host "🔍 Información del nodo ZeroTier:" -ForegroundColor Cyan
try {
    $nodeInfo = Invoke-RestMethod -Uri "http://localhost:9993/status" -Headers $headers -Method GET
    Write-Host "   Tu ID de ZeroTier: $($nodeInfo.address)" -ForegroundColor White
    Write-Host "   Versión: $($nodeInfo.version)" -ForegroundColor White
    Write-Host "   Estado online: $($nodeInfo.online)" -ForegroundColor White
    Write-Host "   TCP fallback: $($nodeInfo.tcpFallbackActive)" -ForegroundColor White
} catch {
    Write-Host "❌ Error obteniendo información del nodo: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Verificar redes conectadas
Write-Host ""
Write-Host "📶 Verificando redes conectadas:" -ForegroundColor Cyan
try {
    $networks = Invoke-RestMethod -Uri "http://localhost:9993/network" -Headers $headers -Method GET
    
    if ($networks.Count -eq 0) {
        Write-Host "❌ No hay redes conectadas" -ForegroundColor Red
        Write-Host "   Necesitas unirte a la red d3ecf5726d212f34" -ForegroundColor Yellow
        
        # Intentar unirse automáticamente
        Write-Host ""
        Write-Host "🔗 Intentando unirse a la red d3ecf5726d212f34..." -ForegroundColor Yellow
        try {
            $joinResult = Invoke-RestMethod -Uri "http://localhost:9993/network/d3ecf5726d212f34" -Headers $headers -Method POST
            Write-Host "✅ Solicitud de unión enviada correctamente" -ForegroundColor Green
            Start-Sleep -Seconds 2
            
            # Verificar de nuevo
            $networks = Invoke-RestMethod -Uri "http://localhost:9993/network" -Headers $headers -Method GET
        } catch {
            Write-Host "❌ Error uniéndose a la red: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    # Mostrar información de todas las redes
    foreach ($network in $networks) {
        Write-Host ""
        if ($network.id -eq "d3ecf5726d212f34") {
            Write-Host "🎯 RED OBJETIVO ENCONTRADA:" -ForegroundColor Green
        } else {
            Write-Host "📡 Otra red:" -ForegroundColor Yellow
        }
        
        Write-Host "   Network ID: $($network.id)" -ForegroundColor White
        Write-Host "   Nombre: $($network.name)" -ForegroundColor White
        Write-Host "   Estado: $($network.status)" -ForegroundColor White
        Write-Host "   Tipo: $($network.type)" -ForegroundColor White
        
        if ($network.assignedAddresses -and $network.assignedAddresses.Count -gt 0) {
            Write-Host "   ✅ IP asignada: $($network.assignedAddresses -join ', ')" -ForegroundColor Green
            
            if ($network.id -eq "d3ecf5726d212f34") {
                $serverIP = $network.assignedAddresses[0]
                Write-Host ""
                Write-Host "🎮 IP DEL SERVIDOR MINECRAFT:" -ForegroundColor Green
                Write-Host "   $serverIP`:25565" -ForegroundColor White -BackgroundColor DarkGreen
                Write-Host ""
                Write-Host "📤 Comparte esta IP con tus amigos para que se conecten" -ForegroundColor Yellow
            }
        } else {
            Write-Host "   ⚠️ Sin IP asignada" -ForegroundColor Red
            if ($network.id -eq "d3ecf5726d212f34") {
                Write-Host "   📋 Acción requerida: Ve a https://my.zerotier.com/ y autoriza este dispositivo" -ForegroundColor Yellow
            }
        }
        
        Write-Host "   MAC: $($network.mac)" -ForegroundColor Gray
        Write-Host "   MTU: $($network.mtu)" -ForegroundColor Gray
        Write-Host "   Bridge: $($network.bridge)" -ForegroundColor Gray
        Write-Host "   Broadcast: $($network.broadcastEnabled)" -ForegroundColor Gray
    }
    
} catch {
    Write-Host "❌ Error obteniendo redes: $($_.Exception.Message)" -ForegroundColor Red
}

# Verificar conectividad específica de la red objetivo
$targetNetwork = $networks | Where-Object { $_.id -eq "d3ecf5726d212f34" }
if ($targetNetwork) {
    Write-Host ""
    Write-Host "🧪 Pruebas de conectividad para red d3ecf5726d212f34:" -ForegroundColor Cyan
    
    if ($targetNetwork.status -eq "OK") {
        Write-Host "   ✅ Estado de la red: CONECTADO" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️ Estado de la red: $($targetNetwork.status)" -ForegroundColor Yellow
    }
    
    if ($targetNetwork.assignedAddresses -and $targetNetwork.assignedAddresses.Count -gt 0) {
        $myIP = $targetNetwork.assignedAddresses[0]
        Write-Host "   ✅ IP asignada correctamente: $myIP" -ForegroundColor Green
        
        # Test de ping a la IP asignada (ping a uno mismo)
        Write-Host "   🏓 Probando conectividad local..." -ForegroundColor Yellow
        try {
            $pingResult = Test-Connection -ComputerName $myIP -Count 1 -Quiet
            if ($pingResult) {
                Write-Host "   ✅ Ping local exitoso" -ForegroundColor Green
            } else {
                Write-Host "   ⚠️ Ping local falló" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "   ⚠️ No se pudo hacer ping: $($_.Exception.Message)" -ForegroundColor Yellow
        }
        
        # Test del puerto 25565
        Write-Host "   🔌 Verificando puerto 25565..." -ForegroundColor Yellow
        try {
            $portTest = Test-NetConnection -ComputerName $myIP -Port 25565 -WarningAction SilentlyContinue
            if ($portTest.TcpTestSucceeded) {
                Write-Host "   ✅ Puerto 25565 accesible desde ZeroTier" -ForegroundColor Green
            } else {
                Write-Host "   ⚠️ Puerto 25565 no responde (servidor Minecraft no está corriendo)" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "   ⚠️ No se pudo probar el puerto: $($_.Exception.Message)" -ForegroundColor Yellow
        }
        
    } else {
        Write-Host "   ❌ Sin IP asignada" -ForegroundColor Red
        Write-Host ""
        Write-Host "🔧 ACCIÓN REQUERIDA:" -ForegroundColor Red
        Write-Host "   1. Ve a https://my.zerotier.com/" -ForegroundColor White
        Write-Host "   2. Haz clic en la red d3ecf5726d212f34" -ForegroundColor White
        Write-Host "   3. Busca tu dispositivo (ID: $($nodeInfo.address))" -ForegroundColor White
        Write-Host "   4. Marca la casilla 'Auth' para autorizarlo" -ForegroundColor White
    }
} else {
    Write-Host ""
    Write-Host "❌ No estás conectado a la red d3ecf5726d212f34" -ForegroundColor Red
    Write-Host "   Ejecuta el configurador de ZeroTier para unirte" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   RESUMEN" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Resumen final
if ($targetNetwork -and $targetNetwork.status -eq "OK" -and $targetNetwork.assignedAddresses.Count -gt 0) {
    $serverIP = $targetNetwork.assignedAddresses[0]
    Write-Host ""
    Write-Host "🎉 ¡TODO FUNCIONA CORRECTAMENTE!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Información para compartir:" -ForegroundColor Cyan
    Write-Host "   Network ID: d3ecf5726d212f34" -ForegroundColor White
    Write-Host "   IP del servidor: $serverIP`:25565" -ForegroundColor White
    Write-Host ""
    Write-Host "📤 Tus amigos deben:" -ForegroundColor Yellow
    Write-Host "   1. Instalar ZeroTier One" -ForegroundColor White
    Write-Host "   2. Unirse a la red: d3ecf5726d212f34" -ForegroundColor White
    Write-Host "   3. Ser autorizados por ti" -ForegroundColor White
    Write-Host "   4. Conectarse a: $serverIP`:25565" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "⚠️ Configuración incompleta" -ForegroundColor Yellow
    Write-Host "   Revisa los pasos anteriores para completar la configuración" -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Presiona Enter para salir"

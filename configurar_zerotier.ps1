# Configurador de ZeroTier para Servidor Minecraft
# Script PowerShell que usa la API local de ZeroTier

Write-Host "========================================" -ForegroundColor Green
Write-Host "   CONFIGURADOR DE ZEROTIER" -ForegroundColor Green  
Write-Host "   Para Servidor Minecraft" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Verificar si ZeroTier está instalado y corriendo
$service = Get-Service "ZeroTierOneService" -ErrorAction SilentlyContinue
if (-not $service -or $service.Status -ne 'Running') {
    Write-Host "❌ ZeroTier no está instalado o no está corriendo" -ForegroundColor Red
    Write-Host "Por favor ejecuta el script configurar_zerotier_manual.bat primero" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ ZeroTier está corriendo correctamente" -ForegroundColor Green

# Leer el token de autenticación
$tokenPath = "C:\ProgramData\ZeroTier\One\authtoken.secret"
if (-not (Test-Path $tokenPath)) {
    Write-Host "❌ No se encontró el token de autenticación" -ForegroundColor Red
    Write-Host "Intenta ejecutar como administrador" -ForegroundColor Yellow
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

# Obtener información del nodo
try {
    $nodeInfo = Invoke-RestMethod -Uri "http://localhost:9993/status" -Headers $headers -Method GET
    Write-Host ""
    Write-Host "🔍 Información de ZeroTier:" -ForegroundColor Cyan
    Write-Host "   Tu ID de ZeroTier: $($nodeInfo.address)" -ForegroundColor White
    Write-Host "   Versión: $($nodeInfo.version)" -ForegroundColor White
    Write-Host "   Estado: $($nodeInfo.online)" -ForegroundColor White
} catch {
    Write-Host "❌ Error conectando a la API de ZeroTier" -ForegroundColor Red
    Write-Host "Detalles: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Obtener redes actuales
try {
    $networks = Invoke-RestMethod -Uri "http://localhost:9993/network" -Headers $headers -Method GET
    Write-Host ""
    Write-Host "📶 Redes conectadas actualmente:" -ForegroundColor Cyan
    if ($networks.Count -eq 0) {
        Write-Host "   Ninguna red conectada" -ForegroundColor Yellow
    } else {
        foreach ($network in $networks) {
            $status = if ($network.status -eq "OK") { "✅" } else { "⚠️" }
            Write-Host "   $status Red: $($network.id)" -ForegroundColor White
            if ($network.assignedAddresses) {
                Write-Host "      IP asignada: $($network.assignedAddresses -join ', ')" -ForegroundColor Gray
            }
        }
    }
} catch {
    Write-Host "❌ Error obteniendo redes" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   CONFIGURACIÓN DE RED" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Opciones disponibles:" -ForegroundColor Cyan
Write-Host "  1. Crear una nueva red (recomendado)" -ForegroundColor White
Write-Host "  2. Unirse a una red existente" -ForegroundColor White
Write-Host "  3. Ver estado actual" -ForegroundColor White
Write-Host "  4. Desconectarse de una red" -ForegroundColor White
Write-Host "  5. Salir" -ForegroundColor White
Write-Host ""

do {
    $opcion = Read-Host "Selecciona una opción (1-5)"
    
    switch ($opcion) {
        "1" {
            Write-Host ""
            Write-Host "🌐 Para crear una nueva red:" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "1. Ve a https://my.zerotier.com/" -ForegroundColor Yellow
            Write-Host "2. Crea una cuenta o inicia sesión" -ForegroundColor Yellow
            Write-Host "3. Haz clic en 'Create A Network'" -ForegroundColor Yellow
            Write-Host "4. Copia el Network ID que se genera (16 caracteres)" -ForegroundColor Yellow
            Write-Host "5. Vuelve aqui y pegalo" -ForegroundColor Yellow
            Write-Host ""
            
            do {
                $networkId = Read-Host "Introduce el Network ID de tu nueva red"
                if ($networkId.Length -ne 16) {
                    Write-Host "❌ Network ID debe tener exactamente 16 caracteres" -ForegroundColor Red
                }
            } while ($networkId.Length -ne 16)
            
            # Unirse a la red
            try {
                Write-Host ""
                Write-Host "🔗 Uniéndose a la red $networkId..." -ForegroundColor Yellow
                
                $joinResult = Invoke-RestMethod -Uri "http://localhost:9993/network/$networkId" -Headers $headers -Method POST
                
                Write-Host "✅ Solicitud enviada correctamente" -ForegroundColor Green
                Write-Host ""
                Write-Host "📋 IMPORTANTE:" -ForegroundColor Red
                Write-Host "   1. Ve a https://my.zerotier.com/" -ForegroundColor Yellow
                Write-Host "   2. Haz clic en tu red" -ForegroundColor Yellow
                Write-Host "   3. Busca tu dispositivo en 'Members'" -ForegroundColor Yellow
                Write-Host "   4. Marca la casilla 'Auth' para autorizar tu conexión" -ForegroundColor Yellow
                Write-Host "   5. Opcional: Asigna una IP fija" -ForegroundColor Yellow
                Write-Host ""
                Write-Host "📶 Comparte este Network ID con tus amigos: $networkId" -ForegroundColor Green
                Write-Host ""
                
            } catch {
                Write-Host "❌ Error uniéndose a la red: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
        
        "2" {
            do {
                $networkId = Read-Host "`nIntroduce el Network ID al que quieres unirte"
                if ($networkId.Length -ne 16) {
                    Write-Host "❌ Network ID debe tener exactamente 16 caracteres" -ForegroundColor Red
                }
            } while ($networkId.Length -ne 16)
            
            try {
                Write-Host ""
                Write-Host "🔗 Uniéndose a la red $networkId..." -ForegroundColor Yellow
                
                $joinResult = Invoke-RestMethod -Uri "http://localhost:9993/network/$networkId" -Headers $headers -Method POST
                
                Write-Host "✅ Solicitud de conexión enviada" -ForegroundColor Green
                Write-Host "⚠️ El administrador de la red debe autorizarte" -ForegroundColor Yellow
                Write-Host ""
                
            } catch {
                Write-Host "❌ Error conectando a la red: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
        
        "3" {
            # Actualizar estado
            try {
                $networks = Invoke-RestMethod -Uri "http://localhost:9993/network" -Headers $headers -Method GET
                Write-Host ""
                Write-Host "📊 Estado actual de ZeroTier:" -ForegroundColor Cyan
                Write-Host ""
                Write-Host "Tu ID de ZeroTier: $($nodeInfo.address)" -ForegroundColor White
                Write-Host ""
                
                if ($networks.Count -eq 0) {
                    Write-Host "❌ No hay redes conectadas" -ForegroundColor Red
                } else {
                    Write-Host "Redes conectadas:" -ForegroundColor Green
                    foreach ($network in $networks) {
                        $status = if ($network.status -eq "OK") { "✅ CONECTADO" } else { "⚠️ PENDIENTE" }
                        Write-Host "   Red: $($network.id) - $status" -ForegroundColor White
                        if ($network.assignedAddresses -and $network.assignedAddresses.Count -gt 0) {
                            Write-Host "   IP de ZeroTier: $($network.assignedAddresses[0]):25565" -ForegroundColor Green
                            Write-Host "   (Esta es la IP que deben usar tus amigos para conectarse)" -ForegroundColor Yellow
                        } else {
                            Write-Host "   ⚠️ Sin IP asignada - revisa la autorización en my.zerotier.com" -ForegroundColor Yellow
                        }
                        Write-Host ""
                    }
                }
            } catch {
                Write-Host "❌ Error obteniendo estado: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
        
        "4" {
            try {
                $networks = Invoke-RestMethod -Uri "http://localhost:9993/network" -Headers $headers -Method GET
                if ($networks.Count -eq 0) {
                    Write-Host "`n❌ No hay redes conectadas" -ForegroundColor Red
                } else {
                    Write-Host "`nRedes disponibles para desconectar:" -ForegroundColor Cyan
                    for ($i = 0; $i -lt $networks.Count; $i++) {
                        Write-Host "   $($i + 1). $($networks[$i].id)" -ForegroundColor White
                    }
                    
                    $selection = Read-Host "`nSelecciona el número de red a desconectar (1-$($networks.Count))"
                    $index = [int]$selection - 1
                    
                    if ($index -ge 0 -and $index -lt $networks.Count) {
                        $networkToLeave = $networks[$index].id
                        
                        try {
                            Invoke-RestMethod -Uri "http://localhost:9993/network/$networkToLeave" -Headers $headers -Method DELETE
                            Write-Host "✅ Desconectado de la red $networkToLeave" -ForegroundColor Green
                        } catch {
                            Write-Host "❌ Error desconectando de la red: $($_.Exception.Message)" -ForegroundColor Red
                        }
                    } else {
                        Write-Host "❌ Selección inválida" -ForegroundColor Red
                    }
                }
            } catch {
                Write-Host "❌ Error obteniendo redes: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
        
        "5" {
            Write-Host ""
            Write-Host "✅ Configuración de ZeroTier completada" -ForegroundColor Green
            Write-Host ""
            Write-Host "📋 RESUMEN PARA CONECTARSE AL SERVIDOR:" -ForegroundColor Cyan
            Write-Host ""
            
            try {
                $networks = Invoke-RestMethod -Uri "http://localhost:9993/network" -Headers $headers -Method GET
                $connectedNetworks = $networks | Where-Object { $_.status -eq "OK" -and $_.assignedAddresses.Count -gt 0 }
                
                if ($connectedNetworks.Count -gt 0) {
                    Write-Host "🎮 Tu servidor está disponible en:" -ForegroundColor Green
                    foreach ($network in $connectedNetworks) {
                        Write-Host "   IP: $($network.assignedAddresses[0]):25565" -ForegroundColor White
                        Write-Host "   Red: $($network.id)" -ForegroundColor Gray
                    }
                    Write-Host ""
                    Write-Host "📤 Tus amigos deben:" -ForegroundColor Yellow
                    Write-Host "   1. Instalar ZeroTier One desde https://www.zerotier.com/download" -ForegroundColor White
                    Write-Host "   2. Unirse a tu red con el Network ID" -ForegroundColor White
                    Write-Host "   3. Ser autorizados por ti en my.zerotier.com" -ForegroundColor White
                    Write-Host "   4. Conectarse a tu IP de ZeroTier:25565 en Minecraft" -ForegroundColor White
                } else {
                    Write-Host "⚠️ No hay redes conectadas con IP asignada" -ForegroundColor Yellow
                    Write-Host "   Asegúrate de autorizar tu dispositivo en my.zerotier.com" -ForegroundColor Yellow
                }
            } catch {
                Write-Host "❌ Error obteniendo información final" -ForegroundColor Red
            }
            
            Write-Host ""
            Write-Host "🎉 ¡Listo para jugar!" -ForegroundColor Green
            break
        }
        
        default {
            Write-Host "❌ Opción inválida. Selecciona 1-5" -ForegroundColor Red
        }
    }
    
    if ($opcion -ne "5") {
        Write-Host ""
        Read-Host "Presiona Enter para continuar"
        Write-Host ""
        Write-Host "Opciones disponibles:" -ForegroundColor Cyan
        Write-Host "  1. Crear una nueva red (recomendado)" -ForegroundColor White
        Write-Host "  2. Unirse a una red existente" -ForegroundColor White
        Write-Host "  3. Ver estado actual" -ForegroundColor White
        Write-Host "  4. Desconectarse de una red" -ForegroundColor White
        Write-Host "  5. Salir" -ForegroundColor White
        Write-Host ""
    }
    
} while ($opcion -ne "5")

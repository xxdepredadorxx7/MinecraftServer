# Script para instalar Java OpenJDK automáticamente
# Versión recomendada para servidores: OpenJDK 21 LTS

Write-Host "=== Instalador Automático de Java para Servidor ===" -ForegroundColor Green
Write-Host "Instalando OpenJDK 21 LTS (Long Term Support)..." -ForegroundColor Yellow

# Verificar si Chocolatey está instalado
function Test-ChocolateyInstalled {
    try {
        choco --version | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Instalar Chocolatey si no está presente
function Install-Chocolatey {
    Write-Host "Chocolatey no está instalado. Instalando Chocolatey..." -ForegroundColor Yellow
    
    # Verificar política de ejecución
    $executionPolicy = Get-ExecutionPolicy
    if ($executionPolicy -eq 'Restricted') {
        Write-Host "Cambiando política de ejecución temporalmente..." -ForegroundColor Yellow
        Set-ExecutionPolicy Bypass -Scope Process -Force
    }
    
    # Instalar Chocolatey
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    
    # Refrescar variables de entorno
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
    
    Write-Host "Chocolatey instalado correctamente." -ForegroundColor Green
}

# Función principal de instalación
function Install-JavaForServer {
    # Verificar si se está ejecutando como administrador
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    
    if (-not $isAdmin) {
        Write-Host "ADVERTENCIA: Se recomienda ejecutar como administrador para una instalación completa." -ForegroundColor Red
        $response = Read-Host "¿Deseas continuar de todos modos? (s/n)"
        if ($response -ne 's' -and $response -ne 'S') {
            Write-Host "Instalación cancelada. Ejecuta el script como administrador." -ForegroundColor Red
            return
        }
    }
    
    # Verificar/Instalar Chocolatey
    if (-not (Test-ChocolateyInstalled)) {
        Install-Chocolatey
    }
    else {
        Write-Host "Chocolatey ya está instalado." -ForegroundColor Green
    }
    
    # Verificar si Java ya está instalado
    try {
        $javaVersion = java -version 2>&1 | Select-String "version"
        if ($javaVersion) {
            Write-Host "Java ya está instalado:" -ForegroundColor Yellow
            Write-Host $javaVersion -ForegroundColor Cyan
            $response = Read-Host "¿Deseas reinstalar/actualizar? (s/n)"
            if ($response -ne 's' -and $response -ne 'S') {
                Write-Host "Instalación cancelada." -ForegroundColor Yellow
                return
            }
        }
    }
    catch {
        Write-Host "Java no está instalado actualmente." -ForegroundColor Yellow
    }
    
    # Instalar OpenJDK 21
    Write-Host "Instalando OpenJDK 21 LTS..." -ForegroundColor Yellow
    try {
        choco install temurin -y
        
        # Refrescar variables de entorno
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
        
        Write-Host "¡OpenJDK 21 instalado correctamente!" -ForegroundColor Green
        
        # Verificar instalación
        Write-Host "`nVerificando instalación..." -ForegroundColor Yellow
        java -version
        javac -version
        
        # Mostrar variables de entorno importantes
        Write-Host "`nVariables de entorno importantes:" -ForegroundColor Cyan
        Write-Host "JAVA_HOME: $env:JAVA_HOME" -ForegroundColor White
        
        # Configurar JAVA_HOME si no está configurado
        $javaHome = [System.Environment]::GetEnvironmentVariable("JAVA_HOME", "Machine")
        if (-not $javaHome) {
            Write-Host "Configurando JAVA_HOME..." -ForegroundColor Yellow
            
            # Buscar instalación de Java
            $javaPath = Get-ChildItem "C:\Program Files\Eclipse Adoptium\" -Directory | Where-Object { $_.Name -like "*jdk*21*" } | Select-Object -First 1
            if ($javaPath) {
                $javaHomePath = $javaPath.FullName
                [System.Environment]::SetEnvironmentVariable("JAVA_HOME", $javaHomePath, "Machine")
                Write-Host "JAVA_HOME configurado en: $javaHomePath" -ForegroundColor Green
            }
        }
        
        Write-Host "`n=== Instalación completada exitosamente ===" -ForegroundColor Green
        Write-Host "Características de esta instalación:" -ForegroundColor Cyan
        Write-Host "- OpenJDK 21 LTS (Long Term Support)" -ForegroundColor White
        Write-Host "- Optimizado para uso en servidores" -ForegroundColor White
        Write-Host "- Incluye JRE y JDK completos" -ForegroundColor White
        Write-Host "- Variables de entorno configuradas automáticamente" -ForegroundColor White
        
        Write-Host "`nReinicia tu terminal o PowerShell para asegurar que todas las variables de entorno estén disponibles." -ForegroundColor Yellow
        
    }
    catch {
        Write-Host "Error durante la instalación: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Intenta ejecutar el script como administrador." -ForegroundColor Yellow
    }
}

# Ejecutar instalación
Install-JavaForServer

Write-Host "`nPresiona cualquier tecla para salir..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

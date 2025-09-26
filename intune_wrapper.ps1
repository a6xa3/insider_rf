# PowerShell wrapper для развертывания через Intune
# Этот скрипт извлекает встроенные ресурсы и запускает установку

param(
    [string]$Mode = "GLOBAL",
    [string]$CreateEmployee = "NO",
    [string]$ManualCollect = "AUTOMATE"
)

# Функция для извлечения встроенного JSON
function Extract-EmbeddedJson {
    param([string]$OutputPath)
    
    # JSON конфигурация встроена в скрипт
    $jsonContent = @'
{
  "mode": "global",
  "settings": {
    "path": "$UserDataDirectory/configuration.json"
  },
  "server": {
    "path": "agents/",
    "address": "geopl.insider.cloud",
    "port": null,
    "secure": true,
    "key": "pIAFy0RnHMrYgDiwX2DRkwnsYMEH4TKC"
  },
  "debug": {
    "type": "console",
    "enabled": false,
    "file": "$UserDataDirectory/agent.log"
  },
  "client": {
    "type": "http"
  }
}
'@
    
    $jsonContent | Out-File -FilePath $OutputPath -Encoding UTF8
    Write-Host "JSON конфигурация извлечена в: $OutputPath"
}

# Основная логика
try {
    $tempDir = [System.IO.Path]::GetTempPath()
    $configPath = Join-Path $tempDir "configuration.json"
    
    # Извлекаем JSON конфигурацию
    Extract-EmbeddedJson -OutputPath $configPath
    
    # Запускаем MSI установку с параметрами
    $msiPath = Join-Path $PSScriptRoot "install.msi"
    $arguments = @(
        "/i", "`"$msiPath`"",
        "/quiet",
        "MODE=$Mode",
        "CREATE_EMPLOYEE=$CreateEmployee", 
        "MANUAL_COLLECT=$ManualCollect"
    )
    
    Write-Host "Запуск установки: msiexec $($arguments -join ' ')"
    $process = Start-Process -FilePath "msiexec.exe" -ArgumentList $arguments -Wait -PassThru
    
    if ($process.ExitCode -eq 0) {
        Write-Host "Установка завершена успешно"
    } else {
        Write-Error "Ошибка установки. Код выхода: $($process.ExitCode)"
        exit $process.ExitCode
    }
    
    # Очищаем временный файл
    if (Test-Path $configPath) {
        Remove-Item $configPath -Force
    }
    
} catch {
    Write-Error "Ошибка выполнения: $($_.Exception.Message)"
    exit 1
}
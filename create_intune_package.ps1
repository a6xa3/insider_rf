# Скрипт для создания пакета для Intune
# Создает .intunewin файл с помощью Microsoft Win32 Content Prep Tool

param(
    [string]$SourceFolder = ".",
    [string]$SetupFile = "intune_wrapper.ps1",
    [string]$OutputFolder = "IntunePackage"
)

# Проверяем наличие Win32 Content Prep Tool
$prepToolPath = "IntuneWinAppUtil.exe"
if (-not (Test-Path $prepToolPath)) {
    Write-Host "Скачиваем Microsoft Win32 Content Prep Tool..."
    $downloadUrl = "https://github.com/Microsoft/Microsoft-Win32-Content-Prep-Tool/raw/master/IntuneWinAppUtil.exe"
    Invoke-WebRequest -Uri $downloadUrl -OutFile $prepToolPath
}

# Создаем выходную папку
if (-not (Test-Path $OutputFolder)) {
    New-Item -ItemType Directory -Path $OutputFolder -Force
}

# Создаем .intunewin пакет
Write-Host "Создание .intunewin пакета..."
& $prepToolPath -c $SourceFolder -s $SetupFile -o $OutputFolder

Write-Host "Пакет создан в папке: $OutputFolder"
Write-Host ""
Write-Host "Параметры для настройки в Intune:"
Write-Host "Install command: powershell.exe -ExecutionPolicy Bypass -File intune_wrapper.ps1"
Write-Host "Uninstall command: msiexec /x {B1DCDB78-5559-4366-8AC6-36F486741444} /quiet"
Write-Host "Detection rule: Registry - HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{B1DCDB78-5559-4366-8AC6-36F486741444}"
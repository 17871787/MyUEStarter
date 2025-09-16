# Open-Farm.ps1
# Open the Dairy Farm level in Unreal Editor

param(
    [string]$UEVersion = "5.6",
    [string]$ProjectPath = "C:\Users\jtowe\OneDrive\Documents\Unreal Projects\MyUEStarter\MyUEStarter.uproject"
)

# Set UE paths
$UERoot = "C:\Program Files\Epic Games\UE_$UEVersion"
$UEBin = "$UERoot\Engine\Binaries\Win64"

if (-not (Test-Path $UEBin)) {
    Write-Error "Unreal Engine $UEVersion not found at $UERoot"
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Opening Dairy Farm in Unreal Editor" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

# Open the editor with the farm level
& "$UEBin\UnrealEditor.exe" "$ProjectPath" "/Game/Farm/Maps/DairyFarm_L1"

Write-Host "`nEditor launched with DairyFarm_L1 level" -ForegroundColor Green
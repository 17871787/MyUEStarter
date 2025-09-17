# Open-Farm.ps1
# Open the Dairy Farm level in Unreal Editor

param(
    [string]$Map = "L2",  # Default to L2
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

# Determine level path
if ($Map -eq "L2") {
    $levelPath = "/Game/Farm/Maps/DairyFarm_L2"
} else {
    $levelPath = "/Game/Farm/Maps/DairyFarm_L1"
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Opening Dairy Farm $Map in Unreal Editor" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Level: $levelPath" -ForegroundColor Yellow

# Open the editor with the farm level
& "$UEBin\UnrealEditor.exe" "$ProjectPath" "$levelPath"

Write-Host "`nEditor launched with DairyFarm_$Map level" -ForegroundColor Green

if ($Map -eq "L2") {
    Write-Host "`nL2 Controls:" -ForegroundColor Cyan
    Write-Host "  T - Toggle day/night" -ForegroundColor White
    Write-Host "  R - Regenerate animals" -ForegroundColor White
    Write-Host "  [ - Previous hour" -ForegroundColor White
    Write-Host "  ] - Next hour" -ForegroundColor White
    Write-Host "  P - Toggle pause" -ForegroundColor White
    Write-Host "  1-6 - Focus camera to paddock" -ForegroundColor White
}
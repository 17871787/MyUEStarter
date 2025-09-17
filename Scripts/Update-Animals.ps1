# Update-Animals.ps1
# Regenerate animals sublevel based on new density or rotation

param(
    [string]$UEVersion = "5.6",
    [string]$ProjectPath = "C:\Users\jtowe\OneDrive\Documents\Unreal Projects\MyUEStarter\MyUEStarter.uproject",
    [float]$Density,  # Optional: New stocking density
    [switch]$Rotate   # Optional: Force rotation to next paddock
)

# Set UE paths
$UERoot = "C:\Program Files\Epic Games\UE_$UEVersion"
$UEBin = "$UERoot\Engine\Binaries\Win64"

if (-not (Test-Path $UEBin)) {
    Write-Error "Unreal Engine $UEVersion not found at $UERoot"
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Updating Farm Animals" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

if ($Density) {
    Write-Host "New stocking density: $Density cows/ha" -ForegroundColor Yellow
}

if ($Rotate) {
    Write-Host "Forcing rotation to next paddock" -ForegroundColor Yellow
}

# Run animal regeneration
Write-Host "`nRegenerating animals..." -ForegroundColor Cyan
& "$UEBin\UnrealEditor-Cmd.exe" "$ProjectPath" -ExecutePythonScript="Scripts/ue/animals_regen.py" -nosplash -unattended

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Animal Update Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Read current state
$configPath = "Content\Farm\Data\farm_config_v2.json"
$statePath = "Content\Farm\Data\GrazingState.json"

if (Test-Path $configPath) {
    $config = Get-Content $configPath | ConvertFrom-Json
    Write-Host "`nCurrent Settings:" -ForegroundColor Cyan
    Write-Host "  Stocking density: $($config.stocking_density_cows_per_ha) cows/ha" -ForegroundColor White
    Write-Host "  Paddocks: $($config.paddocks)" -ForegroundColor White
}

if (Test-Path $statePath) {
    $state = Get-Content $statePath | ConvertFrom-Json
    Write-Host "  Active paddock: $($state.active_paddock_index)" -ForegroundColor White
    Write-Host "  Last rotated: $($state.last_rotated_iso)" -ForegroundColor White
}
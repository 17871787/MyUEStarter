# Gen-Farm.ps1
# Generate the Dairy Farm scene (L1 or L2) from command line

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

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Dairy Farm Scene Generator ($Map)" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Project: $ProjectPath" -ForegroundColor Yellow
Write-Host "Engine: UE $UEVersion" -ForegroundColor Yellow
Write-Host "Target: Level $Map" -ForegroundColor Yellow

# Step 1: Build materials (includes new L2 materials)
Write-Host "`n[1/4] Building farm materials..." -ForegroundColor Cyan
& "$UEBin\UnrealEditor-Cmd.exe" "$ProjectPath" -ExecutePythonScript="Scripts/ue/materials_build.py" -nosplash -unattended

if ($LASTEXITCODE -ne 0) {
    Write-Warning "Material build may have issues, continuing..."
}

# Step 2: Generate appropriate level
if ($Map -eq "L2") {
    Write-Host "`n[2/4] Generating L2 farm scene with sublevels..." -ForegroundColor Cyan
    & "$UEBin\UnrealEditor-Cmd.exe" "$ProjectPath" -ExecutePythonScript="Scripts/ue/farm_generate_l2.py" -nosplash -unattended

    Write-Host "`n[3/4] Building UI system..." -ForegroundColor Cyan
    & "$UEBin\UnrealEditor-Cmd.exe" "$ProjectPath" -ExecutePythonScript="Scripts/ue/ui_build.py" -nosplash -unattended

    Write-Host "`n[4/4] Setting up time of day..." -ForegroundColor Cyan
    & "$UEBin\UnrealEditor-Cmd.exe" "$ProjectPath" -ExecutePythonScript="Scripts/ue/tod_utils.py" -nosplash -unattended

    $levelPath = "/Game/Farm/Maps/DairyFarm_L2"
} else {
    Write-Host "`n[2/4] Generating L1 farm scene..." -ForegroundColor Cyan
    & "$UEBin\UnrealEditor-Cmd.exe" "$ProjectPath" -ExecutePythonScript="Scripts/ue/farm_generate.py" -nosplash -unattended

    Write-Host "`n[3/4] Adding simulation behaviors..." -ForegroundColor Cyan
    & "$UEBin\UnrealEditor-Cmd.exe" "$ProjectPath" -ExecutePythonScript="Scripts/ue/farm_simulate.py" -nosplash -unattended

    $levelPath = "/Game/Farm/Maps/DairyFarm_L1"
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Farm Generation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nLevel created: $levelPath" -ForegroundColor Yellow

if ($Map -eq "L2") {
    Write-Host "`nL2 Features:" -ForegroundColor Cyan
    Write-Host "  - Sublevels: Paddocks, Yard, Animals" -ForegroundColor White
    Write-Host "  - Density-based cow count" -ForegroundColor White
    Write-Host "  - Rotational grazing system" -ForegroundColor White
    Write-Host "  - UI/HUD controls" -ForegroundColor White
    Write-Host "  - NavMesh support" -ForegroundColor White
}

Write-Host "`nTo view the farm, run:" -ForegroundColor Cyan
Write-Host "  .\Open-Farm.ps1 -Map $Map" -ForegroundColor White
Write-Host "`nTo render screenshots:" -ForegroundColor Cyan
Write-Host "  .\Render-Farm.ps1" -ForegroundColor White
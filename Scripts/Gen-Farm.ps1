# Gen-Farm.ps1
# Generate the Dairy Farm scene from command line

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
Write-Host "Dairy Farm Scene Generator" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Project: $ProjectPath" -ForegroundColor Yellow
Write-Host "Engine: UE $UEVersion" -ForegroundColor Yellow

# Step 1: Build materials
Write-Host "`n[1/3] Building farm materials..." -ForegroundColor Cyan
& "$UEBin\UnrealEditor-Cmd.exe" "$ProjectPath" -ExecutePythonScript="Scripts/ue/materials_build.py" -nosplash -unattended

if ($LASTEXITCODE -ne 0) {
    Write-Warning "Material build may have issues, continuing..."
}

# Step 2: Generate farm scene
Write-Host "`n[2/3] Generating farm scene..." -ForegroundColor Cyan
& "$UEBin\UnrealEditor-Cmd.exe" "$ProjectPath" -ExecutePythonScript="Scripts/ue/farm_generate.py" -nosplash -unattended

if ($LASTEXITCODE -ne 0) {
    Write-Warning "Farm generation may have issues, continuing..."
}

# Step 3: Add simulation behaviors
Write-Host "`n[3/3] Adding simulation behaviors..." -ForegroundColor Cyan
& "$UEBin\UnrealEditor-Cmd.exe" "$ProjectPath" -ExecutePythonScript="Scripts/ue/farm_simulate.py" -nosplash -unattended

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Farm Generation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nLevel created: /Game/Farm/Maps/DairyFarm_L1" -ForegroundColor Yellow
Write-Host "`nTo view the farm, run:" -ForegroundColor Cyan
Write-Host "  .\Open-Farm.ps1" -ForegroundColor White
Write-Host "`nOr open manually:" -ForegroundColor Cyan
Write-Host "  & `"$UEBin\UnrealEditor.exe`" `"$ProjectPath`" /Game/Farm/Maps/DairyFarm_L1" -ForegroundColor White
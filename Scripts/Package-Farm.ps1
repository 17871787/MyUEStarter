# Package-Farm.ps1
# Package the Dairy Farm for distribution

param(
    [string]$UEVersion = "5.6",
    [string]$ProjectPath = "C:\Users\jtowe\OneDrive\Documents\Unreal Projects\MyUEStarter\MyUEStarter.uproject",
    [string]$Map = "L2",
    [string]$Platform = "Win64",
    [string]$Configuration = "Development"
)

# Set UE paths
$UERoot = "C:\Program Files\Epic Games\UE_$UEVersion"
$UEBin = "$UERoot\Engine\Binaries\Win64"
$UEBuild = "$UERoot\Engine\Build\BatchFiles"

if (-not (Test-Path $UEBuild)) {
    Write-Error "Unreal Engine $UEVersion not found at $UERoot"
    exit 1
}

# Determine level path
if ($Map -eq "L2") {
    $levelPath = "/Game/Farm/Maps/DairyFarm_L2"
} else {
    $levelPath = "/Game/Farm/Maps/DairyFarm_L1"
}

# Set output directory
$outputDir = "$env:USERPROFILE\UnrealBuilds\MyUEStarter-$Map"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Packaging Dairy Farm $Map" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Platform: $Platform" -ForegroundColor Yellow
Write-Host "Configuration: $Configuration" -ForegroundColor Yellow
Write-Host "Map: $levelPath" -ForegroundColor Yellow
Write-Host "Output: $outputDir" -ForegroundColor Yellow

Write-Host "`nStarting packaging process..." -ForegroundColor Cyan
Write-Host "This may take 5-10 minutes..." -ForegroundColor Yellow

# Run packaging
& "$UEBuild\RunUAT.bat" BuildCookRun `
    -project="$ProjectPath" `
    -platform=$Platform `
    -clientconfig=$Configuration `
    -cook -build -stage -pak -archive `
    -archivedirectory="$outputDir" `
    -map="$levelPath"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "Packaging Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "`nPackaged build location:" -ForegroundColor Cyan
    Write-Host "  $outputDir" -ForegroundColor White

    # Check package size
    if (Test-Path $outputDir) {
        $size = (Get-ChildItem $outputDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1GB
        Write-Host "`nPackage size: $([math]::Round($size, 2)) GB" -ForegroundColor Yellow
    }

    Write-Host "`nTo run the packaged game:" -ForegroundColor Cyan
    Write-Host "  $outputDir\Windows\MyUEStarter.exe" -ForegroundColor White
} else {
    Write-Error "Packaging failed with exit code: $LASTEXITCODE"
    exit $LASTEXITCODE
}
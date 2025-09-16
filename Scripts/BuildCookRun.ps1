# BuildCookRun.ps1
# Build, cook, and package the Unreal project

param(
    [string]$Platform = "Win64",
    [string]$Configuration = "Development",
    [string]$UEVersion = "5.4",
    [switch]$Cook,
    [switch]$Build,
    [switch]$Stage,
    [switch]$Pak,
    [switch]$Archive,
    [string]$ArchiveDirectory = "$env:USERPROFILE\UnrealBuilds\MyUEStarter"
)

# Find UE installation
$UERoot = "C:\Program Files\Epic Games\UE_$UEVersion"
if (-not (Test-Path $UERoot)) {
    Write-Error "Unreal Engine $UEVersion not found at $UERoot"
    exit 1
}

$env:UE_ROOT = $UERoot
$env:UE_BUILD = Join-Path $UERoot "Engine\Build\BatchFiles"

# Find project file
$ProjectFile = Get-ChildItem -Path .. -Filter "*.uproject" | Select-Object -First 1
if (-not $ProjectFile) {
    Write-Error "No .uproject file found in parent directory"
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Building Project: $($ProjectFile.Name)" -ForegroundColor Green
Write-Host "Platform: $Platform" -ForegroundColor Yellow
Write-Host "Configuration: $Configuration" -ForegroundColor Yellow
Write-Host "UE Version: $UEVersion" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

# Build argument string
$Arguments = @(
    "BuildCookRun",
    "-project=`"$($ProjectFile.FullName)`"",
    "-platform=$Platform",
    "-clientconfig=$Configuration"
)

if ($Cook) { $Arguments += "-cook" }
if ($Build) { $Arguments += "-build" }
if ($Stage) { $Arguments += "-stage" }
if ($Pak) { $Arguments += "-pak" }
if ($Archive) {
    $Arguments += "-archive"
    $Arguments += "-archivedirectory=`"$ArchiveDirectory`""
}

Write-Host "Running UAT with arguments:" -ForegroundColor Cyan
Write-Host ($Arguments -join " ") -ForegroundColor Gray

# Run UAT
& "$env:UE_BUILD\RunUAT.bat" $Arguments

if ($LASTEXITCODE -eq 0) {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Build completed successfully!" -ForegroundColor Green
    if ($Archive) {
        Write-Host "Output location: $ArchiveDirectory" -ForegroundColor Yellow
    }
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Error "Build failed with exit code: $LASTEXITCODE"
    exit $LASTEXITCODE
}
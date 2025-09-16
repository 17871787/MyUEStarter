# GenerateFiles.ps1
# Generate Visual Studio project files for the Unreal project

param(
    [string]$UEVersion = "5.4"
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

Write-Host "Generating project files for: $($ProjectFile.Name)" -ForegroundColor Green
Write-Host "Using UE at: $UERoot" -ForegroundColor Cyan

# Generate project files
& "$env:UE_BUILD\GenerateProjectFiles.bat" -project="$($ProjectFile.FullName)"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Project files generated successfully!" -ForegroundColor Green

    # Open solution if exists
    $SolutionFile = Get-ChildItem -Path .. -Filter "*.sln" | Select-Object -First 1
    if ($SolutionFile) {
        Write-Host "Solution file: $($SolutionFile.Name)" -ForegroundColor Yellow
        Write-Host "You can now open this in Visual Studio" -ForegroundColor Yellow
    }
} else {
    Write-Error "Failed to generate project files"
    exit $LASTEXITCODE
}
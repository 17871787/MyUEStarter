# Setup.ps1
# Quick setup script for new developers

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MyUEStarter Project Setup" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

# Check for required tools
Write-Host "`nChecking required tools..." -ForegroundColor Yellow

$tools = @{
    "Git" = "git"
    "GitHub CLI" = "gh"
    "Git LFS" = "git-lfs"
}

$missingTools = @()
foreach ($tool in $tools.GetEnumerator()) {
    if (Get-Command $tool.Value -ErrorAction SilentlyContinue) {
        Write-Host "✓ $($tool.Key) found" -ForegroundColor Green
    } else {
        Write-Host "✗ $($tool.Key) not found" -ForegroundColor Red
        $missingTools += $tool.Key
    }
}

if ($missingTools.Count -gt 0) {
    Write-Host "`nInstalling missing tools..." -ForegroundColor Yellow
    if ("Git" -in $missingTools) {
        winget install --id Git.Git -e --source winget
    }
    if ("GitHub CLI" -in $missingTools) {
        winget install --id GitHub.cli -e --source winget
    }
    if ("Git LFS" -in $missingTools) {
        git lfs install
    }
}

# Pull LFS files
Write-Host "`nPulling Git LFS files..." -ForegroundColor Yellow
git lfs fetch --all
git lfs pull

# Check for Unreal Engine
Write-Host "`nChecking for Unreal Engine..." -ForegroundColor Yellow
$UEVersions = @("5.5", "5.4", "5.3", "5.2", "5.1", "5.0")
$UEFound = $false

foreach ($version in $UEVersions) {
    $path = "C:\Program Files\Epic Games\UE_$version"
    if (Test-Path $path) {
        Write-Host "✓ Found Unreal Engine $version at $path" -ForegroundColor Green
        $env:UE_VERSION = $version
        $env:UE_ROOT = $path
        $env:UE_BUILD = Join-Path $path "Engine\Build\BatchFiles"
        $UEFound = $true
        break
    }
}

if (-not $UEFound) {
    Write-Warning "Unreal Engine not found in standard location. Please install from Epic Games Launcher."
}

# Create Config/DefaultEngine.ini if it doesn't exist
if (-not (Test-Path "..\Config\DefaultEngine.ini")) {
    Write-Host "`nCreating default config..." -ForegroundColor Yellow
    @"
[/Script/EngineSettings.GameMapsSettings]
GameDefaultMap=/Game/Maps/Default.Default
EditorStartupMap=/Game/Maps/Default.Default

[/Script/Engine.RendererSettings]
r.DefaultFeature.AutoExposure.ExtendDefaultLuminanceRange=True

[/Script/HardwareTargeting.HardwareTargetingSettings]
TargetedHardwareClass=Desktop
AppliedTargetedHardwareClass=Desktop
DefaultGraphicsPerformance=Maximum
AppliedDefaultGraphicsPerformance=Maximum
"@ | Out-File -Encoding utf8 "..\Config\DefaultEngine.ini"
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Run .\GenerateFiles.ps1 to generate Visual Studio project files" -ForegroundColor White
Write-Host "2. Open the .sln file in Visual Studio" -ForegroundColor White
Write-Host "3. Or open the .uproject file directly in Unreal Editor" -ForegroundColor White
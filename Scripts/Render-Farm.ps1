# Render-Farm.ps1
# Capture high-resolution screenshot of the farm

param(
    [string]$UEVersion = "5.6",
    [string]$ProjectPath = "C:\Users\jtowe\OneDrive\Documents\Unreal Projects\MyUEStarter\MyUEStarter.uproject",
    [string]$Resolution = "2560x1440",
    [string]$Map = "L2"
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
Write-Host "Rendering Dairy Farm $Map" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Resolution: $Resolution" -ForegroundColor Yellow
Write-Host "Level: $levelPath" -ForegroundColor Yellow

# Create render script
$renderScript = @"
import unreal
import time

def render_screenshot():
    print("Capturing high-resolution screenshot...")

    # Load the level
    level_path = '$levelPath'
    if unreal.EditorAssetLibrary.does_asset_exist(level_path):
        unreal.EditorLevelLibrary.load_level(level_path)
        time.sleep(2)  # Wait for level to load

    # Execute console command for high-res screenshot
    unreal.SystemLibrary.execute_console_command(
        unreal.EditorLevelLibrary.get_editor_world(),
        'HighResShot $Resolution'
    )

    print("Screenshot command executed")
    print("Check: Saved/Screenshots/Windows/")

    # Save level state
    unreal.EditorLevelLibrary.save_current_level()

render_screenshot()
"@

# Save render script temporarily
$tempScript = "$env:TEMP\render_farm_temp.py"
$renderScript | Out-File -FilePath $tempScript -Encoding UTF8

# Execute render
Write-Host "`nExecuting render..." -ForegroundColor Cyan
& "$UEBin\UnrealEditor-Cmd.exe" "$ProjectPath" -ExecutePythonScript="$tempScript" -nosplash -unattended

# Clean up temp script
Remove-Item $tempScript -ErrorAction SilentlyContinue

# Find screenshots
$screenshotPath = Join-Path (Split-Path $ProjectPath) "Saved\Screenshots\Windows"

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Render Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nScreenshots saved to:" -ForegroundColor Cyan
Write-Host "  $screenshotPath" -ForegroundColor White

# List recent screenshots
if (Test-Path $screenshotPath) {
    $screenshots = Get-ChildItem $screenshotPath -Filter "*.png" | Sort-Object LastWriteTime -Descending | Select-Object -First 5
    if ($screenshots) {
        Write-Host "`nRecent screenshots:" -ForegroundColor Yellow
        foreach ($shot in $screenshots) {
            Write-Host "  - $($shot.Name) ($([math]::Round($shot.Length / 1MB, 2)) MB)" -ForegroundColor White
        }
    }
}
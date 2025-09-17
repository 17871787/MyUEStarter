# Fix-Farm-Setup.ps1
# Diagnostic and fix script for farm generation issues

# --- Paths ---
$Proj = "C:\Users\jtowe\OneDrive\Documents\Unreal Projects\MyUEStarter\MyUEStarter.uproject"
$ProjDir = Split-Path $Proj
$UE_ROOT = "C:\Program Files\Epic Games\UE_5.6"
$UE_BIN  = Join-Path $UE_ROOT "Engine\Binaries\Win64"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Dairy Farm Setup Diagnostic & Fix" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

# 1) Force-enable Python plugins
Write-Host "`n[1] Checking Python plugins..." -ForegroundColor Yellow
$uprojectContent = Get-Content $Proj -Raw
$uprojectJson = $uprojectContent | ConvertFrom-Json

# Ensure plugins array exists
if (-not $uprojectJson.Plugins) {
    $uprojectJson | Add-Member -Name "Plugins" -MemberType NoteProperty -Value @()
}

# Check and add required plugins
$requiredPlugins = @("PythonScriptPlugin", "EditorScriptingUtilities")
foreach ($pluginName in $requiredPlugins) {
    $plugin = $uprojectJson.Plugins | Where-Object { $_.Name -eq $pluginName }
    if (-not $plugin) {
        Write-Host "  Adding plugin: $pluginName" -ForegroundColor Cyan
        $uprojectJson.Plugins += [pscustomobject]@{
            Name = $pluginName
            Enabled = $true
        }
    } else {
        Write-Host "  Plugin already enabled: $pluginName" -ForegroundColor Green
        $plugin.Enabled = $true
    }
}

# Save updated .uproject
$uprojectJson | ConvertTo-Json -Depth 10 | Set-Content -Encoding utf8 $Proj
Write-Host "  Plugins configuration saved" -ForegroundColor Green

# 2) Fix DefaultEngine.ini to use L1 first (simpler)
Write-Host "`n[2] Setting default map to L1..." -ForegroundColor Yellow
$EngineIni = Join-Path $ProjDir "Config\DefaultEngine.ini"

# Read existing content and update map settings
$engineContent = Get-Content $EngineIni -Raw
if ($engineContent -match "EditorStartupMap=/Game/Farm/Maps/DairyFarm_L2") {
    $engineContent = $engineContent -replace "DairyFarm_L2", "DairyFarm_L1"
    $engineContent | Set-Content -Encoding utf8 $EngineIni
    Write-Host "  Changed startup map from L2 to L1" -ForegroundColor Green
} else {
    Write-Host "  Startup map already set to L1" -ForegroundColor Green
}

# 3) Verify Python scripts exist
Write-Host "`n[3] Verifying Python scripts..." -ForegroundColor Yellow
$scripts = @(
    "Scripts\ue\materials_build.py",
    "Scripts\ue\farm_generate.py",
    "Scripts\ue\farm_simulate.py"
)

foreach ($script in $scripts) {
    $scriptPath = Join-Path $ProjDir $script
    if (Test-Path $scriptPath) {
        Write-Host "  ✓ $script" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $script MISSING!" -ForegroundColor Red
    }
}

# 4) Re-run generation with logging
Write-Host "`n[4] Re-generating farm with logging..." -ForegroundColor Yellow
$Log = Join-Path $ProjDir "Scripts\last_gen_log.txt"
Remove-Item $Log -ErrorAction SilentlyContinue

$MatPy = Join-Path $ProjDir "Scripts\ue\materials_build.py"
$GenPy = Join-Path $ProjDir "Scripts\ue\farm_generate.py"
$SimPy = Join-Path $ProjDir "Scripts\ue\farm_simulate.py"

Write-Host "  Running materials_build.py..." -ForegroundColor Cyan
& "$UE_BIN\UnrealEditor-Cmd.exe" "$Proj" -unattended -nosplash -ExecutePythonScript="$MatPy" 2>&1 | Out-File -Append $Log

Write-Host "  Running farm_generate.py..." -ForegroundColor Cyan
& "$UE_BIN\UnrealEditor-Cmd.exe" "$Proj" -unattended -nosplash -ExecutePythonScript="$GenPy" 2>&1 | Out-File -Append $Log

Write-Host "  Running farm_simulate.py..." -ForegroundColor Cyan
& "$UE_BIN\UnrealEditor-Cmd.exe" "$Proj" -unattended -nosplash -ExecutePythonScript="$SimPy" 2>&1 | Out-File -Append $Log

# 5) Check for errors in log
Write-Host "`n[5] Checking generation log..." -ForegroundColor Yellow
if (Test-Path $Log) {
    $logContent = Get-Content $Log -Raw
    if ($logContent -match "error|exception|failed" -and $logContent -notmatch "LogPython: Warning") {
        Write-Host "  Errors found in log!" -ForegroundColor Red
        Get-Content $Log -Tail 30
    } else {
        Write-Host "  Generation completed without errors" -ForegroundColor Green
    }
}

# 6) Create debug script to list maps
Write-Host "`n[6] Checking created maps..." -ForegroundColor Yellow
$DebugPy = Join-Path $ProjDir "Scripts\ue\_debug_maps.py"
@"
import unreal

print("\n=== Checking for Farm Maps ===")

# Check if directories exist
if unreal.EditorAssetLibrary.does_directory_exist('/Game/Farm'):
    print("✓ /Game/Farm directory exists")

    if unreal.EditorAssetLibrary.does_directory_exist('/Game/Farm/Maps'):
        print("✓ /Game/Farm/Maps directory exists")

        # List all assets in Maps folder
        assets = unreal.EditorAssetLibrary.list_assets('/Game/Farm/Maps')
        print(f"\nFound {len(assets)} assets in /Game/Farm/Maps:")
        for asset in assets:
            print(f"  - {asset}")

        # Check specific maps
        l1_map = '/Game/Farm/Maps/DairyFarm_L1'
        l2_map = '/Game/Farm/Maps/DairyFarm_L2'

        if unreal.EditorAssetLibrary.does_asset_exist(l1_map):
            print(f"\n✓ L1 map exists: {l1_map}")
        else:
            print(f"\n✗ L1 map NOT found: {l1_map}")

        if unreal.EditorAssetLibrary.does_asset_exist(l2_map):
            print(f"✓ L2 map exists: {l2_map}")
        else:
            print(f"✗ L2 map NOT found: {l2_map}")
    else:
        print("✗ /Game/Farm/Maps directory NOT found")
else:
    print("✗ /Game/Farm directory NOT found")
"@ | Set-Content -Encoding utf8 $DebugPy

& "$UE_BIN\UnrealEditor-Cmd.exe" "$Proj" -unattended -nosplash -ExecutePythonScript="$DebugPy"

# 7) Add PlayerStart and Camera to L1
Write-Host "`n[7] Adding PlayerStart and Camera..." -ForegroundColor Yellow
$CameraPy = Join-Path $ProjDir "Scripts\ue\_add_camera.py"
@"
import unreal

print("Adding PlayerStart and Camera to DairyFarm_L1...")

# Try to load L1 map
map_path = '/Game/Farm/Maps/DairyFarm_L1'
if unreal.EditorAssetLibrary.does_asset_exist(map_path):
    unreal.EditorLevelLibrary.load_level(map_path)

    # Add PlayerStart near yard
    player_start = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.PlayerStart,
        unreal.Vector(0, -500, 100),
        unreal.Rotator(0, 90, 0)
    )
    if player_start:
        print("✓ PlayerStart added")

    # Add Camera for overview
    camera = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.CameraActor,
        unreal.Vector(1000, -1000, 500),
        unreal.Rotator(-20, 45, 0)
    )
    if camera:
        print("✓ Camera added")

    # Save the level
    unreal.EditorLevelLibrary.save_current_level()
    print("Level saved with PlayerStart and Camera")
else:
    print(f"ERROR: Map not found: {map_path}")
"@ | Set-Content -Encoding utf8 $CameraPy

& "$UE_BIN\UnrealEditor-Cmd.exe" "$Proj" -unattended -nosplash -ExecutePythonScript="$CameraPy"

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Diagnostic Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Open the project:" -ForegroundColor White
Write-Host "   & '$UE_BIN\UnrealEditor.exe' '$Proj' '/Game/Farm/Maps/DairyFarm_L1'" -ForegroundColor Gray
Write-Host "`n2. If still blank, check:" -ForegroundColor White
Write-Host "   - Output Log for Python errors" -ForegroundColor Gray
Write-Host "   - Content Browser > Farm > Maps folder" -ForegroundColor Gray
Write-Host "   - World Outliner for actors" -ForegroundColor Gray
Write-Host "   - Viewport camera position (G key for game view)" -ForegroundColor Gray
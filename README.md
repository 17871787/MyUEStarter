# MyUEStarter

CLI-first Unreal Engine project optimized for AI-assisted development.

## 🐄 Dairy Farm Scene Generator L2

Enhanced procedural dairy farm with sublevels, UI controls, density management, rotational grazing, and one-click renders.

## L2 Quickstart

### 🚀 Generate L2 Farm:
```powershell
.\Scripts\Gen-Farm.ps1        # Generates L2 by default
.\Scripts\Gen-Farm.ps1 -Map L1  # Generate L1 version
```

### 👀 Open in Editor:
```powershell
.\Scripts\Open-Farm.ps1       # Opens L2
.\Scripts\Open-Farm.ps1 -Map L1
```

### 📸 Render Screenshot:
```powershell
.\Scripts\Render-Farm.ps1     # 2560x1440 screenshot
```

### 🐄 Update Animals:
```powershell
.\Scripts\Update-Animals.ps1  # Regenerate with current density
.\Scripts\Update-Animals.ps1 -Density 2.5  # Change density
.\Scripts\Update-Animals.ps1 -Rotate       # Force rotation
```

### 📦 Package for Distribution:
```powershell
.\Scripts\Package-Farm.ps1    # Build Win64 package
```

### Direct Commands:
```powershell
# Generate materials only
& "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "C:\Users\jtowe\OneDrive\Documents\Unreal Projects\MyUEStarter\MyUEStarter.uproject" -ExecutePythonScript="Scripts/ue/materials_build.py"

# Generate farm scene
& "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "C:\Users\jtowe\OneDrive\Documents\Unreal Projects\MyUEStarter\MyUEStarter.uproject" -ExecutePythonScript="Scripts/ue/farm_generate.py"

# Open the map (GUI)
& "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\Win64\UnrealEditor.exe" "C:\Users\jtowe\OneDrive\Documents\Unreal Projects\MyUEStarter\MyUEStarter.uproject" "/Game/Farm/Maps/DairyFarm_L1"
```

## L2 Features

### Configuration (v2)
Edit `Content/Farm/Data/farm_config_v2.json`:
- **Paddocks**: 6 (configurable)
- **Stocking density**: 2.0 cows/ha (auto-calculates total)
- **Min/max cows**: 30-150
- **Rotation days**: 2
- **Time of day**: 0-24 hours
- **NavMesh visibility**: true/false

### Grazing State
`Content/Farm/Data/GrazingState.json` tracks:
- Active paddock index
- Last rotation timestamp

### Input Controls (In-Editor)
- **T**: Toggle day/night (13:00 ↔ 03:00)
- **R**: Regenerate animals
- **[/]**: Previous/Next hour
- **P**: Toggle pause
- **1-6**: Focus camera to paddock N

## Quick Commands (PowerShell)

### Generate project files:
```powershell
& "$env:UE_BUILD\GenerateProjectFiles.bat" -project="$(Get-Item *.uproject)"
```

### Package Win64 (Development):
```powershell
& "$env:UE_BUILD\RunUAT.bat" BuildCookRun -project="$(Get-Item *.uproject)" -platform=Win64 -clientconfig=Development -cook -build -stage -pak -archive -archivedirectory="$env:USERPROFILE\UnrealBuilds\MyUEStarter"
```

## Helper Scripts

### Farm Generation
- `Scripts\Gen-Farm.ps1` - Generate complete dairy farm scene
- `Scripts\Open-Farm.ps1` - Open farm in Unreal Editor
- `Scripts\ue\materials_build.py` - Create farm materials
- `Scripts\ue\farm_generate.py` - Generate farm scene
- `Scripts\ue\farm_simulate.py` - Add cow behaviors

### Project Tools
- `Scripts\BuildCookRun.ps1` - Build, cook and package the project
- `Scripts\GenerateFiles.ps1` - Generate Visual Studio project files
- `Scripts\Setup.ps1` - Initial project setup

## Git LFS Workflow

### Lock files before editing:
```powershell
git lfs lock "Content/Maps/Example.umap"
```

### Unlock after editing:
```powershell
git lfs unlock "Content/Maps/Example.umap"
```

### View current locks:
```powershell
git lfs locks
```

## Daily Workflow

```powershell
# Pull latest, get locks
git pull --rebase
git lfs fetch --all

# Create feature branch
git checkout -b feat/your-feature

# Lock any maps before editing
git lfs lock "Content/Maps/YourMap.umap"

# Work, then commit
git add -A
git commit -m "feat: your changes"

# Push & open PR
git push -u origin HEAD
gh pr create --fill
```
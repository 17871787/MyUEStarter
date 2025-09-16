# MyUEStarter

CLI-first Unreal Engine project optimized for AI-assisted development.

## 🐄 Dairy Farm Scene Generator

Procedural dairy farm scene with CLI generation, featuring yard buildings, paddocks, fences, cows, and dynamic lighting.

### 🚀 Generate Dairy Farm (One Command):
```powershell
.\Scripts\Gen-Farm.ps1
```

### 👀 Open Farm in Editor:
```powershell
.\Scripts\Open-Farm.ps1
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

## Farm Configuration

Edit `Content/Farm/Data/farm_config.json` to customize:
- Number of paddocks (default: 4)
- Cow count (default: 60)
- Time of day (default: 15.5 hours)
- Building sizes and positions
- Lane route points
- Fence spacing

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
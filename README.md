# MyUEStarter

CLI-first Unreal Engine project optimized for AI-assisted development.

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
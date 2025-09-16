# GitHubSetup.ps1
# Complete GitHub repository setup

$ghPath = "C:\Program Files\GitHub CLI\gh.exe"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GitHub Repository Setup for MyUEStarter" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

# Check if already authenticated
Write-Host "`nChecking GitHub authentication..." -ForegroundColor Yellow
$authStatus = & $ghPath auth status 2>&1

if ($authStatus -like "*not logged*") {
    Write-Host "You need to authenticate with GitHub." -ForegroundColor Yellow
    Write-Host "Running GitHub authentication..." -ForegroundColor Cyan
    & $ghPath auth login
}

# After authentication, create and push the repository
Write-Host "`nCreating GitHub repository..." -ForegroundColor Yellow
$repoName = "MyUEStarter"

# Try to create the repository
try {
    # Create as private by default (change to --public if you prefer)
    & $ghPath repo create $repoName --source . --push --private --description "CLI-first Unreal Engine starter project"

    Write-Host "========================================" -ForegroundColor Green
    Write-Host "SUCCESS! Repository created and pushed!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green

    # Show the repo URL
    $repoInfo = & $ghPath repo view --json url | ConvertFrom-Json
    Write-Host "Repository URL: $($repoInfo.url)" -ForegroundColor Cyan

} catch {
    Write-Error "Failed to create repository. You may need to:"
    Write-Host "1. Run: gh auth login" -ForegroundColor Yellow
    Write-Host "2. Then run this script again" -ForegroundColor Yellow
}
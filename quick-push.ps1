# Quick GitHub Push Script
param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubUsername
)

Write-Host "========================================" -ForegroundColor Green
Write-Host "Setting up GitHub remote for MyUEStarter" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Green

# Add remote
$repoUrl = "https://github.com/$GitHubUsername/MyUEStarter.git"
Write-Host "`nAdding remote: $repoUrl" -ForegroundColor Yellow

git remote add origin $repoUrl
git branch -M main

Write-Host "`nPushing to GitHub..." -ForegroundColor Yellow
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "SUCCESS! Project pushed to GitHub!" -ForegroundColor Green
    Write-Host "Repository: https://github.com/$GitHubUsername/MyUEStarter" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host "`n========================================" -ForegroundColor Red
    Write-Host "Push failed. Make sure you:" -ForegroundColor Yellow
    Write-Host "1. Created the repository on GitHub.com" -ForegroundColor White
    Write-Host "2. Have the correct username" -ForegroundColor White
    Write-Host "3. Are authenticated (you may be prompted for credentials)" -ForegroundColor White
    Write-Host "========================================" -ForegroundColor Red
}
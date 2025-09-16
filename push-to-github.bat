@echo off
echo ========================================
echo Pushing MyUEStarter to GitHub
echo ========================================

cd /d "C:\Users\jtowe\OneDrive\Documents\Unreal Projects\MyUEStarter"

echo.
echo Current Git status:
git status

echo.
echo You need to:
echo 1. Create a new repository on GitHub.com named "MyUEStarter"
echo    Go to: https://github.com/new
echo    - Repository name: MyUEStarter
echo    - Make it Private or Public as you prefer
echo    - DO NOT initialize with README, .gitignore, or license
echo.
echo 2. After creating the empty repo, run these commands:
echo.
echo    git remote add origin https://github.com/YOUR_USERNAME/MyUEStarter.git
echo    git branch -M main
echo    git push -u origin main
echo.
pause
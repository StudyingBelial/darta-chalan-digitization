@echo off
setlocal

title Auto Git Commit - NTC Darta Chalan

echo ============================================================================
echo   [NTC] Auto Git Commit Runner
echo ============================================================================

git status

echo.
echo [1/3] Staging all project files...
git add -A

echo.
echo [2/3] Excluding user and sysadmin markdown guides from commit...
git reset FRONTEND_USER_GUIDE.md SYSADMIN_GUIDE.md >nul 2>&1

echo.
echo [3/3] Committing changes...
git commit -m "feat: complete darta-chalan digitization platform with universal runner, hardware scanner intake, and test suite"

echo.
echo ============================================================================
echo Git status after commit:
git status
echo ============================================================================
echo Commit completed. Run 'git push origin develop' to push to remote when ready.

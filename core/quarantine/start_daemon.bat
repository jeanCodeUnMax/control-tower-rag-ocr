@echo off
echo ========================================
echo  DEMARRAGE CONSCIENCE DAEMON (HEPHAISTOS)
echo ========================================
cd /d "%~dp0"

:: Le script Python gère maintenant ses propres chemins absolus via PROJECT_ROOT
:: On vérifie juste le statut

echo [1/2] Verification statut...
python conscience_daemon.py --status

echo [2/2] Demarrage daemon...
:: On le lance, il se mettra en arrière-plan lui-même ou on utilise start
start /B python conscience_daemon.py

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo  STATUT FINAL:
python conscience_daemon.py --status
echo ========================================
echo.
echo Le daemon tourne en arriere-plan.
echo Les logs sont dans .agent/conscience_daemon.log (racine project)
pause

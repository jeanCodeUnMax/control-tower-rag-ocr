@echo off
title Control Tower RAG OCR - Launcher

echo ===================================================
echo   Lancement de Control Tower RAG OCR
echo ===================================================
echo.

echo [1/2] Demarrage du Backend (FastAPI) sur le port 8000...
start "Control Tower - Backend" cmd /k "set PYTHONPATH=src&& .venv\Scripts\uvicorn control_tower.api.app:app --reload --port 8000"

echo [2/2] Demarrage du Frontend (Vite)...
cd frontend
start "Control Tower - Frontend" cmd /k "npm run dev"
cd ..

echo.
echo Les deux services ont ete lances dans de nouvelles fenetres.
echo - Backend API : http://localhost:8000/docs
echo - Frontend UI : Le lien s'affichera dans la console Vite (generalement http://localhost:5173)
echo.
pause

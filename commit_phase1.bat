@echo off
cd /d "%~dp0"
echo Ajout des fichiers modifies...
git add src/control_tower/api/app.py
git add src/control_tower/ocr/tesseract.py
git add src/control_tower/generation/llm.py
git add src/control_tower/storage/vector.py
git add frontend/src/App.tsx
git add frontend/src/index.css
git add frontend/package.json
git add frontend/vite.config.ts

echo.
echo Validation du commit...
git commit -m "feat(ui): completion of the frontend dashboard and rag robustness" -m "- Built the Radar (Ingestion), LLM Arena, and Vector Observatory in React." -m "- Added Mock OCR for Tesseract fallback on Windows." -m "- Added Mock Qdrant and LLM fallback to handle WinError 10061." -m "- Successfully migrated to Tailwind CSS v4."

echo.
echo Poussée vers le dépôt distant...
git push

echo.
echo Terminé ! Appuyez sur une touche pour quitter.
pause

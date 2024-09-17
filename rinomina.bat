@echo off
echo Verifica dell'ambiente Python...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python non trovato. Assicurati che Python sia installato e aggiunto al PATH.
    pause
    exit /b 1
)

echo Creazione dell'ambiente virtuale...
python -m venv venv
if %errorlevel% neq 0 (
    echo Errore nella creazione dell'ambiente virtuale.
    pause
    exit /b 1
)

echo Attivazione dell'ambiente virtuale...
call venv\Scripts\activate

echo Installazione delle dipendenze...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Errore nell'installazione delle dipendenze.
    pause
    exit /b 1
)

echo.
echo Avvio del programma...
python renamefileAI.py

echo.
echo Disattivazione dell'ambiente virtuale...
deactivate

pause

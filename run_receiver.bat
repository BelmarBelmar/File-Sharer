@echo off
REM Déterminer le dossier où se trouve le script
set SCRIPT_DIR=%~dp0

REM Supprimer le \ final si présent
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

REM Chemins vers les scripts Python
set SOCKET_SERVER_PATH=%SCRIPT_DIR%\socket_server.py
set MAIN_PATH=%SCRIPT_DIR%\main.py

REM Chercher python dans l'environnement virtuel s'il existe
IF DEFINED VIRTUAL_ENV (
    set PYTHON=%VIRTUAL_ENV%\Scripts\python.exe
) ELSE (
    where python >nul 2>nul
    IF %ERRORLEVEL% EQU 0 (
        for /f "usebackq delims=" %%p in (`where python`) do set PYTHON=%%p & goto :foundpython
    ) ELSE (
        echo Erreur : Aucun exécutable Python trouvé dans le PATH.
        pause
        exit /b 1
    )
)

:foundpython
REM Vérifier si l'exécutable Python existe
if not exist "%PYTHON%" (
    echo Erreur : Python n'est pas installé à %PYTHON%.
    pause
    exit /b 1
)

REM Vérifier si socket_server.py existe
if not exist "%SOCKET_SERVER_PATH%" (
    echo Erreur : socket_server.py introuvable à %SOCKET_SERVER_PATH%
    pause
    exit /b 1
)

REM Vérifier si tkinter est disponible
%PYTHON% -c "import tkinter" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Erreur : tkinter n'est pas installé.
    echo Sous Windows, il faut souvent réinstaller Python avec l'option Tcl/tk cochée.
    pause
    exit /b 1
)

REM Installer tqdm si nécessaire
echo Installation silencieuse de tqdm si nécessaire...
%PYTHON% -m pip install tqdm --quiet

REM Lancer socket_server.py en arrière-plan avec un délai
echo Lancement de socket_server.py...
start "socket_server" cmd /c ""%PYTHON%" "%SOCKET_SERVER_PATH%""
timeout /t 2 >nul  # Attendre 2 secondes pour que le serveur démarre

REM Vérifier et lancer main.py si disponible
if exist "%MAIN_PATH%" (
    echo Lancement de main.py...
    start "main_py" cmd /c ""%PYTHON%" "%MAIN_PATH%""
) else (
    echo Attention : main.py introuvable à %MAIN_PATH%
    pause
    exit /b 1
)

echo Lancement terminé. Appuyez sur une touche pour quitter.
pause
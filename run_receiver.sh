#!/bin/bash

# Déterminer le dossier où se trouve le script run_receiver.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Chemins vers les scripts Python
MAIN_PATH="$SCRIPT_DIR/main.py"
SOCKET_SERVER_PATH="$SCRIPT_DIR/socket_server.py"

# Trouver l'exécutable Python3 dynamiquement
if [ -n "$VIRTUAL_ENV" ]; then
    PYTHON="$VIRTUAL_ENV/bin/python3"
else
    PYTHON=$(command -v python3 2>/dev/null || command -v python 2>/dev/null)
    if [ -z "$PYTHON" ]; then
        echo "Erreur : Aucun exécutable Python3 trouvé dans le PATH."
        exit 1
    fi
fi

# Vérifier si l'exécutable Python existe
if ! command -v "$PYTHON" &> /dev/null; then
    echo "Erreur : Python3 n'est pas installé à $PYTHON."
    exit 1
fi

# Vérifier si main.py existe
if [ ! -f "$MAIN_PATH" ]; then
    echo "Erreur : main.py introuvable à $MAIN_PATH"
    exit 1
fi

# Vérifier si socket_server.py existe
if [ ! -f "$SOCKET_SERVER_PATH" ]; then
    echo "Erreur : socket_server.py introuvable à $SOCKET_SERVER_PATH"
    exit 1
fi

# Vérifier si tkinter est disponible
if ! "$PYTHON" -c "import tkinter" 2>/dev/null; then
    echo "Erreur : tkinter n'est pas installé. Essayez : sudo apt-get install python3-tk"
    exit 1
fi

# Installer tqdm si nécessaire
"$PYTHON" -m pip install tqdm --user --quiet

# Lancer main.py en premier plan
"$PYTHON" "$MAIN_PATH"
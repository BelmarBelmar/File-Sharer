#!/bin/bash

# Déterminer le dossier où se trouve le script run_receiver.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Chemins vers les scripts Python
SOCKET_SERVER_PATH="$SCRIPT_DIR/socket_server.py"
MAIN_PATH="$SCRIPT_DIR/main.py"

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

# Vérifier si socket_server.py existe
if [ ! -f "$SOCKET_SERVER_PATH" ]; then
    echo "Erreur : socket_server.py introuvable à $SOCKET_SERVER_PATH"
    exit 1
fi

# Vérifier si tkinter est disponible (nécessaire pour socket_server.py)
if ! "$PYTHON" -c "import tkinter" 2>/dev/null; then
    echo "Erreur : tkinter n'est pas installé. Essayez : sudo apt-get install python3-tk"
    exit 1
fi

# Installer tqdm si nécessaire
"$PYTHON" -m pip install tqdm --user --quiet

# Lancer socket_server.py en arrière-plan pour maintenir le port ouvert
echo "Lancement de socket_server.py sur le port 5001..."
"$PYTHON" "$SOCKET_SERVER_PATH" &

# Vérifier et lancer main.py si disponible
if [ -f "$MAIN_PATH" ]; then
    echo "Lancement de main.py..."
    "$PYTHON" "$MAIN_PATH" &
else
    echo "Attention : main.py introuvable à $MAIN_PATH. Seule socket_server.py est lancée."
fi

echo "Le serveur est en cours d'exécution. Appuyez sur Ctrl+C dans ce terminal pour arrêter."
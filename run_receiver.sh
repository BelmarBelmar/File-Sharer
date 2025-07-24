#!/bin/bash

# Déterminer le dossier où se trouve le script run_receiver.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Chemin vers receiver.py (dans le même dossier que run_receiver.sh)
SCRIPT_PATH="$SCRIPT_DIR/receiver.py"

# Trouver l'exécutable Python3 dynamiquement
if [ -n "$VIRTUAL_ENV" ]; then
    # Si un environnement virtuel est activé, utiliser son Python
    PYTHON="$VIRTUAL_ENV/bin/python3"
else
    # Sinon, chercher python3 dans le PATH
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

# Vérifier si receiver.py existe
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Erreur : receiver.py introuvable à $SCRIPT_PATH"
    exit 1
fi

# Vérifier si tkinter est disponible
if ! "$PYTHON" -c "import tkinter" 2>/dev/null; then
    echo "Erreur : tkinter n'est pas installé. Essayez : sudo apt-get install python3-tk"
    exit 1
fi

# Installer tqdm si nécessaire
"$PYTHON" -m pip install tqdm --user --quiet

# Lancer receiver.py en arrière-plan avec nohup
nohup "$PYTHON" "$SCRIPT_PATH" &

# Afficher le PID du processus
echo "receiver.py lancé en arrière-plan avec PID $!"
echo "Les logs sont écrits dans $SCRIPT_DIR/nohup.out"
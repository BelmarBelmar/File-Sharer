import curses

def matrix_effect(stdscr):
    curses.curs_set(0)  # Cache le curseur
    height, width = stdscr.getmaxyx()  # Obtient la taille de la fenêtre
    stdscr.nodelay(1)  # Pour que getch ne bloque pas l'exécution
    stdscr.timeout(100)  # Met un délai pour que l'animation fonctionne

    # Définir les couleurs
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)

    while True:
        stdscr.clear()  # Efface l'écran

        for i in range(height):
            stdscr.addstr(i, 0, 'A' * width, curses.color_pair(1))  # Affiche des 'A' en vert
        
        stdscr.refresh()  # Rafraîchit l'écran

# Lancer le programme
curses.wrapper(matrix_effect)


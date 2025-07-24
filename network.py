import socket
import ipaddress

def is_port_open(ip, port, timeout=0.5):
    """Teste si le port est ouvert sur l'IP donnée"""

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((str(ip), port))
        s.close()
        return result == 0
    except Exception:
        return False

def scan_ip(ip, port):
    """
    Scanne une seule IP pour vérifier si elle écoute sur le port donné.
    """
    print(f"🔍 Scan de l'IP {ip} sur le port {port}...")
    if is_port_open(ip, port):
        print(f"✅ Pair trouvé à {ip}")
        return [str(ip)]
    else:
        print(f"❌ {ip} : port fermé ou pair non trouvé")
        return []

def scan_network(network_cidr, port):
    """
    Scanne toutes les IP d'un réseau donné (au format CIDR, ex : '192.168.1.0/24')
    et affiche celles qui ont le port spécifié ouvert.
    """
    print(f"🔍 Scan du réseau {network_cidr} sur le port {port}...\n")
    net = ipaddress.ip_network(network_cidr, strict=False)

    found = []

    for ip in net.hosts():
        if is_port_open(ip, port):
            print(f"✅ Pair trouvé : {ip}")
            found.append(str(ip))
        else:
            print(f"❌ {ip} : port fermé", end='\r')  # écrase la ligne, juste pour suivi

    print("\n\n✅ Scan terminé.")
    print("Pairs détectés :", found)

    return found


if __name__ == "__main__":
    # Exemple d'utilisation
    network = "192.168.1.0/24"   # adapte selon ton réseau local
    port = 5001
    scan_network(network, port)

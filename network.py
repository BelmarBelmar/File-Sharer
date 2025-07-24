import socket
import ipaddress
import subprocess
import platform
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm


def get_local_network():
    """Détecte automatiquement le réseau local auquel le PC est connecté."""
    if platform.system() == "Windows":
        try:
            output = subprocess.check_output("ipconfig", shell=True).decode("cp850", errors="ignore")
            ip, mask = None, None
            for line in output.splitlines():
                if "Adresse IPv4" in line:
                    ip = line.split(":")[1].strip()
                if "Masque de sous-réseau" in line:
                    mask = line.split(":")[1].strip()
            if ip and mask:
                net = ipaddress.ip_network(f"{ip}/{mask}", strict=False)
                print(f"Réseau détecté : {net}")
                return str(net)
            return None
        except Exception as e:
            print(f"Erreur lors de la détection du réseau : {e}")
            return None
    else:  # Linux ou macOS
        try:
            output = subprocess.check_output("ip addr", shell=True).decode()
            for line in output.splitlines():
                if "inet " in line and "wlan" in line:
                    ip_mask = line.strip().split()[1]
                    net = ipaddress.ip_network(ip_mask, strict=False)
                    print(f"Réseau détecté : {net}")
                    return str(net)
            return None
        except Exception as e:
            print(f"Erreur lors de la détection du réseau : {e}")
            return None


def is_port_open(ip, port, timeout=0.3):
    """Teste si le port est ouvert sur l'IP donnée."""
    print(f"Test de {ip}:{port}")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((str(ip), port))
        s.close()
        print(f"Résultat pour {ip}:{port} -> {result}")
        return result == 0
    except socket.timeout:
        print(f"Timeout pour {ip}:{port}")
        return False
    except socket.error as e:
        print(f"Erreur réseau pour {ip}:{port} -> {e}")
        return False


def scan_ip(ip, port):
    """Scanne une seule IP pour vérifier si elle écoute sur le port donné."""
    if is_port_open(ip, port):
        return str(ip)
    return None


def scan_network(network_cidr, port, max_workers=50):
    """Scanne toutes les IP d'un réseau donné et affiche celles avec le port ouvert."""
    print(f"🔍 Scan du réseau {network_cidr} sur le port {port}...\n")
    try:
        net = ipaddress.ip_network(network_cidr, strict=False)
    except ValueError as e:
        print(f"Erreur : Réseau invalide {network_cidr} -> {e}")
        return []

    found = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(scan_ip, ip, port) for ip in net.hosts()]
        for future in tqdm(futures, total=len(futures), desc="Scan en cours"):
            result = future.result()
            if result:
                print(f"✅ Pair trouvé : {result}")
                found.append(result)

    print("\n✅ Scan terminé.")
    print("Pairs détectés :", found)
    return found


if __name__ == "__main__":
    # Détecter automatiquement le réseau local
    network = get_local_network()
    if not network:
        network = "192.168.1.0/24"  # Valeur par défaut
        print(f"⚠️ Détection automatique échouée, utilisation du réseau par défaut : {network}")
    port = 5001
    scan_network(network, port)
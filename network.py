
import socket
import ipaddress
import subprocess
import platform
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

def get_local_network():
    """
    Détecte automatiquement le réseau local auquel le PC est connecté (optimisé pour Linux).
    """
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
                print(f"[NETWORK] Réseau détecté : {net}")
                return str(net)
            return None
        except Exception as e:
            print(f"[ERROR] Erreur lors de la détection du réseau : {e}")
            return None
    else:  # Linux (Kali) ou macOS
        try:
            output = subprocess.check_output("ip addr show | grep inet", shell=True).decode()
            for line in output.splitlines():
                if "inet " in line and ("wlan0" in line or "eth0" in line):  # Interfaces courantes
                    ip_mask = line.strip().split()[1]
                    net = ipaddress.ip_network(ip_mask, strict=False)
                    print(f"[NETWORK] Réseau détecté : {net}")
                    return str(net)
            return None
        except Exception as e:
            print(f"[ERROR] Erreur lors de la détection du réseau : {e}")
            return None

def is_port_open(ip, port, timeout=0.3):
    """
    Teste si le port est ouvert sur l'IP donnée.
    """
    print(f"[NETWORK] Test de {ip}:{port}")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((str(ip), port))
        s.close()
        print(f"[NETWORK] Résultat pour {ip}:{port} -> {result}")
        return result == 0
    except socket.timeout:
        print(f"[NETWORK] Timeout pour {ip}:{port}")
        return False
    except socket.error as e:
        print(f"[NETWORK] Erreur réseau pour {ip}:{port} -> {e}")
        return False

def scan_ip(ip, port):
    """
    Scanne une seule IP pour vérifier si elle écoute sur le port donné.
    """
    if is_port_open(ip, port):
        return str(ip)
    return None

def scan_network(network_cidr, port=5001, max_workers=50):
    """
    Scanne toutes les IP d'un réseau donné et affiche celles avec le port ouvert.
    """
    print(f"🔍 Scan du réseau {network_cidr} sur le port {port}...")
    try:
        net = ipaddress.ip_network(network_cidr, strict=False)
    except ValueError as e:
        print(f"[ERROR] Réseau invalide {network_cidr} -> {e}")
        return []

    found = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(scan_ip, ip, port) for ip in net.hosts()]
        for future in tqdm(futures, total=len(futures), desc="Scan en cours"):
            result = future.result()
            if result:
                print(f"✅ Faire trouvé : {result}")
                found.append(result)

    print("\n✅ Scan terminé.")
    print(f"Pairs détectés : {found}")
    return found

if __name__ == "__main__":
    # Détecter automatiquement le réseau local
    network = get_local_network()
    if not network:
        network = "127.0.0.1/32"  # Valeur par défaut pour tests locaux
        print(f"⚠️ Détection automatique échouée, utilisation du réseau par défaut : {network}")
    scan_network(network, port=5001)

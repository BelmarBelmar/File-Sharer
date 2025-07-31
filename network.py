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
            print("[DEBUG] Sortie brute d'ipconfig :", output)  # Débogage
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
            print("[ERROR] Aucun IP ou masque détecté")
            return None
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Erreur d'exécution d'ipconfig : {e}")
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
            print("[ERROR] Aucun réseau détecté sur wlan0 ou eth0")
            return None
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Erreur d'exécution de ip addr : {e}")
            return None
        except Exception as e:
            print(f"[ERROR] Erreur lors de la détection du réseau : {e}")
            return None

def is_port_open(ip, port, timeout=0.5):
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

def scan_network(network_cidr=None, port=5001, max_workers=50):
    """
    Scanne toutes les IP d'un réseau donné et affiche celles avec le port ouvert.
    Si network_cidr n'est pas fourni, détecte automatiquement le réseau local.
    """
    print(f"🔍 Scan du réseau sur le port {port}...")
    if network_cidr is None:
        network_cidr = get_local_network()
        if not network_cidr:
            print("[WARNING] Détection réseau échouée, forçage vers 192.168.1.0/24 pour test")
            network_cidr = "192.168.1.0/24"  # Forcer une plage courante pour tester
    if not network_cidr:
        print("[ERROR] Réseau non détecté ou invalide")
        return []
    try:
        net = ipaddress.ip_network(network_cidr, strict=False)
    except ValueError as e:
        print(f"[ERROR] Réseau invalide {network_cidr} -> {e}")
        return []

    found = []
    if "127.0.0.1/32" in network_cidr and is_port_open("127.0.0.1", port):
        found.append("127.0.0.1")
        print(f"✅ Pair trouvé : 127.0.0.1")

    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(scan_ip, ip, port) for ip in net.hosts()]
            for future in tqdm(futures, total=len(futures), desc="Scan en cours"):
                result = future.result()
                if result:
                    print(f"✅ Pair trouvé : {result}")
                    found.append(result)
    except Exception as e:
        print(f"[ERROR] Erreur pendant le scan : {e}")
        return found

    if not found:
        print("[INFO] Aucun pair trouvé sur le port 5001. Assurez-vous que socket_server est lancé.")
    else:
        print("\n✅ Scan terminé.")
        print(f"Pairs détectées : {found}")
    return found

if __name__ == "__main__":
    scan_network(port=5001)
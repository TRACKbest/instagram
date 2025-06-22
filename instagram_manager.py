import os
import time
import json
from uuid import uuid4
import requests
import sys

# Dossiers et fichiers
BASE_DIR = os.path.join(os.path.dirname(__file__), "SmmKingdomTask")
ACCOUNTS_FILE = os.path.join(BASE_DIR, "insta-accounts.json")
HASHTAGS_FILE = os.path.join(BASE_DIR, "hashtags.txt")
ON_HOLD_FILE = os.path.join(BASE_DIR, "on_hold_accounts.txt")
SMMPY_ACCOUNTS = os.path.join(BASE_DIR, "insta-acct.txt")

# Limites Instagram
FOLLOW_LIMIT_PER_HOUR = 10
LIKE_LIMIT_PER_HOUR = 10
COMMENT_LIMIT_PER_HOUR = 10
MAX_HASHTAGS = 30

# Couleurs
V = '\033[1;92m'  # Vert
B = '\033[1;97m'  # Blanc
R = '\033[1;91m'  # Rouge
S = '\033[0m'     # Reset

# Initialisation des fichiers
os.makedirs(BASE_DIR, exist_ok=True)
if not os.path.exists(ACCOUNTS_FILE):
    with open(ACCOUNTS_FILE, 'w') as f:
        json.dump({}, f)
if not os.path.exists(HASHTAGS_FILE):
    with open(HASHTAGS_FILE, 'w') as f:
        f.write('')
if not os.path.exists(ON_HOLD_FILE):
    with open(ON_HOLD_FILE, 'w') as f:
        f.write('')

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def attempt_login_and_get_cookie(user, pwd):
    """Connexion à Instagram, retourne le cookie si succès, sinon None."""
    uid = str(uuid4())
    url = "https://i.instagram.com/api/v1/accounts/login/"
    header0 = {
        'User-Agent': 'Instagram 113.0.0.39.122 Android (24/5.0; 515dpi; 1440x2416; huawei/google; Nexus 6P; angler; angler; en_US)',
        "Accept": "*/*", "Accept-Encoding": "gzip, deflate", "Accept-Language": "en-US",
        "X-IG-Capabilities": "3brTvw==", "X-IG-Connection-Type": "WIFI",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        'Host': 'i.instagram.com', 'Connection': 'keep-alive'
    }
    data1 = {
        'uuid': uid, 'password': pwd, 'username': user, 'device_id': uid,
        'from_reg': 'false', '_csrftoken': 'YcJzPesTYxMTfmpSOiVn3pfRAJdrETFD',
        'login_attempt_countn': '0'
    }
    try:
        rq_session = requests.session()
        rq1 = rq_session.post(url=url, headers=header0, data=data1)
        rp1 = rq1.text
        if "ok" in rp1 and "logged_in_user" in rp1:
            cookies = str(rq1.cookies.get_dict())[1:-1].replace("'", '').replace(':', '=').replace(',', ';')
            return cookies
    except Exception as e:
        print(f"Erreur lors de la connexion : {e}")
        return None
    return None

def load_accounts():
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_accounts(accounts):
    with open(ACCOUNTS_FILE, 'w') as f:
        json.dump(accounts, f, indent=2)

def import_smm_py_accounts():
    if os.path.exists(SMMPY_ACCOUNTS):
        with open(SMMPY_ACCOUNTS, 'r') as f:
            lines = f.readlines()
        accounts = load_accounts()
        for line in lines:
            if '|' in line:
                user, cookie = line.strip().split('|', 1)
                if user not in accounts:
                    accounts[user] = {
                        'cookie': cookie,
                        'follow_count': 0,
                        'like_count': 0,
                        'comment_count': 0,
                        'last_action_hour': 0
                    }
        save_accounts(accounts)

def add_account():
    clear()
    print("Ajouter un compte Instagram :")
    print("1. Par identifiants (login/pass)")
    print("2. Par cookie Instagram")
    print("0. Retour menu")
    choice = input("Votre choix : ")
    if choice == '1':
        user = input("Nom d'utilisateur : ").strip()
        pwd = input("Mot de passe : ").strip()
        accounts = load_accounts()
        if user in accounts:
            print("Ce compte existe déjà.")
            time.sleep(1)
            return
        print("Connexion à Instagram en cours...")
        cookie = attempt_login_and_get_cookie(user, pwd)
        if cookie:
            accounts[user] = {
                'cookie': cookie,
                'follow_count': 0,
                'like_count': 0,
                'comment_count': 0,
                'last_action_hour': 0
            }
            save_accounts(accounts)
            print(f"{B}[{V}✔{B}] Compte ajouté et cookie récupéré.{S}")
            time.sleep(2)
        else:
            print(f"{B}[{R}✖{B}] Échec de la connexion. Identifiants invalides ou compte bloqué.{S}")
            time.sleep(2)
    elif choice == '2':
        user = input("Nom d'utilisateur : ").strip()
        cookie = input("Cookie Instagram : ").strip()
        accounts = load_accounts()
        if user in accounts:
            print("Ce compte existe déjà.")
            time.sleep(1)
            return
        accounts[user] = {
            'cookie': cookie,
            'follow_count': 0,
            'like_count': 0,
            'comment_count': 0,
            'last_action_hour': 0
        }
        save_accounts(accounts)
        print(f"{B}[{V}✔{B}] Compte ajouté.{S}")
        time.sleep(1)
    elif choice == '0':
        return
    else:
        print("Choix invalide.")
        time.sleep(1)

def list_accounts():
    clear()
    accounts = load_accounts()
    if not accounts:
        print("Aucun compte enregistré.")
    else:
        print("Liste des comptes :")
        for i, user in enumerate(accounts.keys(), 1):
            print(f"[{i}] {user}")
    input("\nAppuyez sur Entrée pour revenir au menu...")

def delete_account():
    clear()
    accounts = load_accounts()
    if not accounts:
        print("Aucun compte à supprimer.")
        time.sleep(1)
        return
    print("Comptes disponibles :")
    users = list(accounts.keys())
    for i, user in enumerate(users, 1):
        print(f"[{i}] {user}")
    print("[0] Retour menu")
    try:
        choice = int(input("Sélectionnez le numéro du compte à supprimer : "))
        if choice == 0:
            return
        if 1 <= choice <= len(users):
            del accounts[users[choice-1]]
            save_accounts(accounts)
            print(f"{B}[{V}✔{B}] Compte supprimé.{S}")
            time.sleep(1)
        else:
            print(f"{B}[{R}✖{B}] Choix invalide.{S}")
            time.sleep(1)
    except ValueError:
        print(f"{B}[{R}✖{B}] Entrée invalide.{S}")
        time.sleep(1)

def manage_hashtags():
    clear()
    print("Gestion des hashtags (max 30, séparés par espace ou retour à la ligne)")
    if os.path.exists(HASHTAGS_FILE):
        with open(HASHTAGS_FILE, 'r') as f:
            hashtags = [h.strip() for h in f.read().split() if h.strip()]
    else:
        hashtags = []
    print(f"Hashtags actuels ({len(hashtags)}) : {', '.join(hashtags)}")
    print("\n1. Modifier la liste\n0. Retour menu")
    choice = input("Votre choix : ")
    if choice == '1':
        new_tags = input("Entrez les hashtags séparés par espace : ").strip().split()
        if len(new_tags) > MAX_HASHTAGS:
            print(f"Vous ne pouvez pas dépasser {MAX_HASHTAGS} hashtags.")
            time.sleep(2)
            return
        with open(HASHTAGS_FILE, 'w') as f:
            f.write(' '.join(new_tags))
        print(f"{B}[{V}✔{B}] Hashtags mis à jour.{S}")
        time.sleep(1)
    elif choice == '0':
        return
    else:
        print("Choix invalide.")
        time.sleep(1)

def load_on_hold_accounts():
    if os.path.exists(ON_HOLD_FILE):
        with open(ON_HOLD_FILE, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    return []

def save_on_hold_accounts(accounts):
    with open(ON_HOLD_FILE, 'w') as f:
        for user in accounts:
            f.write(user + '\n')

def list_on_hold_accounts():
    clear()
    on_hold = load_on_hold_accounts()
    if not on_hold:
        print("Aucun compte en attente.")
    else:
        print("Comptes en attente (limite horaire atteinte) :")
        for i, user in enumerate(on_hold, 1):
            print(f"[{i}] {user}")
    input("\nAppuyez sur Entrée pour revenir au menu...")

def reactivate_account():
    clear()
    on_hold = load_on_hold_accounts()
    if not on_hold:
        print("Aucun compte à réactiver.")
        time.sleep(1)
        return
    print("Comptes en attente :")
    for i, user in enumerate(on_hold, 1):
        print(f"[{i}] {user}")
    print("[0] Retour menu")
    try:
        choice = int(input("Sélectionnez le numéro du compte à réactiver : "))
        if choice == 0:
            return
        if 1 <= choice <= len(on_hold):
            user = on_hold.pop(choice-1)
            save_on_hold_accounts(on_hold)
            # Remettre à zéro les compteurs horaires
            accounts = load_accounts()
            if user in accounts:
                accounts[user]['follow_count'] = 0
                accounts[user]['like_count'] = 0
                accounts[user]['comment_count'] = 0
                accounts[user]['last_action_hour'] = 0
                save_accounts(accounts)
            print(f"{B}[{V}✔{B}] Compte '{user}' réactivé.{S}")
            time.sleep(1)
        else:
            print(f"{B}[{R}✖{B}] Choix invalide.{S}")
            time.sleep(1)
    except ValueError:
        print(f"{B}[{R}✖{B}] Entrée invalide.{S}")
        time.sleep(1)

def start_bot():
    clear()
    print("--- Démarrage du bot (simulation) ---")
    accounts = load_accounts()
    if not accounts:
        print("Aucun compte disponible.")
        time.sleep(2)
        return
    if os.path.exists(HASHTAGS_FILE):
        with open(HASHTAGS_FILE, 'r') as f:
            hashtags = [h.strip() for h in f.read().split() if h.strip()]
    else:
        hashtags = []
    if not hashtags:
        print("Aucun hashtag défini. Veuillez en ajouter avant de démarrer le bot.")
        time.sleep(2)
        return
    print(f"{len(accounts)} comptes, {len(hashtags)} hashtags.")
    print("\n[Simulation] Le bot va :")
    print(f"- Liker, suivre, commenter entre les comptes (max {FOLLOW_LIMIT_PER_HOUR} follow/heure, {LIKE_LIMIT_PER_HOUR} like/heure, {COMMENT_LIMIT_PER_HOUR} comment/heure par compte)")
    print("- Utiliser les hashtags : " + ', '.join(hashtags))
    print("- Mettre en pause les comptes qui atteignent une limite horaire")
    print("\nAppuyez sur Entrée pour revenir au menu...")
    input()

def update_bot():
    clear()
    print("--- Mise à jour du Bot ---")
    url = "https://raw.githubusercontent.com/TRACKbest/instagram/main/instagram_manager.py"
    try:
        print("Téléchargement de la dernière version...")
        response = requests.get(url)
        response.raise_for_status()  # Lève une exception si le téléchargement échoue
        
        with open(__file__, 'w', encoding='utf-8') as f:
            f.write(response.text)
            
        print(f"{B}[{V}✔{B}] Mise à jour réussie ! Le script va redémarrer.{S}")
        time.sleep(2)
        # Redémarre le script
        os.execv(sys.executable, ['python'] + sys.argv)
    except requests.exceptions.RequestException as e:
        print(f"{B}[{R}✖{B}] Erreur lors du téléchargement de la mise à jour: {e}{S}")
        print("Veuillez réessayer plus tard ou mettre à jour manuellement.")
        time.sleep(3)
    except Exception as e:
        print(f"{B}[{R}✖{B}] Une erreur est survenue lors de la mise à jour: {e}{S}")
        time.sleep(3)

def menu():
    import_smm_py_accounts()
    while True:
        clear()
        print("""
╔══════════════════════════════════════════════╗
║         Instagram Manager - Bot Menu         ║
╚══════════════════════════════════════════════╝
[1] Ajouter un compte
[2] Lister les comptes
[3] Supprimer un compte
[4] Entrer/modifier les hashtags
[5] Lister les comptes en attente
[6] Réactiver un compte en attente
[7] Démarrer le bot
[8] Mettre à jour le bot
[0] Quitter
""")
        choice = input("Votre choix : ")
        if choice == '1':
            add_account()
        elif choice == '2':
            list_accounts()
        elif choice == '3':
            delete_account()
        elif choice == '4':
            manage_hashtags()
        elif choice == '5':
            list_on_hold_accounts()
        elif choice == '6':
            reactivate_account()
        elif choice == '7':
            start_bot()
        elif choice == '8':
            update_bot()
        elif choice == '0':
            print("Au revoir !")
            break
        else:
            print(f"{B}[{R}✖{B}] Choix invalide.{S}")
            time.sleep(1)

if __name__ == "__main__":
    menu() 

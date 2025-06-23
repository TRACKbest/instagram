import os
import time
import json
from uuid import uuid4
import requests
import sys
import random
import re
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
import platform
import importlib.util

# Dossiers et fichiers
BASE_DIR = os.path.join(os.path.dirname(__file__), "SmmKingdomTask")
ACCOUNTS_FILE = os.path.join(BASE_DIR, "insta-accounts.json")
HASHTAGS_FILE = os.path.join(BASE_DIR, "hashtags.txt")
ON_HOLD_FILE = os.path.join(BASE_DIR, "on_hold_accounts.txt")
SMMPY_ACCOUNTS = os.path.join(BASE_DIR, "insta-acct.txt")
SESSIONS_DIR = os.path.join(os.path.dirname(__file__), "sessions")
CREATED_ACCOUNTS_FILE = os.path.join(BASE_DIR, "created_accounts.txt")
CREATORS_FILE = os.path.join(BASE_DIR, "creators.txt")
USER_AGENT_MODE_FILE = os.path.join(os.path.dirname(__file__), 'user_agent_mode.txt')
USER_AGENT_MODES = ['custom', 'real']

# Limites Instagram
FOLLOW_LIMIT_PER_HOUR = 10
LIKE_LIMIT_PER_HOUR = 50
COMMENT_LIMIT_PER_HOUR = 10
MAX_HASHTAGS = 30

# Couleurs
V = '\033[1;92m'  # Vert
B = '\033[1;97m'  # Blanc
R = '\033[1;91m'  # Rouge
S = '\033[0m'     # Reset

# Initialisation des fichiers
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(SESSIONS_DIR, exist_ok=True)
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
        # Nettoyer le cookie avant de l'enregistrer
        cookie = ';'.join([c.strip() for c in cookie.split(';') if c.strip()])
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

def get_user_agent_mode():
    if os.path.exists(USER_AGENT_MODE_FILE):
        with open(USER_AGENT_MODE_FILE, 'r') as f:
            mode = f.read().strip()
            if mode in USER_AGENT_MODES:
                return mode
    return 'custom'

def set_user_agent_mode(mode):
    if mode in USER_AGENT_MODES:
        with open(USER_AGENT_MODE_FILE, 'w') as f:
            f.write(mode)

def user_agent():
    mode = get_user_agent_mode()
    if mode == 'real':
        # Charger la fonction get_random_user_agent depuis android/user_agents.py
        spec = importlib.util.spec_from_file_location('user_agents', os.path.join(os.path.dirname(__file__), 'android', 'user_agents.py'))
        user_agents = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(user_agents)
        return user_agents.get_random_user_agent()
    # Mode custom (par défaut)
    version = f"{random.randint(100, 200)}.0.0.{random.randint(10, 30)}.{random.randint(100, 200)}"
    android_version = f"{random.randint(7, 12)}"
    dpi = random.choice(['320', '480', '640'])
    width = random.choice(['1080', '1440'])
    height = random.choice(['1920', '2560'])
    manufacturer = random.choice(['samsung', 'huawei', 'google', 'oneplus', 'xiaomi'])
    model = random.choice(['SM-G991U', 'Pixel 6', 'Mate 40 Pro', 'OnePlus 9', 'Mi 11'])
    return f"Instagram {version} Android ({android_version}; {dpi}dpi; {width}x{height}; {manufacturer}; {model}; en_US)"

def _get_entity_id(session, url, cookie, entity_type):
    """Récupère un ID (user_id ou media_id) depuis une URL Instagram."""
    headers = {'user-agent': user_agent()}
    # Utiliser le cookie pour la session, si disponible
    cookies_dict = {}
    if cookie:
        # Simple parsing du cookie
        for item in cookie.split(';'):
            if '=' in item:
                key, value = item.split('=', 1)
                cookies_dict[key.strip()] = value.strip()
    try:
        response = session.get(url, headers=headers, cookies=cookies_dict, timeout=10)
        response.raise_for_status()
        
        pattern = f'"{entity_type}":"(.*?)"'
        match = re.search(pattern, response.text)
        
        if match:
            return match.group(1)
        print(f"{B}[{R}✖{B}] Impossible de trouver l'ID ({entity_type}) pour {url}{S}")
        return None
    except requests.RequestException as e:
        print(f"{B}[{R}✖{B}] Erreur réseau en récupérant l'ID de {url}: {e}{S}")
        return None

def _get_user_id(session, username, cookie):
    url = f"https://www.instagram.com/{username}/"
    return _get_entity_id(session, url, cookie, "user_id")

def _get_latest_post_id(session, username, cookie):
    """Récupère l'ID du post le plus récent d'un utilisateur."""
    profile_url = f"https://www.instagram.com/{username}/"
    headers = {'user-agent': user_agent()}
    cookies_dict = {}
    if cookie:
        for item in cookie.split(';'):
            if '=' in item:
                key, value = item.split('=', 1)
                cookies_dict[key.strip()] = value.strip()
    try:
        res = session.get(profile_url, headers=headers, cookies=cookies_dict, timeout=10)
        res.raise_for_status()
        
        # Regex pour trouver le code court du premier lien de post
        match = re.search(r'"shortcode":"([^"]+)"', res.text)
        if match:
            post_url = f"https://www.instagram.com/p/{match.group(1)}/"
            return _get_entity_id(session, post_url, cookie, "media_id")
        return None
    except Exception as e:
        print(f"{B}[{R}✖{B}] Erreur en récupérant le dernier post de {username}: {e}{S}")
        return None

def _perform_action(session, url, cookie, data=None):
    """Exécute une action (POST) sur l'API Instagram."""
    # Nettoyer le cookie pour enlever les espaces superflus
    cookie = ';'.join([c.strip() for c in cookie.split(';') if c.strip()])
    try:
        csrftoken = [item.split('=')[1].strip() for item in cookie.split(';') if 'csrftoken' in item][0]
    except IndexError:
        print(f"{B}[{R}✖{B}] Jeton CSRF introuvable dans le cookie.{S}")
        return None

    headers = {
        "x-ig-app-id": "936619743392459", # ID d'app web
        "x-instagram-ajax": "1008229312", # Varie mais peut être statique
        "x-csrftoken": csrftoken,
        "user-agent": user_agent(),
        "cookie": cookie
    }
    if data:
        headers["content-type"] = "application/x-www-form-urlencoded"

    try:
        response = session.post(url, headers=headers, data=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"{B}[{R}✖{B}] Erreur de requête vers {url}: {e}{S}")
        return None

def follow_user(session, target_username, cookie):
    user_id = _get_user_id(session, target_username, cookie)
    if not user_id: return False
    
    url = f"https://www.instagram.com/api/v1/friendships/create/{user_id}/"
    response = _perform_action(session, url, cookie)
    return response and response.get("status") == "ok"

def like_post(session, post_id, cookie):
    if not post_id: return False
    
    url = f"https://www.instagram.com/api/v1/media/{post_id}/like/"
    response = _perform_action(session, url, cookie)
    return response and response.get("status") == "ok"

def comment_on_post(session, post_id, cookie, text):
    if not post_id: return False
    
    url = f"https://www.instagram.com/api/v1/web/comments/{post_id}/add/"
    data = {'comment_text': text}
    response = _perform_action(session, url, cookie, data=data)
    return response and response.get("status") == "ok"

def start_bot():
    clear()
    print("--- Démarrage du bot ---")
    
    accounts = load_accounts()
    on_hold_users = load_on_hold_accounts()
    active_accounts = {u: d for u, d in accounts.items() if u not in on_hold_users}

    if len(active_accounts) < 2:
        print(f"{B}[{R}✖{B}] Vous avez besoin d'au moins 2 comptes actifs pour démarrer.{S}")
        time.sleep(3)
        return

    hashtags = [h for f in [HASHTAGS_FILE] if os.path.exists(f) for l in open(f) for h in l.split() if h.strip()]
    if not hashtags:
        print(f"{B}[{R}✖{B}] Aucun hashtag défini. Ajoutez-en via le menu.{S}")
        time.sleep(3)
        return
        
    print(f"{B}[{V}✔{B}] Bot démarré avec {len(active_accounts)} comptes. Appuyez sur CTRL+C pour arrêter.{S}")
    time.sleep(2)
    
    try:
        while True:
            all_accounts = load_accounts()
            on_hold_users = load_on_hold_accounts()
            active_users = [u for u in all_accounts if u not in on_hold_users]
            
            if len(active_users) < 2:
                print("Pas assez de comptes actifs. Le bot s'arrête.")
                break

            # Si tous les comptes sont en attente, on arrête le bot
            if len(active_users) == 0:
                print("Tous les comptes ont atteint leurs limites. Le bot s'arrête.")
                break

            random.shuffle(active_users)

            for username in active_users:
                account_data = all_accounts[username]
                cookie = account_data.get('cookie')
                if not cookie: continue
                
                current_hour = time.localtime().tm_hour
                if account_data.get('last_action_hour') != current_hour:
                    account_data.update({'follow_count': 0, 'like_count': 0, 'comment_count': 0, 'last_action_hour': current_hour})

                target_user = random.choice([u for u in active_users if u != username])
                session = requests.session()

                # Suivi
                if account_data['follow_count'] < FOLLOW_LIMIT_PER_HOUR:
                    print(f"[{username}] -> Tente de suivre [{target_user}]...")
                    if follow_user(session, target_user, cookie):
                        print(f"{B}[{V}✔{B}] Follow réussi: {username} -> {target_user}{S}")
                        account_data['follow_count'] += 1
                    else:
                        print(f"{B}[{R}✖{B}] Échec du follow: {username} -> {target_user}{S}")
                    time.sleep(random.randint(20, 40))
                else:
                    print(f"[{username}] a atteint la limite de follow/h.")

                # Like
                post_id = _get_latest_post_id(session, target_user, cookie)
                if post_id:
                    if account_data['like_count'] < LIKE_LIMIT_PER_HOUR:
                        print(f"[{username}] -> Tente de liker un post de [{target_user}]...")
                        if like_post(session, post_id, cookie):
                            print(f"{B}[{V}✔{B}] Like réussi: {username} -> post de {target_user}{S}")
                            account_data['like_count'] += 1
                        else:
                            print(f"{B}[{R}✖{B}] Échec du like: {username} -> post de {target_user}{S}")
                        time.sleep(random.randint(20, 40))
                    else:
                        print(f"[{username}] a atteint la limite de like/h.")

                    # Commentaire
                    if account_data['comment_count'] < COMMENT_LIMIT_PER_HOUR:
                        comment_text = random.choice(hashtags)
                        print(f"[{username}] -> Tente de commenter '{comment_text}'...")
                        if comment_on_post(session, post_id, cookie, comment_text):
                            print(f"{B}[{V}✔{B}] Commentaire réussi: {username} -> post de {target_user}{S}")
                            account_data['comment_count'] += 1
                        else:
                            print(f"{B}[{R}✖{B}] Échec du commentaire: {username} -> post de {target_user}{S}")
                        time.sleep(random.randint(20, 40))
                    else:
                        print(f"[{username}] a atteint la limite de commentaire/h.")

                # Si le compte a atteint les 3 limites, on le met en attente
                if (account_data['follow_count'] >= FOLLOW_LIMIT_PER_HOUR and
                    account_data['like_count'] >= LIKE_LIMIT_PER_HOUR and
                    account_data['comment_count'] >= COMMENT_LIMIT_PER_HOUR):
                    print(f"[{R}✖{B}] Limites horaires atteintes pour {username}. Mise en attente.{S}")
                    on_hold_users.append(username)
                    save_on_hold_accounts(list(set(on_hold_users)))

                save_accounts(all_accounts)
                print("--- Pause avant le prochain compte (60-120s) ---")
                time.sleep(random.randint(60, 120))

    except KeyboardInterrupt:
        print("\nArrêt du bot demandé par l'utilisateur.")
        return

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

def add_created_account(username, password):
    with open(CREATED_ACCOUNTS_FILE, "a") as f:
        f.write(f"{username}:{password}\n")

def add_creator(email_or_phone):
    creators = load_creators()
    if email_or_phone not in creators:
        creators[email_or_phone] = 0
        save_creators(creators)

def load_creators():
    creators = {}
    if os.path.exists(CREATORS_FILE):
        with open(CREATORS_FILE, "r") as f:
            for line in f:
                if ":" in line:
                    k, v = line.strip().split(":", 1)
                    creators[k] = int(v)
    return creators

def save_creators(creators):
    with open(CREATORS_FILE, "w") as f:
        for k, v in creators.items():
            f.write(f"{k}:{v}\n")

def show_created_accounts():
    clear()
    if os.path.exists(CREATED_ACCOUNTS_FILE):
        with open(CREATED_ACCOUNTS_FILE, "r") as f:
            lines = f.readlines()
        print("Comptes créés :")
        for line in lines:
            print(line.strip())
    else:
        print("Aucun compte créé.")
    input("\nAppuie sur Entrée pour revenir au menu...")

def show_creators():
    clear()
    creators = load_creators()
    print("Numéros/emails utilisés :")
    for k, v in creators.items():
        print(f"{k} : {v}/5 comptes")
    input("\nAppuie sur Entrée pour revenir au menu...")

def auto_create_accounts():
    import platform
    if platform.system().lower() == "linux" and "android" in platform.platform().lower():
        print("La création automatique de comptes Instagram n'est pas possible sur Termux/Android.")
        print("Crée les comptes manuellement, puis ajoute-les dans le bot via l'option 'Ajouter un compte'.")
        input("Appuie sur Entrée pour revenir au menu...")
        return
    import random
    import time
    clear()
    print("Création automatique de comptes Instagram (validation manuelle du code email/SMS)")
    email_or_phone = input("Email ou numéro à utiliser : ").strip()
    password = input("Mot de passe à utiliser : ").strip()
    nb = int(input("Combien de comptes veux-tu créer ? "))
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    SESSIONS_DIR = os.path.join(os.path.dirname(__file__), "sessions")
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    CREATED_ACCOUNTS_FILE = os.path.join(BASE_DIR, "created_accounts.txt")
    def generate_username():
        first_names = ["john", "james", "robert", "michael", "william", "david", "richard", "joseph", "thomas", "charles"]
        last_names = ["smith", "johnson", "williams", "brown", "jones", "miller", "davis", "garcia", "rodriguez", "wilson"]
        sep = random.choice(['.', '_'])
        username = f"{random.choice(first_names)}{sep}{random.choice(last_names)}{sep}{random.randint(100,9999)}"
        return username
    def generate_birthdate():
        current_year = time.localtime().tm_year
        age = random.randint(26, 79)
        year = current_year - age
        month = random.randint(1, 12)
        if month == 2:
            day = random.randint(1, 28)
        elif month in [4, 6, 9, 11]:
            day = random.randint(1, 30)
        else:
            day = random.randint(1, 31)
        return (day, month, year)
    def save_account(username, password, cookie_str):
        with open(CREATED_ACCOUNTS_FILE, "a") as f:
            f.write(f"{username}:{password}\n")
        with open(os.path.join(SESSIONS_DIR, f"{username}.session"), "w") as f:
            f.write(cookie_str)
    for i in range(nb):
        print(f"\n--- Création du compte {i+1} ---")
        driver = webdriver.Chrome()
        driver.get("https://www.instagram.com/accounts/emailsignup/")
        time.sleep(3)
        username = generate_username()
        full_name = username.replace('.', ' ').replace('_', ' ').title()
        day, month, year = generate_birthdate()
        # Remplir le formulaire
        driver.find_element(By.NAME, "emailOrPhone").send_keys(email_or_phone)
        driver.find_element(By.NAME, "fullName").send_keys(full_name)
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        # Vérifier que tous les champs sont bien remplis
        while True:
            fields = [
                driver.find_element(By.NAME, "emailOrPhone").get_attribute("value"),
                driver.find_element(By.NAME, "fullName").get_attribute("value"),
                driver.find_element(By.NAME, "username").get_attribute("value"),
                driver.find_element(By.NAME, "password").get_attribute("value"),
            ]
            if all(fields):
                break
            print("Tous les champs ne sont pas remplis, vérifie le formulaire.")
            time.sleep(2)
        # Cliquer sur Suivant
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(5)
        # Remplir la date de naissance
        try:
            # Instagram peut changer le selecteur, adapte si besoin
            month_select = driver.find_element(By.XPATH, "//select[@title='Mois :']")
            month_select.send_keys(str(month))
            day_select = driver.find_element(By.XPATH, "//select[@title='Jour :']")
            day_select.send_keys(str(day))
            year_select = driver.find_element(By.XPATH, "//select[@title='Année :']")
            year_select.send_keys(str(year))
            # Cliquer sur Suivant
            driver.find_element(By.XPATH, "//button[contains(text(),'Suivant')]").click()
            time.sleep(5)
        except Exception as e:
            print("Erreur lors de la saisie de la date de naissance :", e)
        print(f"Compte généré : {username} / {password}")
        print("Valide le captcha et la confirmation dans le navigateur, puis appuie sur Entrée ici pour enregistrer le compte.")
        input("Appuie sur Entrée quand le compte est validé et créé...")
        # Récupérer les cookies
        selenium_cookies = driver.get_cookies()
        cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in selenium_cookies])
        save_account(username, password, cookie_str)
        print(f"Compte enregistré dans {CREATED_ACCOUNTS_FILE} et session sauvegardée.")
        driver.quit()
        time.sleep(5)

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
[9] Créer des comptes Instagram automatiquement
[10] Voir la liste des comptes créés
[11] Voir les numéros/emails utilisés
[12] Changer le mode de User-Agent (actuel: {} )
[0] Quitter
""".format(get_user_agent_mode()))
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
        elif choice == '9':
            auto_create_accounts()
        elif choice == '10':
            show_created_accounts()
        elif choice == '11':
            show_creators()
        elif choice == '12':
            print("\nMode actuel : {}".format(get_user_agent_mode()))
            print("1. Mode custom (aléatoire, style Instagram)")
            print("2. Mode réel (user-agent Android réel)")
            sub = input("Choisir le mode (1 ou 2) : ")
            if sub == '1':
                set_user_agent_mode('custom')
                print("Mode user-agent défini sur custom.")
            elif sub == '2':
                set_user_agent_mode('real')
                print("Mode user-agent défini sur real.")
            else:
                print("Choix invalide.")
            time.sleep(1)
        elif choice == '0':
            print("Au revoir !")
            break
        else:
            print(f"{B}[{R}✖{B}] Choix invalide.{S}")
            time.sleep(1)

if __name__ == "__main__":
    menu() 

import os
import time
import json
from uuid import uuid4
import sys
import random
import re
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ClientError, ClientLoginRequired

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

def attempt_login_and_get_session(user, pwd):
    """Connexion à Instagram avec instagrapi, retourne le client si succès, sinon None."""
    try:
        client = Client()
        client.login(user, pwd)
        return client
    except Exception as e:
        print(f"Erreur lors de la connexion : {e}")
        return None

def login_with_cookie(user, cookie):
    """Connexion à Instagram avec un cookie existant."""
    try:
        client = Client()
        # Convertir le cookie string en dict
        cookies_dict = {}
        for item in cookie.split(';'):
            if '=' in item:
                key, value = item.split('=', 1)
                cookies_dict[key.strip()] = value.strip()
        
        # Définir les cookies
        client.set_cookies(cookies_dict)
        
        # Vérifier si la session est valide
        client.get_timeline_feed()
        return client
    except Exception as e:
        print(f"Erreur lors de la connexion avec cookie : {e}")
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
        client = attempt_login_and_get_session(user, pwd)
        if client:
            # Récupérer les cookies de session
            cookies = client.get_settings()
            cookie_string = '; '.join([f"{k}={v}" for k, v in client.get_cookies().items()])
            
            accounts[user] = {
                'cookie': cookie_string,
                'follow_count': 0,
                'like_count': 0,
                'comment_count': 0,
                'last_action_hour': 0
            }
            save_accounts(accounts)
            print(f"{B}[{V}✔{B}] Compte ajouté et session récupérée.{S}")
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
        
        # Tester la validité du cookie
        print("Test de la connexion avec le cookie...")
        client = login_with_cookie(user, cookie)
        if client:
            accounts[user] = {
                'cookie': cookie,
                'follow_count': 0,
                'like_count': 0,
                'comment_count': 0,
                'last_action_hour': 0
            }
            save_accounts(accounts)
            print(f"{B}[{V}✔{B}] Compte ajouté avec cookie valide.{S}")
            time.sleep(1)
        else:
            print(f"{B}[{R}✖{B}] Cookie invalide ou expiré.{S}")
            time.sleep(2)
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

def get_client_for_user(username, cookie):
    """Crée un client instagrapi pour un utilisateur avec son cookie."""
    try:
        client = Client()
        # Convertir le cookie string en dict
        cookies_dict = {}
        for item in cookie.split(';'):
            if '=' in item:
                key, value = item.split('=', 1)
                cookies_dict[key.strip()] = value.strip()
        
        client.set_cookies(cookies_dict)
        return client
    except Exception as e:
        print(f"Erreur lors de la création du client pour {username}: {e}")
        return None

def follow_user(client, target_username):
    """Suivre un utilisateur avec instagrapi."""
    try:
        user_id = client.user_id_by_username(target_username)
        client.user_follow(user_id)
        return True
    except Exception as e:
        print(f"Erreur lors du follow: {e}")
        return False

def like_post(client, post_id):
    """Liker un post avec instagrapi."""
    try:
        client.media_like(post_id)
        return True
    except Exception as e:
        print(f"Erreur lors du like: {e}")
        return False

def comment_on_post(client, post_id, text):
    """Commenter un post avec instagrapi."""
    try:
        client.media_comment(post_id, text)
        return True
    except Exception as e:
        print(f"Erreur lors du commentaire: {e}")
        return False

def get_latest_post_id(client, username):
    """Récupère l'ID du post le plus récent d'un utilisateur."""
    try:
        user_id = client.user_id_by_username(username)
        user_feed = client.user_medias(user_id, 1)  # Récupère le dernier post
        if user_feed:
            return user_feed[0].id
        return None
    except Exception as e:
        print(f"Erreur en récupérant le dernier post de {username}: {e}")
        return None

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
                print("Pas assez de comptes actifs. Le bot se met en pause (60s).")
                time.sleep(60)
                continue

            random.shuffle(active_users)

            for username in active_users:
                account_data = all_accounts[username]
                cookie = account_data.get('cookie')
                if not cookie: continue
                
                current_hour = time.localtime().tm_hour
                if account_data.get('last_action_hour') != current_hour:
                    account_data.update({'follow_count': 0, 'like_count': 0, 'comment_count': 0, 'last_action_hour': current_hour})

                target_user = random.choice([u for u in active_users if u != username])
                client = get_client_for_user(username, cookie)
                
                if not client:
                    print(f"Impossible de créer le client pour {username}")
                    continue
                
                if account_data['follow_count'] < FOLLOW_LIMIT_PER_HOUR:
                    print(f"[{username}] -> Tente de suivre [{target_user}]...")
                    if follow_user(client, target_user):
                        print(f"{B}[{V}✔{B}] Follow réussi: {username} -> {target_user}{S}")
                        account_data['follow_count'] += 1
                    else:
                        print(f"{B}[{R}✖{B}] Échec du follow: {username} -> {target_user}{S}")
                    time.sleep(random.randint(5, 10))
                
                post_id = get_latest_post_id(client, target_user)
                if post_id:
                    if account_data['like_count'] < LIKE_LIMIT_PER_HOUR:
                        print(f"[{username}] -> Tente de liker un post de [{target_user}]...")
                        if like_post(client, post_id):
                             print(f"{B}[{V}✔{B}] Like réussi: {username} -> post de {target_user}{S}")
                             account_data['like_count'] += 1
                        else:
                            print(f"{B}[{R}✖{B}] Échec du like: {username} -> post de {target_user}{S}")
                        time.sleep(random.randint(5, 10))
                        
                    if account_data['comment_count'] < COMMENT_LIMIT_PER_HOUR:
                        comment_text = random.choice(hashtags)
                        print(f"[{username}] -> Tente de commenter '{comment_text}'...")
                        if comment_on_post(client, post_id, comment_text):
                            print(f"{B}[{V}✔{B}] Commentaire réussi: {username} -> post de {target_user}{S}")
                            account_data['comment_count'] += 1
                        else:
                             print(f"{B}[{R}✖{B}] Échec du commentaire: {username} -> post de {target_user}{S}")
                        time.sleep(random.randint(10, 15))
                
                if all(account_data[k] >= l for k, l in [('follow_count', FOLLOW_LIMIT_PER_HOUR), ('like_count', LIKE_LIMIT_PER_HOUR), ('comment_count', COMMENT_LIMIT_PER_HOUR)]):
                    print(f"[{R}✖{B}] Limites horaires atteintes pour {username}. Mise en attente.{S}")
                    on_hold_users.append(username)
                    save_on_hold_accounts(list(set(on_hold_users)))

                save_accounts(all_accounts)
                print("--- Pause avant le prochain compte (30-60s) ---")
                time.sleep(random.randint(30, 60))

    except KeyboardInterrupt:
        print("\nArrêt du bot demandé par l'utilisateur.")
        return

def update_bot():
    clear()
    print("--- Mise à jour du Bot ---")
    url = "https://raw.githubusercontent.com/TRACKbest/instagram/main/instagram_manager.py"
    try:
        print("Téléchargement de la dernière version...")
        import requests
        response = requests.get(url)
        response.raise_for_status()  # Lève une exception si le téléchargement échoue
        
        with open(__file__, 'w', encoding='utf-8') as f:
            f.write(response.text)
            
        print(f"{B}[{V}✔{B}] Mise à jour réussie ! Le script va redémarrer.{S}")
        time.sleep(2)
        # Redémarre le script
        os.execv(sys.executable, ['python'] + sys.argv)
    except ImportError:
        print(f"{B}[{R}✖{B}] Module requests non disponible pour la mise à jour.{S}")
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

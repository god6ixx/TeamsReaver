import os
import sys
import json
import base64
import requests
import argparse
import datetime
import html
import re
import urllib3
from colorama import init, Fore, Style

init(autoreset=True)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def load_config():
    config = {
        "CLIENT_ID": "",
        "CLIENT_SECRET": "",
        "TENANT_ID": "",
        "DEFAULT_DOMAIN": ""
    }
    
    config_path = os.path.join(os.path.dirname(__file__), ".reaverconf")
    
    if not os.path.exists(config_path):
        print(f"{Fore.YELLOW}[!] Arquivo de configuracao (.reaverconf) nao encontrado.")
        print(f"{Fore.WHITE}[*] Iniciando configuracao inicial interativa...")
        try:
            config["CLIENT_ID"] = input(f"{Fore.CYAN}    -> Digite o CLIENT_ID: ").strip()
            config["CLIENT_SECRET"] = input(f"{Fore.CYAN}    -> Digite o CLIENT_SECRET: ").strip()
            config["TENANT_ID"] = input(f"{Fore.CYAN}    -> Digite o TENANT_ID: ").strip()
            config["DEFAULT_DOMAIN"] = input(f"{Fore.CYAN}    -> Digite o DEFAULT_DOMAIN (ex: @empresa.com.br): ").strip()
            
            with open(config_path, "w") as f:
                for k, v in config.items():
                    f.write(f"{k} = \"{v}\"\n")
            print(f"{Fore.GREEN}[+] Arquivo .reaverconf criado com sucesso!\n")
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}[!] Configuracao cancelada pelo usuario.")
            sys.exit(1)
    else:
        with open(config_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key in config:
                        config[key] = value
    return config

CONFIG = load_config()
CLIENT_ID = CONFIG["CLIENT_ID"]
CLIENT_SECRET = CONFIG["CLIENT_SECRET"]
TENANT_ID = CONFIG["TENANT_ID"]
DEFAULT_DOMAIN = CONFIG["DEFAULT_DOMAIN"]

def show_banner():
    lines = [
        r"""▄▄▄█████▓▓█████ ▄▄▄       ███▄ ▄███▓  ██████     ██▀███  ▓█████ ▄▄▄    ██▒   █▓▓█████  ██▀███  """,
        r"""▓  ██▒ ▓▒▓█   ▀▒████▄    ▓██▒▀█▀ ██▒▒██    ▒    ▓██ ▒ ██▒▓█   ▀▒████▄ ▓██░   █▒▓█   ▀ ▓██ ▒ ██▒""",
        r"""▒ ▓██░ ▒░▒███  ▒██  ▀█▄  ▓██    ▓██░░ ▓██▄      ▓██ ░▄█ ▒▒███  ▒██  ▀█▄▓██  █▒░▒███   ▓██ ░▄█ ▒""",
        r"""░ ▓██▓ ░ ▒▓█  ▄░██▄▄▄▄██ ▒██    ▒██   ▒   ██▒   ▒██▀▀█▄  ▒▓█  ▄░██▄▄▄▄██▒██ █░░▒▓█  ▄ ▒██▀▀█▄  """,
        r"""  ▒██▒ ░ ░▒████▒▓█   ▓██▒▒██▒   ░██▒▒██████▒▒   ░██▓ ▒██▒░▒████▒▓█   ▓██▒▒▀█░  ░▒████▒░██▓ ▒██▒""",
        r"""  ▒ ░░   ░░ ▒░ ░▒▒   ▓▒█░░ ▒░   ░  ░▒ ▒▓▒ ▒ ░   ░ ▒▓ ░▒▓░░░ ▒░ ░▒▒   ▓▒█░░ ▐░  ░░ ▒░ ░░ ▒▓ ░▒▓░""",
        r"""    ░     ░ ░  ░ ▒   ▒▒ ░░  ░      ░░ ░▒  ░ ░     ░▒ ░ ▒░ ░ ░  ░ ▒   ▒▒ ░░ ░░   ░ ░  ░  ░▒ ░ ▒░""",
        r"""  ░         ░    ░   ▒   ░      ░   ░  ░  ░       ░░   ░    ░    ░   ▒     ░░     ░     ░░   ░ """,
        r"""            ░  ░     ░  ░       ░         ░        ░        ░  ░     ░  ░   ░     ░  ░   ░     """,
        r"""                                                                           ░                    """
    ]
    
    print("-" * 108)
    for i, line in enumerate(lines):
        r = 120 + (i * 25)
        if r > 255: r = 255
        color_code = f"\033[38;2;{r};0;0m"
        print(f"{color_code}{line}\033[0m")
    
    print(f"{Fore.RED}             >> Teams Forensic Investigation & Data Export Tool <<")
    print(f"{Fore.RED}                                  by god6ixx")
    print("-" * 108)

def get_token():
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = {
        'client_id': CLIENT_ID,
        'scope': 'https://graph.microsoft.com/.default',
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json().get('access_token')

def get_user(upn, headers):
    if upn and "@" not in upn:
        upn += DEFAULT_DOMAIN
    url = f"https://graph.microsoft.com/v1.0/users/{upn}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def clean_filename(filename):
    return re.sub(r'[^a-zA-Z0-9.-]', '_', filename)

def clean_folder_name(name):
    return re.sub(r'[^a-zA-Z0-9]', '_', name)

def main():
    parser = argparse.ArgumentParser(description="TeamsReaver", add_help=False)
    parser.add_argument("-TargetUPN", help="Target user email")
    parser.add_argument("-SearchTerms", help="Search terms")
    parser.add_argument("-TargetTwo", help="Target second user email")
    parser.add_argument("-Fast", type=int, default=0, help="Fast search")
    parser.add_argument("-Date", help="Specific date")
    parser.add_argument("-Help", "-h", action="store_true", help="Show help")

    args = parser.parse_args()

    if args.Help or (not args.TargetUPN and not args.TargetTwo):
        show_banner()
        print(f"""
{Fore.WHITE}DESCRICAO:
    Ferramenta para busca forense e exportacao de chats do Microsoft Teams via Graph API.

USO:
    python TeamsReaver.py -TargetUPN <user> [Opcoes]

PARAMETROS:
    -TargetUPN      E-mail do alvo.
    -SearchTerms    Lista de termos para busca (ex: 'senha','secretkey').
    -TargetTwo      Extrai TODA a conversa entre o TargetUPN e este segundo usuario.
    -Date           Data especifica (dd/MM/yyyy) para filtrar ocorrencias.
    -Fast           Busca nos ultimos X dias (ex: -Fast 7).
    -Help           Exibe este menu de ajuda.

EXEMPLOS:
    python TeamsReaver.py -TargetUPN usuario -SearchTerms "apikey","secretkey" -Date "29/04/2026"
    python TeamsReaver.py -TargetUPN usuario -TargetTwo outro_usuario
""")
        return

    show_banner()

    search_terms = []
    if args.SearchTerms:
        raw_terms = args.SearchTerms.replace('"', '').replace("'", "")
        search_terms = [t.strip().lower() for t in raw_terms.split(',')]

    start_date = None
    if args.Date:
        try:
            start_date = datetime.datetime.strptime(args.Date, "%d/%m/%Y").date()
            print(f"{Fore.YELLOW}[*] Filtro por data: dia {start_date.strftime('%d/%m/%Y')}")
        except ValueError:
            return
    elif args.Fast > 0:
        start_date = (datetime.datetime.now() - datetime.timedelta(days=args.Fast)).date()

    try:
        if not CLIENT_ID or not CLIENT_SECRET or not TENANT_ID:
            print(f"{Fore.RED}[!] Erro de configuracao detectado.")
            print(f"{Fore.YELLOW}[*] Por favor, verifique o arquivo .reaverconf e consulte a documentacao (README.md).")
            return

        token = get_token()
        headers = {'Authorization': f'Bearer {token}'}
    except Exception:
        print(f"{Fore.RED}[!] Erro de configuracao ou autenticacao detectado.")
        print(f"{Fore.YELLOW}[*] Verifique suas credenciais no .reaverconf e consulte o README.md.")
        return

    try:
        user1 = get_user(args.TargetUPN, headers)
        user_id = user1['id']
        print(f"{Fore.GREEN}[*] Alvo 1: {user1.get('displayName')}")
        
        user_two_id = None
        if args.TargetTwo:
            user2 = get_user(args.TargetTwo, headers)
            user_two_id = user2['id']
            print(f"{Fore.GREEN}[*] Alvo 2: {user2.get('displayName')}")
    except Exception:
        print(f"{Fore.RED}[!] Usuario nao encontrado.")
        return

    base_export = f"Matches_Export_{clean_folder_name(args.TargetUPN)}"
    if not os.path.exists(base_export):
        os.makedirs(base_export)

    print(f"{Fore.WHITE}[*] Mapeando conversas...", end="", flush=True)
    all_chats = []
    chat_url = f"https://graph.microsoft.com/v1.0/users/{user_id}/chats?$top=50"
    
    while chat_url:
        try:
            response = requests.get(chat_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            all_chats.extend(data.get('value', []))
            chat_url = data.get('@odata.nextLink')
            print(".", end="", flush=True)
        except Exception:
            chat_url = None
    
    print(f" {Fore.GREEN}Concluido! ({len(all_chats)} chats)")

    for chat in all_chats:
        chat_id = chat['id']
        match_found = False
        
        if user_two_id:
            try:
                members_url = f"https://graph.microsoft.com/v1.0/chats/{chat_id}/members"
                members_resp = requests.get(members_url, headers=headers)
                members_resp.raise_for_status()
                member_ids = [m.get('userId') for m in members_resp.json().get('value', [])]
                if user_two_id in member_ids:
                    match_found = True
            except Exception:
                pass

        chat_messages_text = []
        raw_messages = []
        msg_url = f"https://graph.microsoft.com/v1.0/chats/{chat_id}/messages?$top=50"
        
        while msg_url:
            try:
                msg_resp = requests.get(msg_url, headers=headers)
                msg_resp.raise_for_status()
                msg_data = msg_resp.json()
                
                for msg in msg_data.get('value', []):
                    raw_messages.append(msg)
                    created_dt = datetime.datetime.fromisoformat(msg['createdDateTime'].replace('Z', '+00:00'))
                    msg_date = created_dt.date()
                    
                    sender = msg.get('from', {}).get('user', {}).get('displayName', "System/Bot")
                    content_html = msg.get('body', {}).get('content', "")
                    content = html.unescape(re.sub('<[^>]+>', '', content_html))
                    
                    att_info = ""
                    attachments = msg.get('attachments', [])
                    if attachments:
                        for att in attachments:
                            att_info += f" [ARQUIVO: {att.get('name')}]"
                    
                    chat_messages_text.append(f"[{msg['createdDateTime']}] {sender}:{att_info} {content}")

                    if not args.TargetTwo:
                        is_date = (msg_date == start_date) if start_date else True
                        is_term = False
                        if search_terms:
                            for t in search_terms:
                                if t in content.lower():
                                    is_term = True
                                    break
                        else:
                            is_term = True
                        
                        if is_date and is_term and content.strip():
                            match_found = True
                            print(f"{Fore.CYAN}[!] MATCH em Chat: {chat_id}")
                
                msg_url = msg_data.get('@odata.nextLink')
            except Exception:
                msg_url = None

        if match_found:
            topic = chat.get('topic')
            if not topic:
                try:
                    members_url = f"https://graph.microsoft.com/v1.0/chats/{chat_id}/members"
                    members_resp = requests.get(members_url, headers=headers)
                    members_resp.raise_for_status()
                    member_names = [m.get('displayName') for m in members_resp.json().get('value', []) if m.get('userId') != user_id]
                    if not member_names:
                        member_names = [m.get('displayName') for m in members_resp.json().get('value', [])]
                    topic = ", ".join(member_names)
                except Exception:
                    topic = f"Chat_{chat.get('chatType')}"

            if not topic:
                topic = f"Chat_{chat.get('chatType')}"
            
            clean_topic = clean_folder_name(topic)[:60]
            short_id = chat_id[-8:]
            folder_name = f"{clean_topic}_{short_id}"
            
            chat_folder = os.path.join(base_export, folder_name)
            if not os.path.exists(chat_folder):
                os.makedirs(chat_folder)
            
            safe_topic_filename = clean_folder_name(topic)[:50]
            if not safe_topic_filename: safe_topic_filename = "Chat_Content"
            
            txt_file_path = os.path.join(chat_folder, f"{safe_topic_filename}.txt")
            with open(txt_file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(chat_messages_text))
            
            for m in raw_messages:
                for att in m.get('attachments', []):
                    content_url = att.get('contentUrl')
                    if content_url:
                        files_folder = os.path.join(chat_folder, "Files")
                        if not os.path.exists(files_folder):
                            os.makedirs(files_folder)
                        
                        try:
                            print(f"    {Fore.YELLOW}[+] Baixando: {att.get('name')}")
                            url_bytes = content_url.encode('utf-8')
                            sharing_id = "u!" + base64.urlsafe_b64encode(url_bytes).decode('utf-8').rstrip('=')
                            download_url = f"https://graph.microsoft.com/v1.0/shares/{sharing_id}/driveItem/content"
                            
                            safe_file_name = clean_filename(att.get('name'))[:100]
                            dest = os.path.join(files_folder, safe_file_name)
                            
                            current_url = download_url
                            while True:
                                dl_resp = requests.get(current_url, headers=headers, stream=True, allow_redirects=False, verify=False)
                                if dl_resp.status_code in [301, 302, 303, 307, 308]:
                                    current_url = dl_resp.headers['Location']
                                    continue
                                break
                            
                            dl_resp.raise_for_status()
                            with open(dest, 'wb') as df:
                                for chunk in dl_resp.iter_content(chunk_size=8192):
                                    df.write(chunk)
                        except Exception as e:
                            print(f"    {Fore.RED}[!] Falha no download de {att.get('name')}.")

            print(f"    {Fore.GREEN}[+] Conversa salva: {folder_name}")
            if args.TargetTwo and chat.get('chatType') in ['oneOnOne', 'personal']:
                sys.exit(0)

    print(f"\n{Fore.GREEN}[!] FIM.")

if __name__ == "__main__":
    main()

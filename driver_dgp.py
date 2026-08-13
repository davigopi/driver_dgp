# flake8: noqa
# pyright: # type: ignore
import os
import sys
import time
import psutil
import json
import shutil
import subprocess
import winreg
import zipfile
import requests
import urllib.request
import mss
import pygetwindow as gw
import signal
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.service import Service as FirefoxService


separador = "_________________________________________________________________________________________________________________________________________________________________"

list_navegador = ['chrome', 'edge', 'firefox', 'brave']

list_sites = [
    "https://www.google.com",
    "https://www.speedtest.net/pt",
    "https://www.youtube.com",
    "https://www.facebook.com",
    "https://www.instagram.com",
    "https://www.linkedin.com",
    "https://www.github.com",
    "https://www.microsoft.com",
    "https://www.python.org",
    "https://stackoverflow.com",
    "https://www.reddit.com",
    "https://www.wikipedia.org",
    "https://www.amazon.com.br",
    "https://www.mercadolivre.com.br",
    "https://www.globo.com",
    "https://www.uol.com.br",
    "https://www.tecmundo.com.br",
    "https://www.baixaki.com.br",
]

dict_url_download_google = {
    'base': "https://storage.googleapis.com/chrome-for-testing-public/",
    'driver_zip': "/win64/chromedriver-win64.zip",
    'chrome_zip': "/win64/chrome-win64.zip"
}

dict_url_download_firefox = {
    "base": "https://github.com/mozilla/geckodriver/releases/download/",
    "geckodriver": "/geckodriver-",
    'driver_zip': "-win64.zip"
}
gecko_url = "https://api.github.com/repos/mozilla/geckodriver/releases/latest"
path_driver_zip = "driver.zip"
path_chrome_zip = "chrome.zip"
extract_path = "driver"

if_not_exist_version_chrome = "142.0.7444.122"

path_brave = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
brave_port = "9222"

# ============================================================
# Baixa o ZIP
# ============================================================
def download_driver_zip(version, navegador='chrome'):
    if navegador == 'firefox':
        resp = requests.get(gecko_url)
        resp.raise_for_status()
        version = resp.json()["tag_name"]
        url = dict_url_download_firefox["base"] + version + dict_url_download_firefox["geckodriver"] + version + dict_url_download_firefox["driver_zip"]
    else:
        url = dict_url_download_google['base'] + version + dict_url_download_google['driver_zip']
    urllib.request.urlretrieve(url, path_driver_zip)

# ============================================================
# Limpa pasta driver
# ============================================================
def clean_path_driver():
    if os.path.exists(extract_path):
        shutil.rmtree(extract_path, ignore_errors=True)
    os.makedirs(extract_path, exist_ok=True)

# ============================================================
# Fechar navagadores
# ============================================================
def close_driver(driver=None, navegador=None, historico=False):
    try:
        if driver:
            driver.quit()
            print(f'\n⚓ Fechar driver ✅', end=' | ', flush=True)
            return True
        elif navegador and historico:
            user_home = os.path.expanduser("~")
            user_data_dir = os.path.normpath(
                os.path.join(user_home, "AppData", f"historico_{navegador}")
            )
            text_pid = ''
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    navegador_exe = navegador+'.exe'
                    if proc.info['name'] and proc.info['name'].lower() == navegador_exe.lower():
                        cmd = proc.info['cmdline']
                        if cmd and any(f'--user-data-dir={user_data_dir}' in arg for arg in cmd):
                            text_pid += f'{proc.pid}, '
                            proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            if text_pid:
                print(f'\n⚓ Fechar navegador {navegador} PID {text_pid}', end=' | ', flush=True)
                return True
        elif navegador:
            navegador = navegador.lower()
            if 'edge' in navegador:
                list_navegador_exe = ["msedgedriver.exe", "msedge.exe"]
            elif 'firefox' in navegador:
                list_navegador_exe = ["firefox.exe"]
            elif 'brave' in navegador:
                list_navegador_exe = ["brave.exe"]
            else:
                list_navegador_exe = ["chromedriver.exe", "chrome.exe"]
        else:
            list_navegador_exe = ["chromedriver.exe", "chrome.exe", "msedgedriver.exe", "msedge.exe"]
        for navegador_exe in list_navegador_exe:
            subprocess.run(['taskkill', '/f', '/im', navegador_exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f'\n⚓ Fechar navegador {navegador_exe} ✅', end=' | ', flush=True)
        return True
    except Exception as e:
        print(f'\n⚓ Fechar driver ou navegador. Exception: {e} ⛔', end=' | ', flush=True)
        return False

# ============================================================
# Localizar monitor pelo seu número ou pela resolução
# ============================================================
def get_monitor(num=None, width=None, height=None):
    if not num and not width and not height:
        print(f'è preciso informa a numeração(num=) ou largura(width=) e altura(height=) da tela')
        return False
    with mss.mss() as sct:
        monitores = sct.monitors[1:]  # Ignora sct.monitors[0] (área unificada)
        if not monitores:
            return sct.monitors[0]
        # 1. Tenta selecionar pela numeração (Ex: num=1 pega o primeiro monitor individual)
        if num is not None and isinstance(num, int):
            index = num - 1  # Ajusta para base 0
            if 0 <= index < len(monitores):
                return monitores[index]
        # 2. Se 'num' não foi passado ou for inválido, busca pela resolução
        for monitor in monitores:
            if monitor["width"] == width and monitor["height"] == height:
                return monitor
        # 3. Fallback: pega o 2º monitor se existir, senão o 1º
        if len(monitores) > 1:
            return monitores[1]
        return monitores[0]

class Driver_Auto_Dgp:
    def __init__(self):
        self.driver = None
        self.path_driver = ''
        self.version = ''

    # ============================================================
    #   UTILIDADES
    # ============================================================
    def delete_chrome_folders(self):
        folders = [
            r'C:\Program Files\Google\Chrome',
            r'C:\Program Files (x86)\Google\Chrome',
            os.path.expanduser(r'~\AppData\Local\Google\Chrome'),
            os.path.expanduser(r'~\AppData\Local\Google\Chromium'),
        ]
        for p in folders:
            if os.path.exists(p):
                shutil.rmtree(p, ignore_errors=True)

    # def set_zoom(self, driver, percentage):
    #     driver.execute_script(f"document.body.style.zoom='{percentage}%'")
    def set_zoom(self, driver, percentage):
        # Funciona para Chrome, Edge, Brave e Firefox moderno via CSS transform
        driver.execute_script(f"document.body.style.transform='scale({percentage / 100})'; document.body.style.transformOrigin='0 0';")


    def set_background_dark(self, driver, dark_mode=True):
        if dark_mode:
            # Fundo preto, texto branco
            driver.execute_script("document.body.style.backgroundColor = 'black';")
            driver.execute_script("document.body.style.color = 'white';")
        else:
            # Restaura para o padrão (ou limpa os estilos diretos)
            driver.execute_script("document.body.style.backgroundColor = '';")
            driver.execute_script("document.body.style.color = '';")

    def refresh_driver(self, driver):
        if driver:
            print('⚓  Atualizando o driver ✅', end=' ', flush=True)
            driver.refresh()
        else:
            print('⚓  Atualizando o driver ⛔', end=' ', flush=True)

    def open_brave_debug(self, user_data_dir):
        comando = [
            path_brave,
            f"--remote-debugging-port={brave_port}",
            f"--user-data-dir={user_data_dir}",
            "--profile-directory=Default"
        ]
        subprocess.Popen(
            comando,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    # ============================================================
    #   INSTALAÇÃO DOS NAVEGADORES FOR TESTING (SILENCIOSA)
    # ============================================================
    def install_new_navegadores(self, navegador, e):
        if navegador in ['edge', 'firefox', 'brave']:
            print(f'❌ Não instalado. Precisar instalar o navegador {navegador} manualmente. A Exceção: {e}')
            sys.exit()
        self.version = if_not_exist_version_chrome
        print(f'❌ Não instalado. Nova versão {self.version} instalando...', end=' ')
        url = dict_url_download_google['base'] + self.version + dict_url_download_google['chrome_zip']
        urllib.request.urlretrieve(url, path_chrome_zip)
        install_path = r'C:\Program Files\Google\Chrome\Application'
        os.makedirs(install_path, exist_ok=True)
        with zipfile.ZipFile(path_chrome_zip, 'r') as zip_ref:
            zip_ref.extractall(install_path)
        # mover arquivos
        src = os.path.join(install_path, 'chrome-win64')
        for file in os.listdir(src):
            # shutil.move(os.path.join(src, file), os.path.join(install_path, file))
            for root, _, files in os.walk(extract_path):
                if 'chromedriver.exe' in files:
                    self.path_driver = os.path.join(root, 'chromedriver.exe')
                    break
        # shutil.rmtree(src)
        time.sleep(0.5)
        shutil.rmtree(src, ignore_errors=True)
        os.remove(path_chrome_zip)
        print('instalado', end=' ')

    # ============================================================
    #   LÊ A VERSÃO DO DRIVER INSTALADO
    # ============================================================
    def get_version(self, navegador, path=r'Software\Google\Chrome\BLBeacon'):
        try:
            if navegador == 'firefox':
                path = r"C:\Program Files\Mozilla Firefox\firefox.exe"
                out = subprocess.check_output([path, "--version"], text=True)
                partes = out.strip().split()
                if partes:
                    self.version = partes[-1]
                else:
                    self.version = "Desconhecida (saída vazia)"
            elif navegador == 'edge':
                self.version = "Selenium Manager"
            elif navegador == 'brave':
                path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
                out = subprocess.check_output([path, "--version"], text=True)
                partes = out.strip().split()
                if partes:
                    self.version = partes[-1]   # ex: 151.1.93.134
                else:
                    self.version = "Desconhecida"
            else:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path)
                chrome_version, _ = winreg.QueryValueEx(key, "version")
                build = ".".join(chrome_version.split(".")[:3])
                url = "https://googlechromelabs.github.io/chrome-for-testing/latest-patch-versions-per-build.json"
                with urllib.request.urlopen(url) as response:
                    dados = json.load(response)
                self.version = dados["builds"][build]["version"]
                print(f"Chrome instalado : {chrome_version}", end=' | ')
                print(f"ChromeDriver usado: {self.version}", end=' | ')
        except Exception as e :
            self.install_new_navegadores(navegador, e)

    # ============================================================
    #   INSTALA O DRIVER COMPATÍVEL
    # ============================================================
    def install_driver(self, navegador):
        if navegador in ['edge', 'brave']:
            self.path_driver = None
            return
        print(f'instalando...', end=' ')
        download_driver_zip(self.version, navegador)
        for i in range(2):
            clean_path_driver()
            try:
                with zipfile.ZipFile(path_driver_zip, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                print('extraido...', end=' ')
                break
            except PermissionError:
                if i == 0:
                    print('❌ PermissionError: liberar...', end=' ')
                else:
                    print('❌ BLOQUEADO. Feche tudo e tente novamente.')
                    sys.exit()
                close_driver(navegador=navegador)
        os.remove(path_driver_zip)
        if navegador == 'firefox':
            self.path_driver = os.path.join(extract_path,'geckodriver.exe')
        else:
            self.path_driver = os.path.join(extract_path, 'chromedriver-win64', 'chromedriver.exe')

        if not os.path.isfile(self.path_driver):
            raise FileNotFoundError(self.path_driver)

    # ============================================================
    #   CRIA O DRIVER SEM ERROS (E COM PERSISTÊNCIA COMPLETA)
    # ============================================================
    def create_driver(self, navegador):
        print(f'Versão: {self.version}, abrindo {navegador}...', end=' ')
        if navegador != 'brave':
            self.install_driver(navegador)
        if navegador == 'firefox':
            options = webdriver.FirefoxOptions()
            options.set_preference("dom.webnotifications.enabled", False)
            options.set_preference("signon.rememberSignons", True)
            # service = FirefoxService(self.path_driver,log_output=os.devnull)
            service = FirefoxService(self.path_driver)
            return webdriver.Firefox(service=service, options=options)

        user_home = os.path.expanduser("~")
        user_data_dir = os.path.normpath(
            os.path.join(user_home, "AppData", f"historico_{navegador}")
        )
        os.makedirs(user_data_dir, exist_ok=True)
        if navegador == 'edge':
            options = webdriver.EdgeOptions()
            options.use_chromium = True
        else:
            options = webdriver.ChromeOptions()

        # 1. Perfil Persistente (Aponta para a pasta e força o uso do perfil Default)
        options.add_argument(f"--user-data-dir={user_data_dir}")
        options.add_argument("--profile-directory=Default")

        # 2. Configurações para forçar o salvamento de senhas via Prefs (Evita crash)
        prefs = {
            "credentials_enable_service": True,
            "profile.password_manager_enabled": True
        }
        options.add_experimental_option("prefs", prefs)

        # 3. Mascarar automação de forma segura para evitar o crash
        options.add_argument("--disable-blink-features=AutomationControlled")

        # 🔇 Silenciar logs do Chrome e otimizações
        options.add_argument('--log-level=3')                               # só erros críticos
        options.add_argument('--disable-logging')                           # Desabilita logs internos
        options.add_argument('--disable-dev-shm-usage')                     # Evita usar a memória compartilhada
        options.add_argument('--disable-notifications')                     # Bloqueia notificações de sites

        if navegador == 'brave':
            self.open_brave_debug(user_data_dir)
            options = webdriver.ChromeOptions()
            options.debugger_address = f"127.0.0.1:{brave_port}"
            return webdriver.Chrome(options=options)
        elif navegador == 'edge':
            return webdriver.Edge(options=options)

        service = ChromeService(self.path_driver, log_path=os.devnull)
        return webdriver.Chrome(service=service, options=options)

    # ============================================================
    #   ABRIR O DRIVER E RETONA-LO
    # ============================================================
    def open_site(self, info):
        if "site" not in info:
            print('Não foi informado a chave site dentro da biblioteca info')
            return False
        if 'navegador' not in info or info['navegador'] not in list_navegador:
            info['navegador'] = 'chrome'
        info['navegador'] = info['navegador'].lower()

        os.system('cls')
        num=1
        target_monitor = get_monitor(num=num)
        pos_x = target_monitor["left"]
        pos_y = target_monitor["top"]

        print(f"{separador}\n⚓ Driver Auto ({info['navegador']}) Site: ({info['site'][8:33]}) "
              f"Monit número: ({num}). X: {pos_x} Y: {pos_y} ✅ ",
              end=' ', flush=True)

        close_driver(navegador=info['navegador'], historico=True)
        if info['navegador'] == 'brave':
            self.get_version(info['navegador'], r'Software\BraveSoftware\Brave-Browser\BLBeacon')
        elif info['navegador'] == 'edge':
            self.get_version(info['navegador'], r'Software\Microsoft\Edge\BLBeacon')
        elif info['navegador'] == 'firefox':
            self.get_version(info['navegador'], '')
        else:
            self.get_version(info['navegador'], r'Software\Google\Chrome\BLBeacon')
        driver = self.create_driver(info['navegador'])


        driver.set_window_position(pos_x, pos_y)
        driver.get(info["site"])
        driver.maximize_window()
        print('✔️')
        return driver


class Driver_Manual_Dgp:
    def open_site(self, info):
        if "site" not in info:
            print('Não foi informado a chave site dentro da biblioteca info')
            return False
        if 'navegador' not in info:
            info['navegador'] = 'chrome'
        info['navegador'] = info['navegador'].lower()

        os.system('cls')
        width=1360
        height=768
        target_monitor = get_monitor(width=width, height=height)
        # Posiciona no canto do monitor alvo
        pos_x = target_monitor["left"]
        pos_y = target_monitor["top"]
        print(f"{separador}\n⚓ Driver Manual ({info['navegador']}) Site: ({info['site'][8:33]}) "
              f"Monit largura: ({width}) altura: ({height}). X: {pos_x} Y: {pos_y} ✅ ",
              end=' ', flush=True)
        user_home = os.path.expanduser("~")
        user_data_dir = os.path.normpath(
            os.path.join(user_home, "AppData", f"historico_{info['navegador']}")
        )
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)
        list_path_navegador_exe = {
            'firefox': r"C:\Program Files\Mozilla Firefox\firefox.exe",
            'edge': r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            'brave': r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            'chrome': r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        }
        titulos_navegador = {
            'chrome': ["chrome", "google"],
            'edge': ["edge", "microsoft edge"],
            'firefox': ["firefox", "mozilla"],
            'brave': ["brave"]
        }
        navegador_path = list_path_navegador_exe.get(info["navegador"], list_path_navegador_exe["chrome"])

        if not os.path.isfile(navegador_path):
            print(f"A pasta/executável {navegador_path} não foi encontrado.")
            return False

        if info['navegador'] == 'firefox':
            args = [navegador_path, info['site']]
        else:
            args = [
                navegador_path,
                # "--remote-debugging-port=9222",
                f"--user-data-dir={user_data_dir}",
                f"--window-position={pos_x},{pos_y}",
                "--no-first-run",
                "--no-default-browser-check",
                "--new-window",
                info["site"],
            ]
        subprocess.Popen(args)

        alvos = titulos_navegador.get(info['navegador'], [info['navegador']])
        time.sleep(1.5)
        for window in gw.getAllWindows():
            title_lower = window.title.lower()
            if any(alvo in title_lower for alvo in alvos):
                try:
                    window.moveTo(pos_x, pos_y)
                    time.sleep(0.2)
                    window.maximize()
                except Exception as e:
                    print(f"Erro ao posicionar janela: {e}")
                break

# ============================================================
#   EXEMPLO DE USO
# ============================================================

if __name__ == '__main__':
    driver_manual_dgp = Driver_Manual_Dgp()
    driver_auto_dgp = Driver_Auto_Dgp()
    print(f'\nAbrir Driver Manual')
    for n, navegador in enumerate(list_navegador):
        info = {"site": random.choice(list_sites),'navegador': navegador}
        time.sleep(1)
        print(f'Driver Manual {n+1}/{len(list_navegador)} -> {navegador}\n')
        driver_manual_dgp.open_site(info)
        time.sleep(3)
        if navegador == 'firefox':  # o firefox não tem o argumentos de historico --user-data-dir=
            close_driver(navegador=navegador)
        else:
            close_driver(navegador=navegador, historico=True)
    print(f'Fechado Driver Manual')

    print(f'\nAbrir Driver Automático')
    for n, navegador in enumerate(list_navegador):
        info = {"site": random.choice(list_sites),'navegador': navegador}
        time.sleep(1)
        print(f'Driver Automático {n+1}/{len(list_navegador)} -> {navegador}\n')
        driver = driver_auto_dgp.open_site(info)
        time.sleep(3)
        if navegador == 'brave':  # o brave não consegue fechar o driver pelo selenium
            close_driver(navegador=navegador)
        else:
            close_driver(driver=driver)
    print(f'Fechado Driver Automático')

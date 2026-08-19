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
# import signal
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.service import Service as FirefoxService


separador = 80*"="

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
    "https://www.baixaki.com.br"
]

dict_path_navegation_exe = {
    'chrome': r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    'edge': r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    'firefox': r"C:\Program Files\Mozilla Firefox\firefox.exe",
    'brave': r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
}
dict_titulos_navegation = {
    'chrome': ["chrome", "google"],
    'edge': ["edge", "microsoft edge"],
    'firefox': ["firefox", "mozilla"],
    'brave': ["brave"]
}
dict_navegation_exe = {
    'chrome': ["chromedriver.exe", "chrome.exe"],
    'edge': ["msedgedriver.exe", "msedge.exe"],
    'firefox': ["firefox.exe", 'geckodriver.exe'],
    'brave': ["brave.exe"]
}
dict_registro_navegation = {
    'chrome': r'Software\Google\Chrome\BLBeacon',
    'edge': r'Software\Microsoft\Edge\BLBeacon',
    'firefox': '',
    'brave': r'Software\BraveSoftware\Brave-Browser\BLBeacon'
}
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

brave_port = "9222"

last_vers_chrome = "https://googlechromelabs.github.io/chrome-for-testing/latest-patch-versions-per-build.json"

user_home = os.path.expanduser("~")
user_data_dir = os.path.join(user_home, "AppData", "historico_navegation_dgp")
user_data_path = os.path.normpath(user_data_dir)


# ============================================================
# Baixa o ZIP
# ============================================================
def download_driver_zip(version, navegation='chrome'):
    if navegation == 'firefox':
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
def close_driver(driver=None, navegation=None, historico=False):
    try:
        list_navegation_exe = []
        if navegation:
            navegation = navegation.lower()
            navegation_exe = navegation+'.exe'
        if driver:
            driver.quit()
            print(f'\n⚓ Fechar driver ✅', end=' | ', flush=True)
            return True
        elif navegation and historico and navegation in dict_navegation_exe:
            text_pid = ''
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and proc.info['name'].lower() == navegation_exe:
                        cmd = proc.info['cmdline']
                        if cmd:
                            cmd_line_str = " ".join(cmd).lower().replace('/', '\\')
                            if user_data_path in cmd_line_str:
                                text_pid += f'{proc.pid}, '
                                try:
                                    parent = psutil.Process(proc.pid)
                                    children = parent.children(recursive=True)
                                    for child in children:
                                        try:
                                            child.terminate()
                                        except psutil.NoSuchProcess:
                                            pass
                                    parent.terminate()
                                    gone, alive = psutil.wait_procs(children + [parent], timeout=2)
                                    for p in alive:
                                        try:
                                            p.kill()
                                        except psutil.NoSuchProcess:
                                            pass
                                except psutil.NoSuchProcess:
                                    pass
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            if text_pid:
                print(f'\n⚓ Fechar navegation {navegation} PID {text_pid}', end=' | ', flush=True)
                return True
        elif navegation and navegation in dict_navegation_exe:
            list_navegation_exe = dict_navegation_exe[navegation]
        else:
            for value in dict_navegation_exe.values():
                list_navegation_exe.extend(value)
        for navegation_exe in list_navegation_exe:
            subprocess.run(['taskkill', '/f', '/im', navegation_exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f'\n⚓ Fechar navegation {navegation_exe} ✅', end=' | ', flush=True)
        return True
    except Exception as e:
        print(f'\n⚓ Fechar driver ou navegation. Exception: {e} ⛔', end=' | ', flush=True)
        return False

# ============================================================
# Localizar monitor pelo seu número ou pela resolução
# ============================================================
def get_monitor(num=None, width=None, height=None):
    if num is None and width is None and height is None:
        raise Exception(f'É preciso informa a numeração(num=) ou largura(width=) e altura(height=) da tela')
    target_monitor = None
    with mss.mss() as sct:
        monitores = sct.monitors[1:]  # Ignora sct.monitors[0] (área unificada)
        if not monitores:
            target_monitor = sct.monitors[0]
        elif num is not None and isinstance(num, int):  # Selecionar pela numeração
            index = num - 1  # Ajusta para base 0
            if 0 <= index < len(monitores):
                target_monitor =  monitores[index]
        if not target_monitor:  # Não enviado ou inválido, busca pela resolução
            for monitor in monitores:
                if monitor["width"] == width and monitor["height"] == height:
                    target_monitor = monitor
                    break
        if not target_monitor:
            if len(monitores) > 1:  # 2º monitor se existir, senão o 1º
                target_monitor = monitores[1]
            else:
                target_monitor = monitores[0]
    info['x'] = target_monitor["left"]
    info['y'] = target_monitor["top"]
    return info['x'], info['y']


# ============================================================
# Validar as informações recebidas no dicionário info
# ============================================================
def validation_info(info):
    if "site" not in info:
        raise Exception("Não foi informado a chave site dentro da biblioteca info")
    if 'navegation' not in info or info['navegation'].lower() not in ['chrome', 'edge', 'firefox', 'brave']:
        info['navegation'] = 'chrome'
    info['navegation'] = info['navegation'].lower()
    if 'num' in info and info['num']:
        info['x'], info['y'] = get_monitor(num=info['num'])
        num_monitor = info['num']
    elif 'width' in info and 'height' in info and info['width'] and info['height']:
        info['x'], info['y'] = get_monitor(width=info['width'], height=info['height'])
        num_monitor = f"{info['width']}x{info['height']}"
    else:
        info['x'], info['y'] = get_monitor(num=1)
        num_monitor = 1

    os.system('cls')
    print(f"{separador}\n⚓ Driver Auto ({info['navegation']}) Site: ({info['site'][8:33]}) "
            f"Monit número: ({num_monitor}). X: {info['x']} Y: {info['y']} ✅ ",
            end=' ', flush=True)
    return info


class Driver_Auto_Dgp:
    def __init__(self):
        self.driver = None
        self.path_driver = ''
        self.versions = {}

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

    def set_zoom(self, driver, percentage):
        driver.execute_script(f"document.body.style.transform='scale({percentage / 100})'; document.body.style.transformOrigin='0 0';")

    def set_background_dark(self, driver, dark_mode=True):
        if dark_mode:
            driver.execute_script("document.body.style.backgroundColor = 'black';")
            driver.execute_script("document.body.style.color = 'white';")
        else:
            driver.execute_script("document.body.style.backgroundColor = '';")
            driver.execute_script("document.body.style.color = '';")

    def refresh_driver(self, driver):
        if driver:
            print('⚓  Atualizando o driver ✅', end=' ', flush=True)
            driver.refresh()
        else:
            print('⚓  Atualizando o driver ⛔', end=' ', flush=True)

    def open_brave_debug(self):
        comando = [
            dict_path_navegation_exe['brave'],
            f"--remote-debugging-port={brave_port}",
            f"--user-data-dir={user_data_path}",
            "--profile-directory=Default"
        ]
        subprocess.Popen(
            comando,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    # ============================================================
    #   INSTALAÇÃO DOS navegationES FOR TESTING (SILENCIOSA)
    # ============================================================
    def install_new_navegationes(self, navegation, e):
        if navegation in ['edge', 'firefox', 'brave']:
            print(f'❌ Não instalado. Precisar instalar o navegation {navegation} manualmente. A Exceção: {e}')
            sys.exit()
        self.version = if_not_exist_version_chrome
        print(f'❌ Não instalado. Nova versão {self.version} instalando...', end=' ')
        url = dict_url_download_google['base'] + self.version + dict_url_download_google['chrome_zip']
        urllib.request.urlretrieve(url, path_chrome_zip)
        install_path = r'C:\Program Files\Google\Chrome\Application'
        os.makedirs(install_path, exist_ok=True)
        with zipfile.ZipFile(path_chrome_zip, 'r') as zip_ref:
            zip_ref.extractall(install_path)
        src = os.path.join(install_path, 'chrome-win64')
        if os.path.exists(src):
            for item in os.listdir(src):
                s = os.path.join(src, item)
                d = os.path.join(install_path, item)
                if os.path.exists(d):
                    if os.path.isdir(d):
                        shutil.rmtree(d, ignore_errors=True)
                    else:
                        os.remove(d)
                shutil.move(s, d)
            shutil.rmtree(src, ignore_errors=True)
        print('instalado', end=' ')

    # ============================================================
    #   LÊ A VERSÃO DO DRIVER INSTALADO
    # ============================================================
    def get_version(self, navegation, path=dict_registro_navegation['chrome']):
        if navegation in self.versions:
            return self.versions[navegation]
        try:
            if navegation == 'firefox':
                path = dict_path_navegation_exe[navegation]
                out = subprocess.check_output([path, "--version"], text=True)
                partes = out.strip().split()
                ver = partes[-1] if partes else "Desconhecida"
            elif navegation == 'edge':
                ver = "Selenium Manager"
            elif navegation == 'brave':
                path = dict_path_navegation_exe[navegation]
                out = subprocess.check_output([path, "--version"], text=True)
                partes = out.strip().split()
                ver = partes[-1] if partes else "Desconhecida"
            else:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path)
                chrome_version, _ = winreg.QueryValueEx(key, "version")
                build = ".".join(chrome_version.split(".")[:3])
                url = last_vers_chrome
                with urllib.request.urlopen(url) as response:
                    dados = json.load(response)
                ver = dados["builds"][build]["version"]
                print(f"Chrome instalado : {chrome_version} | ChromeDriver usado: {ver}", end=' | ')
            self.versions[navegation] = ver
            self.version = ver
            return ver
        except Exception as e :
            self.install_new_navegationes(navegation, e)

    # ============================================================
    #   INSTALA O DRIVER COMPATÍVEL
    # ============================================================
    def install_driver(self, navegation):
        if navegation in ['edge', 'brave']:
            self.path_driver = None
            return
        if navegation == 'firefox':
            expected_path = os.path.join(extract_path,'geckodriver.exe')
        else:
            expected_path = os.path.join(extract_path, 'chromedriver-win64', 'chromedriver.exe')
        if os.path.isfile(expected_path):  # DRIVER JÁ EXISTIR
            self.path_driver = expected_path
            return
        print(f'instalando...', end=' ')
        download_driver_zip(self.version, navegation)
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
                close_driver(navegation=navegation)
        if os.path.exists(path_driver_zip):
            os.remove(path_driver_zip)
        self.path_driver = expected_path
        if not os.path.isfile(self.path_driver):
            raise FileNotFoundError(self.path_driver)

    # ============================================================
    #   CRIA O DRIVER SEM ERROS (E COM PERSISTÊNCIA COMPLETA)
    # ============================================================
    def create_driver(self, navegation):
        print(f'Versão: {self.version}, abrindo {navegation}...', end=' ')
        if navegation == 'brave':
            self.open_brave_debug()
            options = webdriver.ChromeOptions()
            options.add_experimental_option("debuggerAddress", f"127.0.0.1:{brave_port}")
            return webdriver.Chrome(options=options)
        if navegation == 'firefox':
            options = webdriver.FirefoxOptions()
            options.set_preference("dom.webnotifications.enabled", False)
            options.set_preference("signon.rememberSignons", True)
            service = FirefoxService(self.path_driver)
            return webdriver.Firefox(service=service, options=options)
        self.install_driver(navegation)
        os.makedirs(user_data_path, exist_ok=True)
        if navegation == 'edge':
            options = webdriver.EdgeOptions()
        else:
           options = webdriver.ChromeOptions()
        options.add_argument(f"--user-data-dir={user_data_path}")            # Define a pasta para salvar/carregar dados do perfil (cookies, logins, etc.)
        options.add_argument("--profile-directory=Default")                  # Força o uso do perfil "Default" dentro do diretório de dados
        options.add_argument('--no-sandbox')                                 # Desativa o modo sandbox (útil para executar como root ou em containers/servidores)
        options.add_argument('--log-level=3')                                # Filtra os logs do navegation para exibir apenas erros críticos (FATAL)
        options.add_argument('--disable-logging')                            # Desabilita a gravação e exibição de logs internos do Chromium/Chrome
        options.add_argument('--disable-dev-shm-usage')                      # Evita crashes ao usar a memória do sistema (/tmp) em vez da memória compartilhada (/dev/shm)
        options.add_argument('--disable-gpu')                                # Desativa a aceleração por hardware via GPU (evita falhas de renderização em alguns sistemas)
        options.add_argument('--disable-notifications')                      # Bloqueia pop-ups e solicitações de permissão para notificações de sites
        prefs = {
            "credentials_enable_service": True,
            "profile.password_manager_enabled": True
        }                                                                   # Força o salvamento de senhas via Prefs
        options.add_experimental_option("prefs", prefs)
        if navegation == 'edge':
            return webdriver.Edge(options=options)
        service = ChromeService(self.path_driver, log_path=os.devnull)
        return webdriver.Chrome(service=service, options=options)

    # ============================================================
    #   ABRIR O DRIVER E RETONA-LO
    # ============================================================
    def open_site(self, info):
        info = validation_info(info)
        close_driver(navegation=info['navegation'], historico=True)
        self.get_version(info['navegation'], dict_registro_navegation[info['navegation']])
        driver = self.create_driver(info['navegation'])
        driver.set_window_position(info['x'], info['y'])
        driver.get(info["site"])
        driver.maximize_window()
        print('✔️')
        return driver


class Driver_Manual_Dgp:
    def open_site(self, info):
        info = validation_info(info)
        if not os.path.exists(user_data_path):
            os.makedirs(user_data_path)
        navegation_path = dict_path_navegation_exe.get(info['navegation'], dict_path_navegation_exe["chrome"])
        if not os.path.isfile(navegation_path):
            print(f"A pasta/executável {navegation_path} não foi encontrado.")
            return False
        if info['navegation'] == 'firefox':
            args = [
                navegation_path,
                "-profile", user_data_path,
                "-new-window",
                info['site']
            ]
        else:
            args = [
                navegation_path,
                # "--remote-debugging-port=9222",
                f"--user-data-dir={user_data_path}",
                f"--window-position={info['x']},{info['y']}",
                "--no-first-run",
                "--no-default-browser-check",
                "--new-window",
                info["site"],
            ]
        subprocess.Popen(args)
        alvos = dict_titulos_navegation.get(info['navegation'], [info['navegation']])
        time.sleep(1.5)
        for window in gw.getAllWindows():
            title_lower = window.title.lower()
            if any(alvo in title_lower for alvo in alvos):
                try:
                    window.moveTo(info['x'], info['y'])
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
    for n, navegation in enumerate(dict_path_navegation_exe):
        info = {"site": random.choice(list_sites),'navegation': navegation, 'width':1360, 'height':768, 'num':None}
        time.sleep(1)
        print(f'Driver Manual {n+1}/{len(dict_path_navegation_exe)} -> {navegation}\n')
        driver_manual_dgp.open_site(info)
        time.sleep(3)
        close_driver(navegation=navegation)
        # close_driver(navegation=navegation, historico=True)
    print(f'Fechado Driver Manual')

    print(f'\nAbrir Driver Automático')
    for n, navegation in enumerate(dict_path_navegation_exe):
        info = {"site": random.choice(list_sites),'navegation': navegation}
        time.sleep(1)
        print(f'Driver Automático {n+1}/{len(dict_path_navegation_exe)} -> {navegation}\n')
        driver = driver_auto_dgp.open_site(info)
        time.sleep(3)
        if navegation == 'brave':
            close_driver(navegation=navegation)
        else:
            close_driver(driver=driver)
    print(f'Fechado Driver Automático')

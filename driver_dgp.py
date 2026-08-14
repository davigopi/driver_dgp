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

dict_path_navegador_exe = {
    'chrome': r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    'edge': r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    'firefox': r"C:\Program Files\Mozilla Firefox\firefox.exe",
    'brave': r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
}
dict_titulos_navegador = {
    'chrome': ["chrome", "google"],
    'edge': ["edge", "microsoft edge"],
    'firefox': ["firefox", "mozilla"],
    'brave': ["brave"]
}
dict_navegador_exe = {
    'chrome': ["chromedriver.exe", "chrome.exe"],
    'edge': ["msedgedriver.exe", "msedge.exe"],
    'firefox': ["firefox.exe", 'geckodriver.exe'],
    'brave': ["brave.exe"]
}
dict_registro_navegador = {
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
user_data_dir = os.path.join(user_home, "AppData", "historico_navegador_dgp")
user_data_path = os.path.normpath(user_data_dir)


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
        list_navegador_exe = []
        if navegador:
            navegador = navegador.lower()
            navegador_exe = navegador+'.exe'
        if driver:
            driver.quit()
            print(f'\n⚓ Fechar driver ✅', end=' | ', flush=True)
            return True
        elif navegador and historico and navegador in dict_navegador_exe:
            text_pid = ''
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and proc.info['name'].lower() == navegador_exe:
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
                print(f'\n⚓ Fechar navegador {navegador} PID {text_pid}', end=' | ', flush=True)
                return True
        elif navegador and navegador in dict_navegador_exe:
            list_navegador_exe = dict_navegador_exe[navegador]
        else:
            for value in dict_navegador_exe.values():
                list_navegador_exe.extend(value)
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
    if num is None and width is None and height is None:
        print(f'è preciso informa a numeração(num=) ou largura(width=) e altura(height=) da tela')
        sys.exit(1)
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
    pos_x = target_monitor["left"]
    pos_y = target_monitor["top"]
    return pos_x, pos_y

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
            dict_path_navegador_exe['brave'],
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
    def get_version(self, navegador, path=dict_registro_navegador['chrome']):
        if navegador in self.versions:
            return self.versions[navegador]
        try:
            if navegador == 'firefox':
                path = dict_path_navegador_exe[navegador]
                out = subprocess.check_output([path, "--version"], text=True)
                partes = out.strip().split()
                ver = partes[-1] if partes else "Desconhecida"
            elif navegador == 'edge':
                ver = "Selenium Manager"
            elif navegador == 'brave':
                path = dict_path_navegador_exe[navegador]
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
            self.versions[navegador] = ver
            self.version = ver
            return ver
        except Exception as e :
            self.install_new_navegadores(navegador, e)

    # ============================================================
    #   INSTALA O DRIVER COMPATÍVEL
    # ============================================================
    def install_driver(self, navegador):
        if navegador in ['edge', 'brave']:
            self.path_driver = None
            return
        if navegador == 'firefox':
            expected_path = os.path.join(extract_path,'geckodriver.exe')
        else:
            expected_path = os.path.join(extract_path, 'chromedriver-win64', 'chromedriver.exe')
        if os.path.isfile(expected_path):  # DRIVER JÁ EXISTIR
            self.path_driver = expected_path
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
        if os.path.exists(path_driver_zip):
            os.remove(path_driver_zip)
        self.path_driver = expected_path
        if not os.path.isfile(self.path_driver):
            raise FileNotFoundError(self.path_driver)

    # ============================================================
    #   CRIA O DRIVER SEM ERROS (E COM PERSISTÊNCIA COMPLETA)
    # ============================================================
    def create_driver(self, navegador):
        print(f'Versão: {self.version}, abrindo {navegador}...', end=' ')
        if navegador == 'brave':
            self.open_brave_debug()
            options = webdriver.ChromeOptions()
            options.add_experimental_option("debuggerAddress", f"127.0.0.1:{brave_port}")
            return webdriver.Chrome(options=options)
        if navegador == 'firefox':
            options = webdriver.FirefoxOptions()
            options.set_preference("dom.webnotifications.enabled", False)
            options.set_preference("signon.rememberSignons", True)
            service = FirefoxService(self.path_driver)
            return webdriver.Firefox(service=service, options=options)
        self.install_driver(navegador)
        os.makedirs(user_data_path, exist_ok=True)
        if navegador == 'edge':
            options = webdriver.EdgeOptions()
        else:
           options = webdriver.ChromeOptions()
        options.add_argument(f"--user-data-dir={user_data_path}")            # Define a pasta para salvar/carregar dados do perfil (cookies, logins, etc.)
        options.add_argument("--profile-directory=Default")                  # Força o uso do perfil "Default" dentro do diretório de dados
        options.add_argument('--no-sandbox')                                 # Desativa o modo sandbox (útil para executar como root ou em containers/servidores)
        options.add_argument('--log-level=3')                                # Filtra os logs do navegador para exibir apenas erros críticos (FATAL)
        options.add_argument('--disable-logging')                            # Desabilita a gravação e exibição de logs internos do Chromium/Chrome
        options.add_argument('--disable-dev-shm-usage')                      # Evita crashes ao usar a memória do sistema (/tmp) em vez da memória compartilhada (/dev/shm)
        options.add_argument('--disable-gpu')                                # Desativa a aceleração por hardware via GPU (evita falhas de renderização em alguns sistemas)
        options.add_argument('--disable-notifications')                      # Bloqueia pop-ups e solicitações de permissão para notificações de sites
        prefs = {
            "credentials_enable_service": True,
            "profile.password_manager_enabled": True
        }                                                                   # Força o salvamento de senhas via Prefs
        options.add_experimental_option("prefs", prefs)
        if navegador == 'edge':
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
        if 'navegador' not in info:
            info['navegador'] = 'chrome'
        if 'num' not in info and'width' not in info and 'height' not in info:
            info['num'] = 1
        if info['num'] is None:
            pos_x, pos_y  = get_monitor(width=info['width'], height=info['height'])
        else:
            pos_x, pos_y  = get_monitor(num=info['num'])
        info['navegador'] = info['navegador'].lower()
        os.system('cls')
        print(f"{separador}\n⚓ Driver Auto ({info['navegador']}) Site: ({info['site'][8:33]}) "
              f"Monit número: ({info['num']}). X: {pos_x} Y: {pos_y} ✅ ",
              end=' ', flush=True)
        close_driver(navegador=info['navegador'], historico=True)
        self.get_version(info['navegador'], dict_registro_navegador[info['navegador']])
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
        if 'num' not in info and'width' not in info and 'height' not in info:
            info['num'] = 1
        if info['num'] is None:
            pos_x, pos_y  = get_monitor(width=info['width'], height=info['height'])
        else:
            pos_x, pos_y  = get_monitor(num=info['num'])
        info['navegador'] = info['navegador'].lower()
        os.system('cls')
        print(f"{separador}\n⚓ Driver Manual ({info['navegador']}) Site: ({info['site'][8:33]}) "
              f"Monit largura: ({info['width']}) altura: ({info['height']}). X: {pos_x} Y: {pos_y} ✅ ",
              end=' ', flush=True)
        if not os.path.exists(user_data_path):
            os.makedirs(user_data_path)
        navegador_path = dict_path_navegador_exe.get(info["navegador"], dict_path_navegador_exe["chrome"])
        if not os.path.isfile(navegador_path):
            print(f"A pasta/executável {navegador_path} não foi encontrado.")
            return False
        if info['navegador'] == 'firefox':
            args = [
                navegador_path,
                "-profile", user_data_path,
                "-new-window",
                info['site']
            ]
        else:
            args = [
                navegador_path,
                # "--remote-debugging-port=9222",
                f"--user-data-dir={user_data_path}",
                f"--window-position={pos_x},{pos_y}",
                "--no-first-run",
                "--no-default-browser-check",
                "--new-window",
                info["site"],
            ]
        subprocess.Popen(args)
        alvos = dict_titulos_navegador.get(info['navegador'], [info['navegador']])
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
    for n, navegador in enumerate(dict_path_navegador_exe):
        info = {"site": random.choice(list_sites),'navegador': navegador, 'width':1360, 'height':768, 'num':None}
        time.sleep(1)
        print(f'Driver Manual {n+1}/{len(dict_path_navegador_exe)} -> {navegador}\n')
        driver_manual_dgp.open_site(info)
        time.sleep(3)
        close_driver(navegador=navegador)
        # close_driver(navegador=navegador, historico=True)
    print(f'Fechado Driver Manual')

    print(f'\nAbrir Driver Automático')
    for n, navegador in enumerate(dict_path_navegador_exe):
        info = {"site": random.choice(list_sites),'navegador': navegador}
        time.sleep(1)
        print(f'Driver Automático {n+1}/{len(dict_path_navegador_exe)} -> {navegador}\n')
        driver = driver_auto_dgp.open_site(info)
        time.sleep(3)
        if navegador == 'brave':
            close_driver(navegador=navegador)
        else:
            close_driver(driver=driver)
    print(f'Fechado Driver Automático')

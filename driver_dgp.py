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
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.service import Service as FirefoxService


separador = "_________________________________________________________________________________________________________________________________________________________________"

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
# Mata processos travados
# ============================================================
def close_driver(driver=None, navegador=None):
    try:
        if driver:
            driver.quit()
            print(f'\n⚓  Fechando do driver ✅', end=' ', flush=True)
        elif navegador:
            subprocess.run(['taskkill', '/f', '/im', navegador], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f'\n⚓  Fechando do navegador {navegador} ✅', end=' ', flush=True)
        else:
            for navegador in ["chromedriver.exe", "chrome.exe", "msedgedriver.exe", "msedge.exe"]:
                subprocess.run(['taskkill', '/f', '/im', navegador], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f'\n⚓  Fechando do navegador {navegador} ✅', end=' ', flush=True)
    except:
        print(f'\n⚓  Fechando do driver ⛔', end=' ', flush=True)


# ============================================================
# Localizar monitor pela resolução
# ============================================================
def get_monitor(num=None, width=1360, height=768):
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
        self.text_print = ''

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
        driver.execute_script(f"document.body.style.zoom='{percentage}%'")

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
    #   FECHAR O DRIVER SE ERROS
    # ============================================================
    def close_browser_specify(self, process_name):
        user_home = os.path.expanduser("~")
        user_data_dir = os.path.join(user_home, "AppData", "navegador_historico")
        self.text_print += (f'Fechando {process_name} PID ')
        text_pid = ''
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and proc.info['name'].lower() == process_name.lower():
                    cmd = proc.info['cmdline']
                    if cmd and any(f'--user-data-dir={user_data_dir}' in arg for arg in cmd):
                        text_pid += f'{proc.pid}, '
                        proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        if text_pid:
            print(f'{self.text_print} {text_pid}', end=' | ')

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
            shutil.move(os.path.join(src, file), os.path.join(install_path, file))
        shutil.rmtree(src)
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
                close_driver()
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
        user_data_dir = os.path.join(user_home, "AppData", f"navegador_historico_{navegador}")
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
    def open_site(self, info, navegador='Chrome'):
        os.system('cls')
        self.text_print = ''
        print(f'{separador}\n⚓  {navegador} | Site: {info["site"][8:33]}', end=' | ')
        navegador = navegador.lower()

        if navegador == 'brave':
            self.close_browser_specify("brave.exe")
            self.get_version(navegador, r'Software\BraveSoftware\Brave-Browser\BLBeacon')
            driver = self.create_driver(navegador)
        elif navegador == 'edge':
            self.close_browser_specify("msedge.exe")
            self.get_version(navegador, r'Software\Microsoft\Edge\BLBeacon')
            driver = self.create_driver(navegador)
        elif navegador == 'firefox':
            self.close_browser_specify("firefox.exe")
            self.get_version(navegador, '')
            driver = self.create_driver(navegador)
        else:
            self.close_browser_specify("chrome.exe")
            self.get_version(navegador, r'Software\Google\Chrome\BLBeacon')
            driver = self.create_driver(navegador)

        target_monitor = get_monitor(num=3)
        driver.set_window_position(target_monitor["left"], target_monitor["top"])
        driver.get(info["site"])
        driver.maximize_window()
        print('✔️')
        return driver











class Driver_Manual_Dgp:
    def open_site_pre_open(self, info_ea):
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        user_home = os.path.expanduser("~")
        user_data_dir = os.path.join(user_home, "Documents", "jg_historico")

        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)

        target_monitor = get_monitor(width=1360, height=768)

        # Posiciona no canto do monitor alvo
        pos_x = target_monitor["left"]
        pos_y = target_monitor["top"]

        args = [
            chrome_path,
            "--remote-debugging-port=9222",
            f"--user-data-dir={user_data_dir}",
            f"--window-position={pos_x},{pos_y}",
            "--no-first-run",
            info_ea["site"],
        ]

        # 1. Abre o processo do Chrome
        subprocess.Popen(args)

        # 2. Aguarda a janela surgir e força o Maximizar pelo Windows
        time.sleep(1.5)  # Tempo para a janela ser criada
        for window in gw.getAllWindows():
            if "Chrome" in window.title or "Google" in window.title:
                window.maximize()
                break


# ============================================================
#   EXEMPLO DE USO
# ============================================================

if __name__ == '__main__':
    driver_manual_dgp = Driver_Manual_Dgp()
    driver_auto_dgp = Driver_Auto_Dgp()

    print(f'Abrir Driver Manual')
    info = {"site": 'https://google.com'}
    driver = driver_manual_dgp.open_site_pre_open(info)
    time.sleep(3)
    close_driver(navegador='chrome.exe')
    print(f'Fechado Driver Manual')




    print(f'\nAbrir Driver Automatico')
    info = {'site': 'https://www.speedtest.net/pt'}
    lista = ['chromes', 'edge', 'firefox', 'brave']
    num_list = len(lista)
    for n, navegador in enumerate(lista):
        time.sleep(1)
        print(f'{n+1}/{num_list} -> {navegador}\n')
        driver = driver_auto_dgp.open_site(info, navegador)
        time.sleep(3)
        if navegador == 'brave':
            close_driver(navegador='brave.exe')
        else:
            close_driver(driver=driver)
    print(f'Fechado Driver Automatico')

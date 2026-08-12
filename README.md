TUTORIAL: CRIAR E CENTRALIZAR A BIBLIOTECA E COMANDO CLI (driver_dgp)
===============================================================================
---------------------------------------------------------
## 1. ESTRUTURA DA PASTA DO PROJETO LOCAL
---------------------------------------------------------
Crie uma pasta com o nome driver_dgp e coloque os dois arquivos dentro dela:
```
driver_dgp/
    ├── driver_dgp.py      <-- O seu código da ferramenta Git
    ├── pyproject.toml      <-- Arquivo de configuração da biblioteca Python
    ├── README.md
    ├── LICENSE (Opcional)
    ├── .gitignore
    ├── .editorconfig
    ├── requirements-dev.txt
    └── CHANGELOG.md
```
---------------------------------------------------------
## 2. PUBLICAR NO GITHUB
---------------------------------------------------------
Repositório público ou privado no GitHub com o nome driver_dgp.

URL do repositório: https://github.com/davigopi/driver_dgp


---------------------------------------------------------
## 3. INSTALAR E ATUALIZAÇÕS
---------------------------------------------------------

Abra o terminal do seu computador, ative o ambiente virtual e, no diretório do repositório driver_dgp, execute

---------------------------------------------------------
## 4. INSTALAR A FERRAMENTA NO COMPUTADOR
---------------------------------------------------------
```bash
pip install git+https://github.com/davigopi/driver_dgp.git
```
---------------------------------------------------------
## 5. ATUALIZAR A FERRAMENTA NO FUTURO
---------------------------------------------------------
Alterado a version em pyproject.toml:
```bash
pip install --upgrade git+https://github.com/davigopi/driver_dgp.git
```
Força a atualização:
```bash
pip install --force-reinstall git+https://github.com/davigopi/driver_dgp.git
```
```bash
pip install --upgrade --no-cache-dir git+https://github.com/davigopi/driver_dgp.git
```

---------------------------------------------------------
## 6. INSTALAR REQUIREMENTS
---------------------------------------------------------
```bash
pip install -r venv\Lib\site-packages\driver_dgp\requirements.txt
```
---------------------------------------------------------
## 7. COMO USAR NOS SEUS PROJETOS
---------------------------------------------------------
- Via terminal (em qualquer pasta de projeto React Native, Python, etc.):
  Basta abrir o terminal na pasta desejada e digitar:
```bash
python -m driver_dgp
```
- Via importação dentro de scripts Python futuros:
```python
from driver_dgp import Driver_Dgp
```
```python
import driver_dgp
```

---------------------------------------------------------
## 8. EXEMPLOS DE CÓDIGO DE COMO UTILIZAR
---------------------------------------------------------

### A) Exemplo Básico

```python
import time
from driver_dgp import Driver_Dgp

# Instancia a classe
driver_auto = Driver_Dgp()

# Define o site
info = {'site': 'https://www.google.com'}

# Abre o site no navegador desejado ('chrome', 'edge', 'firefox', 'brave')
driver = driver_auto.open_site(info, navegador='chrome')

# Sua automação Selenium aqui...
time.sleep(3)

# Fecha o driver com segurança
driver_auto.close_driver(driver)
```
### B) Abrindo em Outros Navegadores
```python
from driver_dgp import Driver_Dgp

driver_auto = Driver_Dgp()
info = {'site': 'https://www.google.com'}

# Edge
driver_edge = driver_auto.open_site(info, navegador='edge')
driver_auto.close_driver(driver_edge)

# Firefox
driver_firefox = driver_auto.open_site(info, navegador='firefox')
driver_auto.close_driver(driver_firefox)

# Brave
driver_brave = driver_auto.open_site(info, navegador='brave')
driver_auto.close_driver(driver_brave)

```
### C) Utilizando Outras Funções da Classe
```python
from driver_dgp import Driver_Dgp

driver_auto = Driver_Dgp()
driver = driver_auto.open_site({'site': 'https://www.google.com'}, navegador='chrome')

# Ajustar zoom da página
driver_auto.set_zoom(driver, percentual=80)

# Ativar modo escuro
driver_auto.set_background_dark(driver, dark_mode=True)

# Atualizar a página
driver_auto.refresh_driver(driver)

driver_auto.close_driver(driver)
```

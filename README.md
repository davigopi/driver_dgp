TUTORIAL: CRIAR E CENTRALIZAR A BIBLIOTECA E COMANDO CLI (driver_dgp)
===============================================================================
---------------------------------------------------------
## 1. ESTRUTURA DA PASTA DO PROJETO LOCAL
---------------------------------------------------------
Crie uma pasta com o nome driver_dgp e coloque os dois arquivos dentro dela:
```bash
driver_dgp/
    ├── driver_dgp.py
    ├── pyproject.toml
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
## 8. PARÂMETROS DE CONFIGURAÇÃO (`info`)
---------------------------------------------------------

Ao utilizar os métodos `open_site(info)` das classes `Driver_Auto_Dgp` e `Driver_Manual_Dgp`, as configurações de inicialização devem ser passadas através de um dicionário (`info`).

### Estrutura do Dicionário `info`

| Chave | Tipo | Obrigatório? | Valor Padrão | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| `site` | `str` | **Sim** | — | URL completa da página que será aberta (ex: `'https://www.google.com'`). |
| `navegador` | `str` | Não | `'chrome'` | Navegador a ser utilizado. Opções aceitas: `'chrome'`, `'edge'`, `'firefox'`, `'brave'`. |
| `num` | `int` / `None` | Não | `1` | Número do monitor onde a janela deve ser aberta (base 1). Se definido como `None`, o sistema tentará identificar o monitor pelas chaves `width` e `height`. |
| `width` | `int` | Não | `None` | Largura da resolução do monitor de destino (ex: `1920`). Utilizado para identificar a tela quando `num=None`. |
| `height` | `int` | Não | `None` | Altura da resolução do monitor de destino (ex: `1080`). Utilizado para identificar a tela quando `num=None`. |

---

### Exemplo Completo de Declaração

```python
# Exemplo 1: Configuração básica (Abre no Chrome, Monitor 1)
info_basico = {
    'site': '[https://www.google.com](https://www.google.com)'
}

# Exemplo 2: Definindo navegador e monitor por número
info_monitor_num = {
    'site': '[https://www.google.com](https://www.google.com)',
    'navegador': 'edge',
    'num': 2  # Abre no segundo monitor
}

# Exemplo 3: Definindo monitor por resolução
info_monitor_res = {
    'site': '[https://www.google.com](https://www.google.com)',
    'navegador': 'firefox',
    'num': None,
    'width': 1360,
    'height': 768
}
```
---------------------------------------------------------
## 9. EXEMPLOS DE CÓDIGO DE COMO UTILIZAR
---------------------------------------------------------

### A) Modo Automático (Selenium Driver)
Utilize a classe `Driver_Auto_Dgp` para instanciar um driver do Selenium totalmente automatizado com gerenciamento automático de perfil e versão.

```python
import time
from driver_dgp import Driver_Auto_Dgp, close_driver

# Instancia a classe
driver_auto = Driver_Auto_Dgp()

# Configura as informações de acesso
info = {
    'site': '[https://www.google.com](https://www.google.com)',
    'navegador': 'chrome', # Opções: 'chrome', 'edge', 'firefox', 'brave'
    'num': 1               # Número do monitor onde a janela será posicionada
}

# Abre o site e retorna a instância do Selenium WebDriver
driver = driver_auto.open_site(info)

# Sua automação Selenium aqui...
time.sleep(3)

# Fecha o driver com segurança (para o Brave, utilize close_driver(navegador='brave'))
close_driver(driver=driver)
```
### B) Modo Manual (Abertura Direta do Navegador)
Utilize a classe Driver_Manual_Dgp para abrir o navegador via processo do sistema, mantendo perfil persistente e posicionamento de tela, sem vincular uma sessão Selenium.

```Python
import time
from driver_dgp import Driver_Manual_Dgp, close_driver

driver_manual = Driver_Manual_Dgp()

# Exemplo definindo o monitor pela resolução
info = {
    'site': '[https://www.google.com](https://www.google.com)',
    'navegador': 'edge',
    'num': None,          # Define como None para buscar pela resolução
    'width': 1920,
    'height': 1080
}

# Abre o navegador diretamente no SO
driver_manual.open_site(info)

time.sleep(5)

# Fecha o navegador pelo nome da aplicação
close_driver(navegador='edge')
```
### C) Abrindo em Outros Navegadores
A estrutura flexível do dicionário info permite alternar entre os navegadores suportados com facilidade.

```Python
import time
from driver_dgp import Driver_Auto_Dgp, close_driver

driver_auto = Driver_Auto_Dgp()

for nav in ['chrome', 'edge', 'firefox', 'brave']:
    info = {
        'site': '[https://www.google.com](https://www.google.com)',
        'navegador': nav
    }

    driver = driver_auto.open_site(info)
    time.sleep(2)

    # Tratamento para fechar o Brave ou o driver padrão
    if nav == 'brave':
        close_driver(navegador='brave')
    else:
        close_driver(driver=driver)
```
### D) Utilizando Funções Utilitárias e de Tela
Você pode manipular a visualização da página e o estado do navegador através dos métodos integrados.

```Python
from driver_dgp import Driver_Auto_Dgp, close_driver

driver_auto = Driver_Auto_Dgp()

info = {'site': '[https://www.google.com](https://www.google.com)', 'navegador': 'chrome'}
driver = driver_auto.open_site(info)

# Ajustar zoom da página (ex: 80%)
driver_auto.set_zoom(driver, percentage=80)

# Ativar modo escuro via JavaScript
driver_auto.set_background_dark(driver, dark_mode=True)

# Atualizar a página
driver_auto.refresh_driver(driver)

# Encerrar
close_driver(driver=driver)
```

<FollowUp label="Quer que eu ajude a documentar também as opções aceitas no dicionário 'info' no README?" query="Adicione uma tabela explicativa no README detalhando as chaves aceitas pelo dicionário 'info' (como site, navegador, num, width, height)."/>

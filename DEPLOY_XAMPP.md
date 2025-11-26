# Deploy no XAMPP (Windows)

Guia completo para fazer deploy do projeto Django no XAMPP após finalizar o desenvolvimento.

---

## 📋 Pré-requisitos

- ✅ XAMPP instalado (com Apache)
- ✅ Python 3.11+ instalado
- ✅ Desenvolvimento do projeto finalizado
- ✅ Git instalado (opcional, para versionamento)

---

## 🔄 PASSO 1: Preparar o Projeto para Produção

### 1.1 Atualizar o `settings.py` para produção

Abra `cozinha/settings.py` e ajuste:

```python
# DEBUG deve ser False em produção
DEBUG = False

# Adicione o IP/domínio do servidor XAMPP
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'seu-ip-local']

# Configure arquivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Configure arquivos de mídia
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### 1.2 Gerar uma SECRET_KEY segura

```powershell
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Copie o resultado e substitua no `settings.py`:

```python
SECRET_KEY = "cole-a-chave-gerada-aqui"
```

### 1.3 Criar arquivo `.env` (opcional mas recomendado)

Crie `.env` na raiz do projeto:

```env
DEBUG=False
SECRET_KEY=sua-secret-key-aqui
ALLOWED_HOSTS=localhost,127.0.0.1
```

E instale o python-decouple:

```powershell
pip install python-decouple
```

Ajuste o `settings.py`:

```python
from decouple import config

DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')
```

### 1.4 Atualizar o `requirements.txt`

```powershell
pip freeze > requirements.txt
```

---

## 📦 PASSO 2: Copiar o Projeto para o XAMPP

### 2.1 Copiar todos os arquivos

```powershell
xcopy /E /I e:\projetos\ficha_tecnica_cozinha C:\xampp\htdocs\ficha_tecnica_cozinha
```

**OU** se estiver usando Git:

```powershell
cd C:\xampp\htdocs
git clone https://github.com/seu-usuario/ficha_tecnica_cozinha_web.git ficha_tecnica_cozinha
```

### 2.2 Verificar a estrutura

```
C:\xampp\htdocs\ficha_tecnica_cozinha\
├── cozinha/
├── fichas/
├── eventos/
├── equipe/
├── templates/
├── media/
├── manage.py
├── requirements.txt
└── .gitignore
```

---

## 🐍 PASSO 3: Configurar Ambiente Virtual

### 3.1 Criar ambiente virtual

```powershell
cd C:\xampp\htdocs\ficha_tecnica_cozinha
python -m venv .venv
```

### 3.2 Ativar ambiente virtual

```powershell
.venv\Scripts\activate
```

### 3.3 Instalar dependências

```powershell
pip install -r requirements.txt
pip install mod_wsgi
```

---

## 🗄️ PASSO 4: Configurar o Banco de Dados

### 4.1 Executar migrações

```powershell
python manage.py migrate
```

### 4.2 Criar superusuário (admin)

```powershell
python manage.py createsuperuser
```

Informe:
- Username: `admin` (ou o que preferir)
- Email: seu email
- Password: senha segura

### 4.3 Coletar arquivos estáticos

```powershell
python manage.py collectstatic --noinput
```

### 4.4 (Opcional) Carregar dados iniciais

Se você tem fixtures ou dados de teste:

```powershell
python manage.py loaddata dados_iniciais.json
```

---

## ⚙️ PASSO 5: Configurar o Apache (mod_wsgi)

### 5.1 Obter configuração do mod_wsgi

```powershell
mod_wsgi-express module-config
```

**Copie a linha `LoadModule` que aparecer.** Exemplo:
```
LoadModule wsgi_module "C:/xampp/htdocs/ficha_tecnica_cozinha/.venv/Lib/site-packages/mod_wsgi/server/mod_wsgi.cp311-win_amd64.pyd"
```

### 5.2 Editar `httpd.conf`

Abra: `C:\xampp\apache\conf\httpd.conf`

**Cole a linha do LoadModule no final do arquivo:**

```apache
# Módulo WSGI para Django
LoadModule wsgi_module "C:/xampp/htdocs/ficha_tecnica_cozinha/.venv/Lib/site-packages/mod_wsgi/server/mod_wsgi.cp311-win_amd64.pyd"
```

### 5.3 Editar `httpd-vhosts.conf`

Abra: `C:\xampp\apache\conf\extra\httpd-vhosts.conf`

**Adicione no final:**

```apache
<VirtualHost *:80>
    ServerName localhost
    ServerAlias 127.0.0.1
    DocumentRoot "C:/xampp/htdocs/ficha_tecnica_cozinha"
    
    # Configuração WSGI
    WSGIScriptAlias / "C:/xampp/htdocs/ficha_tecnica_cozinha/cozinha/wsgi.py"
    WSGIPythonHome "C:/xampp/htdocs/ficha_tecnica_cozinha/.venv"
    WSGIPythonPath "C:/xampp/htdocs/ficha_tecnica_cozinha"
    
    # Diretório do Django
    <Directory "C:/xampp/htdocs/ficha_tecnica_cozinha/cozinha">
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>
    
    # Arquivos estáticos (CSS, JS, imagens do Django Admin)
    Alias /static "C:/xampp/htdocs/ficha_tecnica_cozinha/staticfiles"
    <Directory "C:/xampp/htdocs/ficha_tecnica_cozinha/staticfiles">
        Require all granted
    </Directory>
    
    # Arquivos de mídia (uploads dos usuários)
    Alias /media "C:/xampp/htdocs/ficha_tecnica_cozinha/media"
    <Directory "C:/xampp/htdocs/ficha_tecnica_cozinha/media">
        Require all granted
    </Directory>
    
    # Logs
    ErrorLog "C:/xampp/apache/logs/django_error.log"
    CustomLog "C:/xampp/apache/logs/django_access.log" combined
</VirtualHost>
```

### 5.4 Ajustar permissões (se necessário)

Dê permissão de escrita para a pasta do banco de dados:

```powershell
icacls C:\xampp\htdocs\ficha_tecnica_cozinha\db.sqlite3 /grant Everyone:F
icacls C:\xampp\htdocs\ficha_tecnica_cozinha\media /grant Everyone:F
```

---

## 🚀 PASSO 6: Iniciar o Servidor

### 6.1 Abrir XAMPP Control Panel

- Execute `C:\xampp\xampp-control.exe`

### 6.2 Reiniciar o Apache

- Clique em **Stop** no Apache (se estiver rodando)
- Clique em **Start**

### 6.3 Verificar erros

Se o Apache não iniciar, verifique os logs:
- `C:\xampp\apache\logs\error.log`
- `C:\xampp\apache\logs\django_error.log`

---

## ✅ PASSO 7: Testar o Sistema

### 7.1 Acessar a página inicial

Abra o navegador em:
```
http://localhost
```

Deve carregar a página inicial do sistema de fichas técnicas.

### 7.2 Acessar o Admin

```
http://localhost/admin
```

Faça login com o superusuário criado.

### 7.3 Testar funcionalidades

- ✅ Cadastrar ingredientes
- ✅ Criar receitas
- ✅ Adicionar eventos
- ✅ Fazer upload de imagens
- ✅ Gerar fichas técnicas

---

## 🔧 Método Alternativo: Servidor de Desenvolvimento

Se tiver problemas com o Apache, use o servidor do Django:

### 1. Ativar ambiente virtual

```powershell
cd C:\xampp\htdocs\ficha_tecnica_cozinha
.venv\Scripts\activate
```

### 2. Iniciar servidor

```powershell
python manage.py runserver 0.0.0.0:8000
```

### 3. Acessar

```
http://localhost:8000
```

⚠️ **Não use em produção real!** Apenas para desenvolvimento/testes locais.

---

## 📊 PASSO 8: Configurações Opcionais

### 8.1 Usar MySQL ao invés de SQLite

#### Instalar driver

```powershell
pip install mysqlclient
```

#### Criar banco no MySQL

Abra phpMyAdmin: `http://localhost/phpmyadmin`

- Criar banco: `ficha_tecnica_db`
- Collation: `utf8mb4_general_ci`

#### Configurar no `settings.py`

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ficha_tecnica_db',
        'USER': 'root',
        'PASSWORD': '',  # Senha do MySQL (padrão é vazio no XAMPP)
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

#### Executar migrações novamente

```powershell
python manage.py migrate
python manage.py createsuperuser
```

### 8.2 Configurar Email (para recuperação de senha)

No `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'sua-senha-app'
DEFAULT_FROM_EMAIL = 'seu-email@gmail.com'
```

### 8.3 Configurar Logs

No `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

Criar pasta de logs:

```powershell
mkdir C:\xampp\htdocs\ficha_tecnica_cozinha\logs
```

---

## 🛠️ Troubleshooting

### 1. Copiar o projeto para o XAMPP

```powershell
xcopy /E /I e:\projetos\ficha_tecnica_cozinha C:\xampp\htdocs\ficha_tecnica_cozinha
```

### 2. Criar ambiente virtual e instalar dependências

```powershell
cd C:\xampp\htdocs\ficha_tecnica_cozinha
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install mod_wsgi
```

### 3. Configurar o Apache

#### 3.1 Obter o caminho do mod_wsgi

```powershell
mod_wsgi-express module-config
```

Copie a linha `LoadModule` que aparece.

#### 3.2 Editar `C:\xampp\apache\conf\httpd.conf`

Adicione no final do arquivo a linha do LoadModule:

```apache
LoadModule wsgi_module "C:/xampp/htdocs/ficha_tecnica_cozinha/.venv/Lib/site-packages/mod_wsgi/server/mod_wsgi.cp311-win_amd64.pyd"
```

⚠️ **Nota**: O caminho pode variar conforme a versão do Python (cp311 = Python 3.11)

#### 3.3 Editar `C:\xampp\apache\conf\extra\httpd-vhosts.conf`

Adicione no final:

```apache
<VirtualHost *:80>
    ServerName localhost
    DocumentRoot "C:/xampp/htdocs/ficha_tecnica_cozinha"
    
    WSGIScriptAlias / "C:/xampp/htdocs/ficha_tecnica_cozinha/cozinha/wsgi.py"
    WSGIPythonHome "C:/xampp/htdocs/ficha_tecnica_cozinha/.venv"
    WSGIPythonPath "C:/xampp/htdocs/ficha_tecnica_cozinha"
    
    <Directory "C:/xampp/htdocs/ficha_tecnica_cozinha/cozinha">
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>
    
    Alias /static "C:/xampp/htdocs/ficha_tecnica_cozinha/staticfiles"
    <Directory "C:/xampp/htdocs/ficha_tecnica_cozinha/staticfiles">
        Require all granted
    </Directory>
    
    Alias /media "C:/xampp/htdocs/ficha_tecnica_cozinha/media"
    <Directory "C:/xampp/htdocs/ficha_tecnica_cozinha/media">
        Require all granted
    </Directory>
</VirtualHost>
```

### 4. Preparar o Django

```powershell
cd C:\xampp\htdocs\ficha_tecnica_cozinha
.venv\Scripts\activate
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 5. Reiniciar o Apache

- Abra o **XAMPP Control Panel**
- Clique em **Stop** no Apache
- Clique em **Start** novamente

### 6. Acessar o sistema

Abra o navegador em: `http://localhost`

---

## Método 2: Servidor de Desenvolvimento (Mais Simples)

Para desenvolvimento e testes, use o servidor embutido do Django:

### 1. Copiar o projeto

```powershell
xcopy /E /I e:\projetos\ficha_tecnica_cozinha C:\xampp\htdocs\ficha_tecnica_cozinha
```

### 2. Instalar dependências

```powershell
cd C:\xampp\htdocs\ficha_tecnica_cozinha
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Preparar o banco de dados

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 4. Iniciar o servidor

```powershell
python manage.py runserver 0.0.0.0:8000
```

### 5. Acessar o sistema

Abra o navegador em: `http://localhost:8000`

**Admin**: `http://localhost:8000/admin`

---

## Troubleshooting

### Erro: "No module named 'mod_wsgi'"

```powershell
pip install mod_wsgi
```

### Erro: "Cannot load modules/mod_wsgi.so"

Verifique o caminho no `LoadModule`. Execute:
```powershell
mod_wsgi-express module-config
```

### Apache não inicia

Verifique os logs em: `C:\xampp\apache\logs\error.log`

### Página em branco ou erro 500

Verifique os logs do Apache e do Django:
- `C:\xampp\apache\logs\error.log`
- Console onde rodou o servidor

### Static files não carregam

Execute:
```powershell
python manage.py collectstatic --noinput
```

Verifique as permissões da pasta `staticfiles/`

---

## Configurações Recomendadas para Produção Local

### 1. Criar arquivo `.env`

```env
DEBUG=False
SECRET_KEY=gere-uma-chave-segura
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 2. Gerar SECRET_KEY segura

```powershell
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 3. Configurar MySQL (opcional - padrão é SQLite)

No `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ficha_tecnica_db',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

Instale o driver:
```powershell
pip install mysqlclient
```

---

## Comandos Úteis

### Ativar ambiente virtual
```powershell
.venv\Scripts\activate
```

### Criar novo superusuário
```powershell
python manage.py createsuperuser
```

### Atualizar banco de dados
```powershell
python manage.py migrate
```

### Coletar arquivos estáticos
```powershell
python manage.py collectstatic --noinput
```

### Verificar configurações
```powershell
python manage.py check
```

### Rodar testes
```powershell
python manage.py test
```

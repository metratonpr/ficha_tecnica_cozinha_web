# Deploy no DirectAdmin

## 1. Preparar o Projeto Localmente

### 1.1 Criar arquivo de produção
Crie o arquivo `.env` na raiz do projeto:
```bash
DEBUG=False
SECRET_KEY=sua-chave-secreta-aqui-gere-uma-nova
ALLOWED_HOSTS=seudominio.com,www.seudominio.com
DATABASE_URL=sqlite:///db.sqlite3
```

### 1.2 Atualizar settings.py para produção
Adicione no `cozinha/settings.py`:
```python
import os
from pathlib import Path

DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY', 'sua-chave-atual')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')
```

## 2. Configurar no DirectAdmin

### 2.1 Acessar o DirectAdmin
- Acesse: `https://seuservidor.com:2222`
- Login com suas credenciais

### 2.2 Instalar Python App
1. Vá em **Python App Setup** ou **Python Selector**
2. Crie uma nova aplicação:
   - Nome: `ficha_tecnica`
   - Versão Python: `3.11` ou superior
   - Diretório: `public_html/ficha_tecnica` ou `domains/seudominio.com/ficha_tecnica`
   - Entry point: `passenger_wsgi.py`

### 2.3 Upload dos Arquivos
Via **File Manager** ou **FTP**:
1. Compacte o projeto: `zip -r projeto.zip . -x ".venv/*" "__pycache__/*" "*.pyc" "db.sqlite3"`
2. Upload para o diretório escolhido
3. Extraia o arquivo

### 2.4 Criar passenger_wsgi.py
No diretório raiz do projeto, crie `passenger_wsgi.py`:
```python
import sys
import os

# Adiciona o diretório do projeto ao path
INTERP = os.path.join(os.environ['HOME'], 'virtualenv', 'public_html', 'ficha_tecnica', '3.11', 'bin', 'python3')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.insert(0, os.path.dirname(__file__))

# Configura o Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'cozinha.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 3. Instalar Dependências

### Via Terminal SSH:
```bash
cd ~/domains/seudominio.com/ficha_tecnica
source ~/virtualenv/ficha_tecnica/3.11/bin/activate
pip install -r requirements.txt
```

### Ou via DirectAdmin Python App:
- Copie o conteúdo de `requirements.txt`
- Cole na área de dependências

## 4. Configurar Banco de Dados

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## 5. Configurar Arquivos Estáticos

### No DirectAdmin:
1. Vá em **File Manager**
2. Crie diretórios:
   - `public_html/static/`
   - `public_html/media/`
3. Defina permissões: `755`

### Atualizar settings.py:
```python
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'public_html', 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'public_html', 'media')
```

## 6. Configurar .htaccess

Crie `.htaccess` no diretório public_html:
```apache
# Desabilita mod_security
<IfModule mod_security.c>
    SecFilterEngine Off
    SecFilterScanPOST Off
</IfModule>

# Python application
PassengerEnabled On
PassengerAppRoot /home/usuario/domains/seudominio.com/ficha_tecnica

# Servir arquivos estáticos diretamente
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteBase /
    
    # Servir static files
    RewriteCond %{REQUEST_URI} ^/static/
    RewriteRule ^(.*)$ - [L]
    
    # Servir media files
    RewriteCond %{REQUEST_URI} ^/media/
    RewriteRule ^(.*)$ - [L]
    
    # Redirecionar tudo para o WSGI
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule ^(.*)$ passenger_wsgi.py [L]
</IfModule>
```

## 7. Reiniciar Aplicação

### Via DirectAdmin:
1. Python App Setup
2. Clique em **Restart**

### Via SSH:
```bash
touch ~/domains/seudominio.com/ficha_tecnica/tmp/restart.txt
```

## 8. Testar

Acesse: `https://seudominio.com`

## Checklist Final

- [ ] Arquivo `.env` configurado
- [ ] `DEBUG=False` em produção
- [ ] `SECRET_KEY` única gerada
- [ ] `ALLOWED_HOSTS` configurado
- [ ] Dependências instaladas
- [ ] Migrações executadas
- [ ] Arquivos estáticos coletados
- [ ] Superusuário criado
- [ ] Permissões de diretórios corretas (755)
- [ ] `.htaccess` configurado
- [ ] Aplicação reiniciada

## Comandos Úteis

```bash
# Ver logs de erro
tail -f ~/domains/seudominio.com/logs/error.log

# Reiniciar app
touch ~/domains/seudominio.com/ficha_tecnica/tmp/restart.txt

# Coletar static files
python manage.py collectstatic --noinput

# Fazer backup do banco
cp db.sqlite3 db.sqlite3.backup
```

## Troubleshooting

### Erro 500:
- Verifique `DEBUG=True` temporariamente para ver o erro
- Cheque os logs em `~/domains/seudominio.com/logs/error.log`

### Static files não carregam:
- Execute `python manage.py collectstatic`
- Verifique permissões dos diretórios

### Aplicação não atualiza:
- Execute: `touch tmp/restart.txt`
- Limpe o cache do navegador

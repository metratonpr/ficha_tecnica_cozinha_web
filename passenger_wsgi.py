import sys
import os

# Caminho para o interpretador Python do virtualenv
INTERP = os.path.join(os.environ['HOME'], 'virtualenv', 'domains', 'receitas.iapotech.com.br', 'public_html', 'ficha_tecnica_cozinha', '3.11', 'bin', 'python3')

if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Adiciona o diretório do projeto ao Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ficha_tecnica_cozinha'))

# Configura as variáveis de ambiente do Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'cozinha.settings'

# Carrega a aplicação WSGI do Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

import sys
import os

# Caminho para o interpretador Python do virtualenv
# AJUSTE O CAMINHO CONFORME SEU SERVIDOR
INTERP = os.path.join(os.environ['HOME'], 'virtualenv', 'ficha_tecnica', '3.11', 'bin', 'python3')

if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Adiciona o diretório do projeto ao Python path
sys.path.insert(0, os.path.dirname(__file__))

# Configura as variáveis de ambiente do Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'cozinha.settings'

# Carrega a aplicação WSGI do Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

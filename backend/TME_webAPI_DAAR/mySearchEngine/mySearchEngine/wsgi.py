import os
import sys
from django.core.wsgi import get_wsgi_application

# Ajouter le chemin parent au sys.path pour que 'mySearchEngine' soit trouvé
sys.path.append('/var/task/backend/TME_webAPI_DAAR/mySearchEngine')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.TME_webAPI_DAAR.mySearchEngine.mySearchEngine.settings')
app = get_wsgi_application()
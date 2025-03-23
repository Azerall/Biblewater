import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.TME_webAPI_DAAR.mySearchEngine.mySearchEngine.settings')

application = get_wsgi_application()
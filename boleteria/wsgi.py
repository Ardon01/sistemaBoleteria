"""
WSGI config for boleteria project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boleteria.settings')

application = get_wsgi_application()

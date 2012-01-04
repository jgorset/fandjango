from django.core.management  import setup_environ

from project import settings

# Configure Django's environments.
setup_environ(settings)

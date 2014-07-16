import os

if 'DJANGO_DEV' in os.environ:
    from .dev import *
else:
    from .prod import *

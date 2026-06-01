# -*- coding: utf-8 -*-
"""Launch the SHAMEL ASGI app under Daphne with APScheduler INFO logging,
so scheduler job executions (and any InterfaceError) are visible in stdout.
Non-intrusive: does not modify app code."""
import os, sys, logging

os.environ.setdefault('USE_LOCAL_DB', 'true')
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'acdc_config.settings')

# Surface APScheduler job execution + errors
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    stream=sys.stdout,
)
logging.getLogger('apscheduler').setLevel(logging.INFO)
logging.getLogger('apscheduler.executors.default').setLevel(logging.INFO)

import django
django.setup()

from daphne.cli import CommandLineInterface

if __name__ == '__main__':
    # bind 0.0.0.0:9000 so it doesn't clash with the runserver on 8000
    sys.argv = ['daphne', '-b', '0.0.0.0', '-p', '9000', 'acdc_config.asgi:application']
    CommandLineInterface().run(sys.argv[1:])

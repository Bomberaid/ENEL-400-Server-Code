from gevent import monkey
monkey.patch_all()  # Must be first, before anything else

from app import create_app

app = create_app()
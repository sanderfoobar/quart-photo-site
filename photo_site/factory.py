import os
import logging
import asyncio

from quart import Quart
from quart_auth import AuthManager

import settings
from photo_site.routes import bp_routes
from photo_site.routes_admin import bp_routes_admin

app = None
auth_manager = AuthManager()


async def _setup_database(app: Quart):
    import peewee
    import photo_site.models
    models = peewee.Model.__subclasses__()
    for m in models:
        m.create_table()


def create_app():
    global app
    app = Quart(__name__)
    auth_manager.init_app(app)
    app.config['MAX_CONTENT_LENGTH'] = 20971520 * 10
    app.logger.setLevel(logging.INFO)
    app.secret_key = settings.app_secret

    if not os.path.exists(settings.data_dir):
        os.mkdir(settings.data_dir)

    @app.context_processor
    def template_variables():
        from quart_auth import current_user
        return dict(current_user=current_user)

    @app.before_serving
    async def startup():
        await _setup_database(app)
        app.register_blueprint(bp_routes)
        app.register_blueprint(bp_routes_admin)

    return app

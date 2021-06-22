from photo_site.factory import create_app
import settings

app = create_app()
app.run(settings.host, port=settings.port, debug=settings.debug, use_reloader=False)

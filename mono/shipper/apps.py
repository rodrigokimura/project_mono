from django.apps import AppConfig


class ShipperConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shipper'

    def ready(self):
        from shipper import signals
        signals.__name__

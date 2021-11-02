from django.apps import AppConfig


class RamenappConfig(AppConfig):
    name = 'ramenapp'

    def ready(self):
        # シグナルのロードをする。signals.pyを読み込むだけでOK
        from . import signals





    

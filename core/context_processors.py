from .models import Configuracion

def info_clinica(request):
    try:
        config = Configuracion.objects.first()
    except:
        config = None
    
    return {
        'clinica_config': config
    }
from django.contrib import admin
from .models import ObraSocial, TipoTratamiento, Arancel, Paciente, Turno, LiquidacionObraSocial, CategoriaGasto, Gasto, Configuracion

admin.site.register(ObraSocial)
admin.site.register(TipoTratamiento)
admin.site.register(Arancel)
admin.site.register(Paciente)
admin.site.register(Turno)
admin.site.register(LiquidacionObraSocial)
admin.site.register(CategoriaGasto)
admin.site.register(Gasto)
admin.site.register(Configuracion)
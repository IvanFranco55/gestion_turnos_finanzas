from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import (
    lista_turnos, balance_financiero, # Vistas Funciones
    TurnoCreateView, TurnoUpdateView, TurnoDeleteView, # Vistas Clases (Las que faltaban)
    toggle_atendido, toggle_pagado, # Las nuevas funciones de los botones
    reporte_deudores, registrar_pago_deuda
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.lista_turnos, name='lista_turnos'), # Home por defecto
    path('balance/', views.balance_financiero, name='balance'),
    path('pacientes/', views.PacienteListView.as_view(), name='lista_pacientes'),
    path('pacientes/nuevo/', views.PacienteCreateView.as_view(), name='crear_paciente'),
    path('pacientes/editar/<int:pk>/', views.PacienteUpdateView.as_view(), name='editar_paciente'),
    path('pacientes/borrar/<int:pk>/', views.PacienteDeleteView.as_view(), name='borrar_paciente'),
    # OBRAS SOCIALES
    path('config/obras-sociales/', views.ObraSocialListView.as_view(), name='lista_obras_sociales'),
    path('config/obras-sociales/nueva/', views.ObraSocialCreateView.as_view(), name='crear_os'),
    path('config/obras-sociales/editar/<int:pk>/', views.ObraSocialUpdateView.as_view(), name='editar_os'),
    path('config/obras-sociales/borrar/<int:pk>/', views.ObraSocialDeleteView.as_view(), name='borrar_os'),

    # TRATAMIENTOS
    path('config/tratamientos/', views.TratamientoListView.as_view(), name='lista_tratamientos'),
    path('config/tratamientos/nuevo/', views.TratamientoCreateView.as_view(), name='crear_tratamiento'),
    path('config/tratamientos/editar/<int:pk>/', views.TratamientoUpdateView.as_view(), name='editar_tratamiento'),
    path('config/tratamientos/borrar/<int:pk>/', views.TratamientoDeleteView.as_view(), name='borrar_tratamiento'),

    path('turnos/nuevo/', views.TurnoCreateView.as_view(), name='crear_turno'),
    path('turnos/editar/<int:pk>/', views.TurnoUpdateView.as_view(), name='editar_turno'),
    path('turno/borrar/<int:pk>/', views.TurnoDeleteView.as_view(), name='borrar_turno'),

    path('finanzas/gasto/nuevo/', views.GastoCreateView.as_view(), name='crear_gasto'),
    path('finanzas/liquidacion/nueva/', views.LiquidacionCreateView.as_view(), name='crear_liquidacion'),

    # ARANCELES
    path('config/aranceles/', views.ArancelListView.as_view(), name='lista_aranceles'),
    path('config/aranceles/nuevo/', views.ArancelCreateView.as_view(), name='crear_arancel'),
    path('config/aranceles/editar/<int:pk>/', views.ArancelUpdateView.as_view(), name='editar_arancel'),
    path('config/aranceles/borrar/<int:pk>/', views.ArancelDeleteView.as_view(), name='borrar_arancel'),

    # CATEGORIAS
    path('config/categorias/', views.CategoriaListView.as_view(), name='lista_categorias'),
    path('config/categorias/nuevo/', views.CategoriaCreateView.as_view(), name='crear_categoria'),
    path('config/categorias/borrar/<int:pk>/', views.CategoriaDeleteView.as_view(), name='borrar_categoria'),

    # GASTOS
    path('finanzas/gasto/editar/<int:pk>/', views.GastoUpdateView.as_view(), name='editar_gasto'),
    path('finanzas/gasto/borrar/<int:pk>/', views.GastoDeleteView.as_view(), name='borrar_gasto'),

    # LIQUIDACIONES (Ingresos OS)
    path('finanzas/liquidacion/editar/<int:pk>/', views.LiquidacionUpdateView.as_view(), name='editar_liquidacion'),
    path('finanzas/liquidacion/borrar/<int:pk>/', views.LiquidacionDeleteView.as_view(), name='borrar_liquidacion'),

    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path('turno/toggle-atendido/<int:pk>/', toggle_atendido, name='toggle_atendido'),
    path('turno/toggle-pagado/<int:pk>/', toggle_pagado, name='toggle_pagado'),

    path('finanzas/deudores/', reporte_deudores, name='reporte_deudores'),

    path('finanzas/pagar-deuda/<int:pk>/', registrar_pago_deuda, name='registrar_pago_deuda'),

    path('config/actualizar-logo/', views.actualizar_logo, name='actualizar_logo'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
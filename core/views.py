from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin # Para las clases
from django.contrib.auth.decorators import login_required # Para las funciones (def)

# Importamos todos los modelos y formularios
from .models import (
    Turno, Gasto, LiquidacionObraSocial, Paciente, ObraSocial, 
    TipoTratamiento, Arancel, CategoriaGasto
)
from .forms import (
    PacienteForm, ObraSocialForm, TipoTratamientoForm, TurnoForm, 
    GastoForm, LiquidacionForm, ArancelForm, CategoriaGastoForm
)

# --- VISTA 1: AGENDA DE TURNOS ---
@login_required # <--- CANDADO AGREGADO
def lista_turnos(request):
    turnos = Turno.objects.all().order_by('-fecha', 'hora')
    
    # Filtros
    fecha_filtro = request.GET.get('fecha')       # Filtro Día exacto
    mes_filtro = request.GET.get('mes')           # Filtro Mes entero
    paciente_filtro = request.GET.get('paciente') # Filtro Apellido

    if fecha_filtro:
        turnos = turnos.filter(fecha=fecha_filtro)
    
    # Lógica del Filtro de Mes
    if mes_filtro:
        anio, mes = mes_filtro.split('-')
        turnos = turnos.filter(fecha__year=anio, fecha__month=mes)

    if paciente_filtro:
        turnos = turnos.filter(paciente__apellido__icontains=paciente_filtro)

    # Calculamos el total de lo que se ve en pantalla
    total_filtrado = sum(t.monto_paciente for t in turnos if t.pagado)

    context = {
        'turnos': turnos,
        'total': total_filtrado,
    }
    return render(request, 'core/lista_turnos.html', context)

# --- VISTA 2: BALANCE GENERAL ---
@login_required # <--- CANDADO AGREGADO
def balance_financiero(request):
    hoy = timezone.now()
    
    # 1. CAPTURAR FILTROS
    mes = request.GET.get('mes', hoy.month)
    anio = request.GET.get('anio', hoy.year)
    os_id = request.GET.get('obra_social', '')

    try:
        mes = int(mes)
        anio = int(anio)
    except ValueError:
        mes = hoy.month
        anio = hoy.year

    # 2. CONSULTAS BASE
    turnos = Turno.objects.filter(
        fecha__month=mes, 
        fecha__year=anio
    ).exclude(estado='CANCELADO')

    liquidaciones = LiquidacionObraSocial.objects.filter(fecha_ingreso__month=mes, fecha_ingreso__year=anio)
    gastos = Gasto.objects.filter(fecha__month=mes, fecha__year=anio)

    # 3. FILTRO POR OBRA SOCIAL
    if os_id:
        turnos = turnos.filter(obra_social_aplicada_id=os_id)
        liquidaciones = liquidaciones.filter(obra_social_id=os_id)

    # 4. SUMAR
    total_turnos = turnos.aggregate(Sum('monto_pagado'))['monto_pagado__sum'] or 0
    total_os = liquidaciones.aggregate(Sum('monto_total'))['monto_total__sum'] or 0
    total_gastos = gastos.aggregate(Sum('monto'))['monto__sum'] or 0

    resultado = (total_turnos + total_os) - total_gastos

    meses_nombre = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
        7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }

    context = {
        'ingresos_turnos': total_turnos,
        'ingresos_os': total_os,
        'egresos': total_gastos,
        'resultado': resultado,
        'mes_actual': mes,
        'anio_actual': anio,
        'os_actual': int(os_id) if os_id else '',
        'nombre_mes': meses_nombre.get(mes),
        'lista_meses': meses_nombre.items(),
        'lista_anios': range(2024, 2030),
        'obras_sociales': ObraSocial.objects.all(),
        'movimientos_turnos': turnos.filter(monto_pagado__gt=0).order_by('-fecha', '-hora'),
        'movimientos_gastos': gastos.order_by('-fecha'),
        'movimientos_os': liquidaciones.order_by('-fecha_ingreso'),
    }
    return render(request, 'core/balance.html', context)

# --- ABM PACIENTES ---
class PacienteListView(LoginRequiredMixin, ListView): # <--- CANDADO AGREGADO
    model = Paciente
    template_name = 'core/pacientes/lista.html'
    context_object_name = 'pacientes'
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Paciente.objects.filter(apellido__icontains=query)
        return Paciente.objects.all()

class PacienteCreateView(LoginRequiredMixin, CreateView): # <--- CANDADO AGREGADO
    model = Paciente
    form_class = PacienteForm
    template_name = 'core/pacientes/form.html'
    success_url = reverse_lazy('lista_pacientes')

class PacienteUpdateView(LoginRequiredMixin, UpdateView): # <--- CANDADO AGREGADO
    model = Paciente
    form_class = PacienteForm
    template_name = 'core/pacientes/form.html'
    success_url = reverse_lazy('lista_pacientes')

class PacienteDeleteView(LoginRequiredMixin, DeleteView): # <--- CANDADO AGREGADO
    model = Paciente
    template_name = 'core/pacientes/confirmar_borrar.html'
    success_url = reverse_lazy('lista_pacientes')

# --- ABM OBRAS SOCIALES ---
class ObraSocialListView(LoginRequiredMixin, ListView): # <--- CANDADO AGREGADO
    model = ObraSocial
    template_name = 'core/config/lista_os.html'
    context_object_name = 'obras_sociales'

class ObraSocialCreateView(LoginRequiredMixin, CreateView): # <--- CANDADO AGREGADO
    model = ObraSocial
    form_class = ObraSocialForm
    template_name = 'core/config/form_generico.html'
    success_url = reverse_lazy('lista_obras_sociales')

class ObraSocialUpdateView(LoginRequiredMixin, UpdateView): # <--- CANDADO AGREGADO
    model = ObraSocial
    form_class = ObraSocialForm
    template_name = 'core/config/form_generico.html'
    success_url = reverse_lazy('lista_obras_sociales')

class ObraSocialDeleteView(LoginRequiredMixin, DeleteView): # <--- CANDADO AGREGADO
    model = ObraSocial
    template_name = 'core/config/confirmar_borrar.html'
    success_url = reverse_lazy('lista_obras_sociales')

# --- ABM TRATAMIENTOS ---
class TratamientoListView(LoginRequiredMixin, ListView): # <--- CANDADO AGREGADO
    model = TipoTratamiento
    template_name = 'core/config/lista_tratamientos.html'
    context_object_name = 'tratamientos'

class TratamientoCreateView(LoginRequiredMixin, CreateView): # <--- CANDADO AGREGADO
    model = TipoTratamiento
    form_class = TipoTratamientoForm
    template_name = 'core/config/form_generico.html'
    success_url = reverse_lazy('lista_tratamientos')

class TratamientoUpdateView(LoginRequiredMixin, UpdateView): # <--- CANDADO AGREGADO
    model = TipoTratamiento
    form_class = TipoTratamientoForm
    template_name = 'core/config/form_generico.html'
    success_url = reverse_lazy('lista_tratamientos')

class TratamientoDeleteView(LoginRequiredMixin, DeleteView): # <--- CANDADO AGREGADO
    model = TipoTratamiento
    template_name = 'core/config/confirmar_borrar.html'
    success_url = reverse_lazy('lista_tratamientos')

# --- ABM TURNOS ---
class TurnoCreateView(LoginRequiredMixin, CreateView): # <--- CANDADO AGREGADO
    model = Turno
    form_class = TurnoForm
    template_name = 'core/turnos/form.html'
    success_url = reverse_lazy('lista_turnos')

class TurnoUpdateView(LoginRequiredMixin, UpdateView): # <--- CANDADO AGREGADO
    model = Turno
    form_class = TurnoForm
    template_name = 'core/turnos/form.html'
    success_url = reverse_lazy('lista_turnos')

class TurnoDeleteView(LoginRequiredMixin, DeleteView): # <--- CANDADO AGREGADO
    model = Turno
    template_name = 'core/config/confirmar_borrar.html'
    success_url = reverse_lazy('lista_turnos')

# --- ABM GASTOS ---
class GastoCreateView(LoginRequiredMixin, CreateView): # <--- CANDADO AGREGADO
    model = Gasto
    form_class = GastoForm
    template_name = 'core/config/form_generico.html'
    success_url = reverse_lazy('balance')

class GastoUpdateView(LoginRequiredMixin, UpdateView): # <--- CANDADO AGREGADO
    model = Gasto
    form_class = GastoForm
    template_name = 'core/config/form_generico.html'
    success_url = reverse_lazy('balance')

class GastoDeleteView(LoginRequiredMixin, DeleteView): # <--- CANDADO AGREGADO
    model = Gasto
    template_name = 'core/config/confirmar_borrar.html'
    success_url = reverse_lazy('balance')

# --- ABM LIQUIDACIONES (Ingresos OS) ---
class LiquidacionCreateView(LoginRequiredMixin, CreateView): # <--- CANDADO AGREGADO
    model = LiquidacionObraSocial
    form_class = LiquidacionForm
    template_name = 'core/config/form_generico.html'
    success_url = reverse_lazy('balance')

class LiquidacionUpdateView(LoginRequiredMixin, UpdateView): # <--- CANDADO AGREGADO
    model = LiquidacionObraSocial
    form_class = LiquidacionForm
    template_name = 'core/config/form_generico.html'
    success_url = reverse_lazy('balance')

class LiquidacionDeleteView(LoginRequiredMixin, DeleteView): # <--- CANDADO AGREGADO
    model = LiquidacionObraSocial
    template_name = 'core/config/confirmar_borrar.html'
    success_url = reverse_lazy('balance')

# --- ABM ARANCELES ---
class ArancelListView(LoginRequiredMixin, ListView): # <--- CANDADO AGREGADO
    model = Arancel
    template_name = 'core/config/lista_aranceles.html'
    context_object_name = 'aranceles'

    def get_queryset(self):
        queryset = super().get_queryset()
        os_id = self.request.GET.get('obra_social')
        if os_id:
            queryset = queryset.filter(obra_social_id=os_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['obras_sociales'] = ObraSocial.objects.all()
        context['os_seleccionada'] = int(self.request.GET.get('obra_social')) if self.request.GET.get('obra_social') else None
        return context

class ArancelCreateView(LoginRequiredMixin, CreateView): # <--- CANDADO AGREGADO
    model = Arancel
    form_class = ArancelForm
    template_name = 'core/config/form_generico.html'
    success_url = reverse_lazy('lista_aranceles')

class ArancelUpdateView(LoginRequiredMixin, UpdateView): # <--- CANDADO AGREGADO
    model = Arancel
    form_class = ArancelForm
    template_name = 'core/config/form_generico.html'
    success_url = reverse_lazy('lista_aranceles')

class ArancelDeleteView(LoginRequiredMixin, DeleteView): # <--- CANDADO AGREGADO
    model = Arancel
    template_name = 'core/config/confirmar_borrar.html'
    success_url = reverse_lazy('lista_aranceles')

# --- ABM CATEGORIAS DE GASTOS ---
class CategoriaListView(LoginRequiredMixin, ListView): # <--- CANDADO AGREGADO
    model = CategoriaGasto
    template_name = 'core/config/lista_categorias.html'
    context_object_name = 'categorias'

class CategoriaCreateView(LoginRequiredMixin, CreateView): # <--- CANDADO AGREGADO
    model = CategoriaGasto
    form_class = CategoriaGastoForm
    template_name = 'core/config/form_generico.html'
    success_url = reverse_lazy('lista_categorias')

class CategoriaDeleteView(LoginRequiredMixin, DeleteView): # <--- CANDADO AGREGADO
    model = CategoriaGasto
    template_name = 'core/config/confirmar_borrar.html'
    success_url = reverse_lazy('lista_categorias')
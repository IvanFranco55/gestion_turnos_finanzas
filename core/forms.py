from django import forms
from .models import Paciente, ObraSocial, TipoTratamiento, Turno, Gasto, LiquidacionObraSocial, Arancel, CategoriaGasto

# --- 1. MIXIN INTELIGENTE (TIENE QUE IR PRIMERO) ---
class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            # SI ES UN CHECKBOX: Usamos la clase especial 'form-check-input'
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            # SI ES CUALQUIER OTRA COSA: Usamos 'form-control'
            else:
                field.widget.attrs.update({'class': 'form-control'})

# --- 2. FORMULARIOS ---

class PacienteForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Paciente
        fields = '__all__'
        widgets = {
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }

class ObraSocialForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ObraSocial
        fields = '__all__'

class TipoTratamientoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = TipoTratamiento
        fields = '__all__'
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 2}),
        }

class TurnoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Turno
        # AGREGUÉ 'pagado' A ESTA LISTA (Antes no estaba)
        fields = ['fecha', 'hora', 'paciente', 'tratamiento', 'obra_social_aplicada', 'monto_paciente', 'monto_pagado', 'metodo_pago', 'estado', 'nota_evolucion', 'pagado']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.TimeInput(attrs={'type': 'time'}),
            'nota_evolucion': forms.Textarea(attrs={'rows': 3}),
            'pagado': forms.CheckboxInput(attrs={'class': 'form-check-input'}), # Refuerzo visual
        }
        help_texts = {
            'monto_paciente': 'Dejar en 0 para que el sistema calcule el precio automático según el Arancel.',
            'obra_social_aplicada': 'Seleccioná con qué obra social se atiende HOY.'
        }
    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')

        # Si faltan datos, no validamos nada (deja que el error por defecto salte)
        if not fecha or not hora:
            return cleaned_data

        # BUSCAMOS COINCIDENCIAS
        # "Buscame turnos en esa fecha y hora, que NO estén cancelados"
        coincidencias = Turno.objects.filter(
            fecha=fecha, 
            hora=hora
        ).exclude(estado='CANCELADO')

        # Excepción: Si estoy EDITANDO un turno, no me tengo que chocar conmigo mismo.
        if self.instance.pk:
            coincidencias = coincidencias.exclude(pk=self.instance.pk)

        # SI ENCONTRÓ ALGO... ERROR.
        if coincidencias.exists():
            # Esto hace que el formulario falle y muestre el mensaje rojo
            raise forms.ValidationError("⚠️ ¡Cuidado! Ya existe un turno activo en ese horario.")
        
        return cleaned_data
    
class GastoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Gasto
        fields = '__all__'
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }

class LiquidacionForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = LiquidacionObraSocial
        fields = '__all__'
        widgets = {
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date'}),
        }

class ArancelForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Arancel
        fields = '__all__'

class CategoriaGastoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = CategoriaGasto
        fields = '__all__'
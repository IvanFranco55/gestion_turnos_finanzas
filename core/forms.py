from django import forms
from .models import Paciente, ObraSocial, TipoTratamiento, Turno, Gasto, LiquidacionObraSocial, Arancel, CategoriaGasto

class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

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

# --- ACÁ ESTÁ EL PRIMER ARREGLO (TURNOS) ---
class TurnoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Turno
        # Incluimos 'pagado' para que pueda tildarlo al editar
        fields = ['fecha', 'hora', 'paciente', 'tratamiento', 'obra_social_aplicada', 
                  'monto_paciente', 'monto_pagado', 'metodo_pago', 'nota_evolucion', 'pagado']
        
        widgets = {
            # FORMATO CORRECTO PARA QUE NO SE BORRE LA FECHA
            'fecha': forms.DateInput(
                format='%Y-%m-%d', 
                attrs={'type': 'date'}
            ),
            # FORMATO CORRECTO PARA QUE NO SE BORRE LA HORA
            'hora': forms.TimeInput(
                format='%H:%M', 
                attrs={'type': 'time'}
            ),
            'nota_evolucion': forms.Textarea(attrs={'rows': 3}),
            'pagado': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'width: 20px; height: 20px;'}),
        }
        help_texts = {
            'monto_paciente': 'Dejar en 0 para que el sistema calcule el precio automático según el Arancel.',
            'obra_social_aplicada': 'Seleccioná con qué obra social se atiende HOY.',
            'pagado': 'Marcar si canceló el TOTAL de la deuda.'
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')

        if not fecha or not hora:
            return cleaned_data

        coincidencias = Turno.objects.filter(
            fecha=fecha, 
            hora=hora
        ).exclude(estado='CANCELADO')

        if self.instance.pk:
            coincidencias = coincidencias.exclude(pk=self.instance.pk)

        if coincidencias.exists():
            raise forms.ValidationError("⚠️ ¡Cuidado! Ya existe un turno activo en ese horario.")
        
        return cleaned_data

# --- ACÁ ESTÁ EL SEGUNDO ARREGLO (GASTOS) ---
class GastoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Gasto
        fields = '__all__'
        widgets = {
            # FORMATO CORRECTO APLICADO AQUI TAMBIEN
            'fecha': forms.DateInput(
                format='%Y-%m-%d', 
                attrs={'type': 'date'}
            ),
        }

# --- ACÁ ESTÁ EL TERCER ARREGLO (LIQUIDACIONES) ---
class LiquidacionForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = LiquidacionObraSocial
        fields = '__all__'
        widgets = {
            # FORMATO CORRECTO APLICADO AQUI TAMBIEN
            'fecha_ingreso': forms.DateInput(
                format='%Y-%m-%d', 
                attrs={'type': 'date'}
            ),
        }

class ArancelForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Arancel
        fields = '__all__'

class CategoriaGastoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = CategoriaGasto
        fields = '__all__'
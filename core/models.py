from django.db import models
from django.utils import timezone

class ObraSocial(models.Model):
    nombre = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = "Obras Sociales"

    def __str__(self):
        return self.nombre

class TipoTratamiento(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.nombre

class Arancel(models.Model):
    """
    Define cuánto paga el paciente (Copago) para cada combinación.
    """
    obra_social = models.ForeignKey(ObraSocial, on_delete=models.CASCADE)
    tratamiento = models.ForeignKey(TipoTratamiento, on_delete=models.CASCADE)
    copago_sugerido = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = ('obra_social', 'tratamiento')
        verbose_name_plural = "Aranceles (Precios)"

    def __str__(self):
        return f"{self.obra_social} - {self.tratamiento}: ${self.copago_sugerido}"

class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    obra_social_default = models.ForeignKey(ObraSocial, on_delete=models.SET_NULL, null=True, blank=True)
    observaciones = models.TextField(blank=True, null=True)
    
    def __str__(self):
        os_nombre = self.obra_social_default.nombre if self.obra_social_default else "Particular"
        return f"{self.apellido}, {self.nombre} - ({os_nombre})"

class Turno(models.Model):
    ESTADOS = [
        ('PENDIENTE', '⏳ Pendiente'),
        ('FINALIZADO', '✅ Atendido'),
        ('CANCELADO', '🚫 Cancelado'),
    ]
    METODOS_PAGO = [('EFECTIVO', 'Efectivo'), ('TRANSFERENCIA', 'Transferencia/MP')]

    fecha = models.DateField(default=timezone.now)
    hora = models.TimeField()
    paciente = models.ForeignKey('Paciente', on_delete=models.PROTECT)
    tratamiento = models.ForeignKey('TipoTratamiento', on_delete=models.PROTECT)
    obra_social_aplicada = models.ForeignKey('ObraSocial', on_delete=models.PROTECT)
    
    monto_paciente = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pagado = models.BooleanField(default=False)
    
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    nota_evolucion = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-fecha', '-hora']

    @property
    def saldo_pendiente(self):
        return self.monto_paciente - self.monto_pagado

    def save(self, *args, **kwargs):
        if not self.id and self.monto_paciente == 0:
            try:
                arancel = Arancel.objects.get(
                    obra_social=self.obra_social_aplicada, 
                    tratamiento=self.tratamiento
                )
                self.monto_paciente = arancel.copago_sugerido
            except Arancel.DoesNotExist:
                pass 

        if self.pagado and self.monto_pagado < self.monto_paciente:
            self.monto_pagado = self.monto_paciente

        if self.monto_paciente > 0 and self.monto_pagado >= self.monto_paciente:
            self.pagado = True

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.fecha} - {self.paciente}"

class LiquidacionObraSocial(models.Model):
    fecha_ingreso = models.DateField(default=timezone.now)
    obra_social = models.ForeignKey(ObraSocial, on_delete=models.PROTECT)
    periodo = models.CharField(max_length=100) # Ej: "Marzo 2026"
    monto_total = models.DecimalField(max_digits=12, decimal_places=2)
    comprobante = models.FileField(upload_to='liquidaciones/', blank=True, null=True)

class CategoriaGasto(models.Model):
    nombre = models.CharField(max_length=50)
    def __str__(self): return self.nombre

class Gasto(models.Model):
    fecha = models.DateField(default=timezone.now)
    categoria = models.ForeignKey(CategoriaGasto, on_delete=models.PROTECT)
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import datetime

from .models import (
    Paciente, ObraSocial, TipoTratamiento, Arancel, 
    Turno, Gasto, LiquidacionObraSocial, CategoriaGasto
)

class SistemaOdontologiaTest(TestCase):

    def setUp(self):
        """
        Esta función corre ANTES de cada prueba. 
        Prepara el escenario (crea usuario, paciente, obra social, etc).
        """
        # 1. Creamos un usuario para poder loguearnos (porque tus vistas tienen @login_required)
        self.user = User.objects.create_user(username='admin', password='123')
        self.client.login(username='admin', password='123')

        # 2. Datos básicos
        self.osde = ObraSocial.objects.create(nombre="OSDE")
        self.trat_conducto = TipoTratamiento.objects.create(nombre="Conducto", descripcion="Tratamiento raiz")
        self.categoria_luz = CategoriaGasto.objects.create(nombre="Luz")

        # 3. Configuramos un precio (Arancel)
        # OSDE paga Conducto -> $10.000
        self.arancel = Arancel.objects.create(
            obra_social=self.osde,
            tratamiento=self.trat_conducto,
            copago_sugerido=10000
        )

        # 4. Un paciente
        self.paciente = Paciente.objects.create(
            nombre="Lionel", apellido="Messi", dni="101010", 
            obra_social_default=self.osde
        )

    # ==========================================
    # 1. PRUEBAS DE LÓGICA AUTOMÁTICA (MODELOS)
    # ==========================================

    def test_turno_toma_precio_arancel_automaticamente(self):
        """Si creo un turno con precio 0, debe tomar el precio del Arancel ($10.000)"""
        turno = Turno.objects.create(
            paciente=self.paciente,
            tratamiento=self.trat_conducto,
            obra_social_aplicada=self.osde,
            hora=datetime.time(10, 0),
            monto_paciente=0 # Lo dejo en 0 adrede
        )
        # Verificamos que se haya actualizado solo
        self.assertEqual(turno.monto_paciente, 10000)

    def test_calculo_saldo_pendiente(self):
        """Si sale 10.000 y paga 3.000, debe deber 7.000"""
        turno = Turno.objects.create(
            paciente=self.paciente,
            tratamiento=self.trat_conducto,
            obra_social_aplicada=self.osde,
            hora=datetime.time(10, 0),
            monto_paciente=10000,
            monto_pagado=3000
        )
        self.assertEqual(turno.saldo_pendiente, 7000)
        self.assertFalse(turno.pagado) # No debería estar pagado

    def test_se_marca_pagado_automaticamente(self):
        """Si pago el total, el check de 'pagado' debe ponerse True solo"""
        turno = Turno.objects.create(
            paciente=self.paciente,
            tratamiento=self.trat_conducto,
            obra_social_aplicada=self.osde,
            hora=datetime.time(10, 0),
            monto_paciente=10000,
            monto_pagado=10000 # Pago total
        )
        self.assertTrue(turno.pagado)

    # ==========================================
    # 2. PRUEBAS DE FINANZAS (BALANCE)
    # ==========================================

    def test_calculo_balance_general(self):
        """
        Prueba Integral:
        + Ingreso Consultorio: $5.000
        + Ingreso Banco (OS): $20.000
        - Gasto Luz: $1.000
        -----------------------------
        RESULTADO ESPERADO: $24.000
        """
        # 1. Turno cobrado
        Turno.objects.create(
            paciente=self.paciente, tratamiento=self.trat_conducto, obra_social_aplicada=self.osde,
            hora=datetime.time(9,0), monto_paciente=5000, monto_pagado=5000, pagado=True,
            fecha=timezone.now()
        )
        # 2. Liquidación Banco
        LiquidacionObraSocial.objects.create(
            obra_social=self.osde, periodo="Enero", monto_total=20000,
            fecha_ingreso=timezone.now()
        )
        # 3. Gasto
        Gasto.objects.create(
            categoria=self.categoria_luz, monto=1000, fecha=timezone.now()
        )

        # Hacemos la petición a la vista de balance
        response = self.client.get(reverse('balance'))
        
        # Verificamos el contexto (lo que le llega al HTML)
        self.assertEqual(response.context['ingresos_turnos'], 5000)
        self.assertEqual(response.context['ingresos_os'], 20000)
        self.assertEqual(response.context['egresos'], 1000)
        self.assertEqual(response.context['resultado'], 24000)

    # ==========================================
    # 3. PRUEBAS DE DEUDORES Y PAGOS PARCIALES
    # ==========================================

    def test_reporte_deudores_filtra_correctamente(self):
        """El reporte solo debe mostrar gente que debe plata Y ya fue atendida"""
        # Caso 1: Debe plata y está finalizado (DEBERÍA APARECER)
        t1 = Turno.objects.create(
            paciente=self.paciente, tratamiento=self.trat_conducto, obra_social_aplicada=self.osde,
            hora=datetime.time(9,0), monto_paciente=10000, monto_pagado=0, 
            estado='FINALIZADO', pagado=False
        )
        
        # Caso 2: Debe plata pero es futuro/pendiente (NO DEBERÍA APARECER)
        t2 = Turno.objects.create(
            paciente=self.paciente, tratamiento=self.trat_conducto, obra_social_aplicada=self.osde,
            hora=datetime.time(10,0), monto_paciente=10000, monto_pagado=0, 
            estado='PENDIENTE', pagado=False
        )

        response = self.client.get(reverse('reporte_deudores'))
        
        # Verificamos que t1 esté y t2 no
        self.assertIn(t1, response.context['turnos'])
        self.assertNotIn(t2, response.context['turnos'])

    def test_registrar_pago_parcial(self):
        """Probamos el botón de 'Registrar Pago' en la lista de deudores"""
        # Turno que debe 10.000
        turno = Turno.objects.create(
            paciente=self.paciente, tratamiento=self.trat_conducto, obra_social_aplicada=self.osde,
            hora=datetime.time(9,0), monto_paciente=10000, monto_pagado=0, 
            estado='FINALIZADO', pagado=False
        )

        # Simulamos que el usuario escribe "4000" en el modal y guarda
        url = reverse('registrar_pago_deuda', args=[turno.pk])
        self.client.post(url, {'monto_abonado': '4000'})

        # Recargamos el turno de la base de datos
        turno.refresh_from_db()

        # Ahora debe haber pagado 4000 y deber 6000
        self.assertEqual(turno.monto_pagado, 4000)
        self.assertEqual(turno.saldo_pendiente, 6000)
        self.assertFalse(turno.pagado) # Sigue debiendo

        # Pagamos el resto (6000)
        self.client.post(url, {'monto_abonado': '6000'})
        turno.refresh_from_db()
        
        # Ahora debe estar saldado
        self.assertTrue(turno.pagado)
        self.assertEqual(turno.saldo_pendiente, 0)

    # ==========================================
    # 4. PRUEBAS DE BOTONES MÁGICOS (TOGGLES)
    # ==========================================

    def test_toggle_pagado_funciona(self):
        """El botón mágico '$' debe poner el pago completo automáticamente"""
        turno = Turno.objects.create(
            paciente=self.paciente, tratamiento=self.trat_conducto, obra_social_aplicada=self.osde,
            hora=datetime.time(9,0), monto_paciente=5000, monto_pagado=0, pagado=False
        )

        # Clic en el botón
        self.client.get(reverse('toggle_pagado', args=[turno.pk]))
        
        turno.refresh_from_db()
        self.assertTrue(turno.pagado)
        self.assertEqual(turno.monto_pagado, 5000) # Se autocompletó

        # Clic de nuevo (Deshacer)
        self.client.get(reverse('toggle_pagado', args=[turno.pk]))
        
        turno.refresh_from_db()
        self.assertFalse(turno.pagado)
        self.assertEqual(turno.monto_pagado, 0) # Volvió a 0
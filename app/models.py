from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import math  

# CLASIFICACIÓN DE ESPACIOS 
class TipoEspacio(models.Model):
    nombre = models.CharField(max_length=50)
    tarifa_por_hora = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.nombre} - ${self.tarifa_por_hora}/hr"

#  INVENTARIO DE ESPACIOS 
class Espacio(models.Model):
    OPCIONES_ZONA = [
        ('BALBUENA', 'Balbuena'),
        ('MOCTEZUMA', 'Moctezuma'),
        ('AEROPUERTO', 'Aeropuerto'),
    ]
    identificador = models.CharField(max_length=10)
    zona = models.CharField(max_length=20, choices=OPCIONES_ZONA, default='BALBUENA')
    tipo = models.ForeignKey(TipoEspacio, on_delete=models.PROTECT)
    ocupado = models.BooleanField(default=False)

    def __str__(self):
        estado = "Ocupado" if self.ocupado else "Disponible"
        return f"{self.zona}: {self.identificador} ({estado})"

# REGISTRO DE ENTRADA/SALIDA 
class Registro(models.Model):
    espacio = models.ForeignKey(Espacio, on_delete=models.PROTECT)
    matricula = models.CharField(max_length=20)
    hora_entrada = models.DateTimeField(default=timezone.now)
    hora_salida = models.DateTimeField(null=True, blank=True)
    monto_pagado = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    pagado = models.BooleanField(default=False)

    #  Lógica centralizada de cobro 
    def calcular_costo_actual(self):
        """
        Calcula el tiempo transcurrido y el costo total hasta el momento.
        Retorna una tupla: (horas_totales, costo_total)
        """
        
        if self.pagado and self.monto_pagado:
        
            tiempo_total = self.hora_salida - self.hora_entrada
            horas = math.ceil(tiempo_total.total_seconds() / 3600) or 1
            return horas, float(self.monto_pagado)

        
        tiempo_fin = self.hora_salida if self.hora_salida else timezone.now()
        duracion = tiempo_fin - self.hora_entrada
        
        #  Fracción de hora sube a la siguiente hora
        horas = math.ceil(duracion.total_seconds() / 3600) or 1
        
        #  tarifa  de espacio asociado
        tarifa = float(self.espacio.tipo.tarifa_por_hora)
        total = horas * tarifa
        
        return horas, total

    def __str__(self):
        return f"{self.matricula} - {self.espacio}"

#PERFIL DE CLIENTE 
class Cliente(models.Model):
    
    OPCIONES_VEHICULO = [
        ('Automovil', 'Automóvil'),   
        ('Camioneta', 'Camioneta'),
        ('Motocicleta', 'Motocicleta'), 
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    nombre = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    placas = models.CharField(max_length=20, blank=True, null=True)
    
    tipo_vehiculo = models.CharField(
        max_length=50, 
        choices=OPCIONES_VEHICULO, 
        blank=True, 
        null=True
    )

    def __str__(self):
        return f"Cliente: {self.user.username}"

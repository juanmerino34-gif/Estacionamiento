from django.shortcuts import render, redirect
from .models import Espacio, Registro, TipoEspacio, Cliente
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import csv 
from django.http import HttpResponse, FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


def inicio(request):
    mensaje = None 
    datos_cliente = None 

    
    if request.method == 'POST':
        placas_recibidas = request.POST.get('placas')
        tipo_seleccionado = request.POST.get('tipo_vehiculo')
        try:
            tipo_obj = TipoEspacio.objects.get(nombre=tipo_seleccionado)
            espacio_disponible = Espacio.objects.filter(tipo=tipo_obj, ocupado=False).first()
            if espacio_disponible:
                Registro.objects.create(
                    espacio=espacio_disponible,
                    matricula=placas_recibidas,
                    hora_entrada=timezone.now()
                )
                espacio_disponible.ocupado = True
                espacio_disponible.save()
                mensaje = f"✅ ¡Bienvenido! Tu lugar asignado es: {espacio_disponible.zona} - {espacio_disponible.identificador}"
            else:
                mensaje = f"❌ Lo sentimos, no hay espacios disponibles para {tipo_seleccionado}."
        except TipoEspacio.DoesNotExist:
            mensaje = "⚠️ Error: El tipo de vehículo no existe."
        except Exception as e:
            mensaje = f"⚠️ Error inesperado: {str(e)}"

    
    if request.user.is_authenticated:
        try:
            
            cliente = Cliente.objects.get(user=request.user)
            
            
            registro_activo = Registro.objects.filter(matricula=cliente.placas, hora_salida__isnull=True).first()
            
            if registro_activo:
                
                horas, total = registro_activo.calcular_costo_actual()
               
                
                datos_cliente = {
                    'nombre': cliente.nombre or request.user.first_name,
                    'placa': cliente.placas,
                    'zona': registro_activo.espacio.zona,
                    'espacio': registro_activo.espacio.identificador,
                    'entrada': registro_activo.hora_entrada,
                    'horas_transcurridas': horas,
                    'tarifa': registro_activo.espacio.tipo.tarifa_por_hora,
                    'total_actual': total
                }
            else:
                
                datos_cliente = {
                    'nombre': cliente.nombre or request.user.first_name,
                    'estado': 'inactivo'
                }
        except Cliente.DoesNotExist:
            pass 

    
    hay_balbuena = Espacio.objects.filter(zona='BALBUENA', ocupado=False).exists()
    hay_moctezuma = Espacio.objects.filter(zona='MOCTEZUMA', ocupado=False).exists()
    hay_aeropuerto = Espacio.objects.filter(zona='AEROPUERTO', ocupado=False).exists()

    contexto = {
        'balbuena_libre': hay_balbuena, 
        'moctezuma_libre': hay_moctezuma, 
        'aeropuerto_libre': hay_aeropuerto, 
        'mensaje': mensaje,
        'datos_cliente': datos_cliente
    }
    return render(request, 'index.html', contexto)

# LOGIN CAJA 
def login_caja(request):
    mensaje = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(username=user_obj.username, password=password)
            if user and user.is_superuser: 
                login(request, user)
                return redirect('home') 
            else:
                mensaje = "⚠️ Acceso denegado."
        except User.DoesNotExist:
            mensaje = "⚠️ Usuario no encontrado."
    return render(request, 'login_caja.html', {'mensaje': mensaje})

#  COBRAR 
@login_required(login_url='login_caja') 
def cobrar(request):
    if not request.user.is_superuser: return redirect('login_caja')
    mensaje, datos_pago = None, None

    if request.method == 'POST':
        if 'buscar_placa' in request.POST:
            placa = request.POST.get('placa_buscar')
            registro = Registro.objects.filter(matricula=placa, hora_salida__isnull=True).first()
            if registro:
                
                horas, total = registro.calcular_costo_actual()
               
                
                datos_pago = {
                    'registro_id': registro.id, 
                    'placa': registro.matricula, 
                    'zona': registro.espacio.zona, 
                    'espacio': registro.espacio.identificador, 
                    'entrada': registro.hora_entrada, 
                    'salida': timezone.now(), 
                    'horas': horas, 
                    'tarifa': registro.espacio.tipo.tarifa_por_hora, 
                    'total': total
                }
            else:
                mensaje = "⚠️ Vehículo no encontrado."
        elif 'confirmar_pago' in request.POST:
            reg = Registro.objects.get(id=request.POST.get('registro_id'))
            reg.hora_salida = timezone.now()
            reg.monto_pagado = request.POST.get('total_pagar')
            reg.pagado = True
            reg.save()
            reg.espacio.ocupado = False
            reg.espacio.save()
            mensaje = f"💰 Cobro exitoso."
    return render(request, 'cobrar.html', {'mensaje': mensaje, 'datos': datos_pago})

# CLIENTES CON VALIDACIÓN DE DUPLICADOS
def registro_cliente(request):
    mensaje = None 
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        
        usuario_ingresado = request.POST.get('username')
        placas_ingresadas = request.POST.get('placas')

        if Cliente.objects.filter(placas=placas_ingresadas).exists():
            mensaje = f"❌ Error: Las placas {placas_ingresadas} ya están registradas en el sistema."
        
        elif User.objects.filter(username=usuario_ingresado).exists():
             mensaje = f"❌ Error: El usuario '{usuario_ingresado}' ya existe. Intenta con otro."

        elif form.is_valid():
            user = form.save()
            Cliente.objects.create(
                user=user,
                nombre=request.POST.get('nombre'),
                telefono=request.POST.get('telefono'),
                placas=placas_ingresadas,
                tipo_vehiculo=request.POST.get('tipo_vehiculo')
            )
            login(request, user)
            return redirect('home')
        
        else:
            mensaje = "❌ Error en el formulario. Revisa que las contraseñas coincidan."

    else:
        form = UserCreationForm()
    
    return render(request, 'registro.html', {'form': form, 'mensaje': mensaje})

def login_cliente(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login_cliente.html', {'form': form})

# PERFIL CON HISTORIAL
@login_required
def perfil_cliente(request):
    user = request.user
    cliente, created = Cliente.objects.get_or_create(user=user)

    
    if cliente.placas:
        historial = Registro.objects.filter(matricula=cliente.placas).order_by('-hora_entrada')
    else:
        historial = []

    mensaje = None
    if request.method == 'POST':
        if 'actualizar' in request.POST:
            user.first_name = request.POST.get('nombre')
            user.email = request.POST.get('email')
            user.save()
            
            cliente.nombre = request.POST.get('nombre')
            cliente.telefono = request.POST.get('telefono')
            cliente.placas = request.POST.get('placas')
            cliente.tipo_vehiculo = request.POST.get('tipo_vehiculo')
            cliente.save()
            
            
            if cliente.placas:
                historial = Registro.objects.filter(matricula=cliente.placas).order_by('-hora_entrada')
            
            mensaje = "✅ Datos actualizados."
        elif 'eliminar' in request.POST:
            user.delete()
            return redirect('home')

    return render(request, 'perfil.html', {
        'user': user, 
        'cliente': cliente, 
        'mensaje': mensaje,
        'historial': historial  
    })

def cerrar_sesion(request):
    logout(request)
    return redirect('home')

#  REPORTES (PDF Y EXCEL) 
@login_required(login_url='login_caja')
def reporte_pdf(request):
    if not request.user.is_superuser: return redirect('login_caja')

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "Reporte de Ingresos - Estacionamiento")
    p.setFont("Helvetica", 10)
    p.drawString(100, 735, f"Generado el: {timezone.now().strftime('%d/%m/%Y %H:%M')}")

    y = 700
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y, "Placa")
    p.drawString(150, y, "Entrada")
    p.drawString(300, y, "Salida")
    p.drawString(450, y, "Monto")
    p.line(50, y-5, 500, y-5)
    y -= 25

    registros = Registro.objects.all().order_by('-hora_entrada')[:50]
    total_ingresos = 0

    p.setFont("Helvetica", 9)
    for reg in registros:
        if y < 50:
            p.showPage()
            y = 750
        
        entrada = reg.hora_entrada.strftime("%d/%m %H:%M")
        salida = reg.hora_salida.strftime("%d/%m %H:%M") if reg.hora_salida else "EN CURSO"
        monto = f"${reg.monto_pagado}" if reg.monto_pagado else "-"
        
        if reg.monto_pagado:
            try:
                total_ingresos += float(reg.monto_pagado)
            except:
                pass

        p.drawString(50, y, str(reg.matricula))
        p.drawString(150, y, entrada)
        p.drawString(300, y, salida)
        p.drawString(450, y, monto)
        y -= 20

    p.line(50, y+15, 500, y+15)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(300, y-10, f"TOTAL RECAUDADO: ${total_ingresos}")

    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='reporte_estacionamiento.pdf')

@login_required(login_url='login_caja')
def reporte_excel(request):
    if not request.user.is_superuser: return redirect('login_caja')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="historial_vehiculos.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Matricula', 'Zona', 'Entrada', 'Salida', 'Monto Pagado', 'Estado'])

    registros = Registro.objects.all().order_by('-hora_entrada')

    for reg in registros:
        estado = "Pagado" if reg.pagado else "Pendiente"
        zona = reg.espacio.zona if reg.espacio else "N/A"
        writer.writerow([
            reg.id,
            reg.matricula,
            zona,
            reg.hora_entrada,
            reg.hora_salida,
            reg.monto_pagado,
            estado
        ])

    return response

from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name='home'),
    path('cobrar/', views.cobrar, name='cobrar'),
    path('login_caja/', views.login_caja, name='login_caja'),
    
    # RUTAS PARA CLIENTES
    path('registro/', views.registro_cliente, name='registro'),
    path('login/', views.login_cliente, name='login_cliente'),
    path('perfil/', views.perfil_cliente, name='perfil'),
    path('logout/', views.cerrar_sesion, name='logout'),

    # RUTAS PARA REPORTES 
    path('reporte/pdf/', views.reporte_pdf, name='reporte_pdf'),
    path('reporte/excel/', views.reporte_excel, name='reporte_excel'),
]
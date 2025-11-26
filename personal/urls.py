from django.urls import path
from . import views
from .views import (
    inicio,
    gestion_horas,
    carga_horas,
    dashboard,
    reporte_cumplimiento,
    estadisticas
)

urlpatterns = [
    path('inicio/', inicio, name='inicio'),
    path('gestion-horas/', gestion_horas, name='gestion_horas'),
    path('carga-horas/', carga_horas, name='carga_horas'),
    path('dashboard/', dashboard, name='dashboard'),
    path('reporte/', reporte_cumplimiento, name='reporte_cumplimiento'),
    path('estadisticas/', estadisticas, name='estadisticas'),
    path('test/', views.test_view, name='test'),

]

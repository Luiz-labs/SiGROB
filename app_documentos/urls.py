from django.urls import path
from . import views

urlpatterns = [
  path('', views.lista_documentos, name='documentos_lista'),
  path('subir/', views.subir_documento, name='documentos_subir'),
  path('<int:pk>/', views.detalle_documento, name='documentos_detalle'),
  path('<int:pk>/revisar/', views.revisar_documento, name='documentos_revisar'),
]

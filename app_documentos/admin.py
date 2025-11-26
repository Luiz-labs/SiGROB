from django.contrib import admin
from .models import Documento

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
  list_display = ('usuario', 'titulo', 'tipo', 'estado', 'fecha_subida', 'fecha_revision')
  list_filter = ('tipo', 'estado', 'fecha_subida')
  search_fields = ('usuario__username', 'titulo', 'descripcion')

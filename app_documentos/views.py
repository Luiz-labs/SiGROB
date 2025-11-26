from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.db.models import Count
from .models import Documento
from .forms import DocumentoForm

@login_required
def lista_documentos(request):
  qs = Documento.objects.filter(usuario=request.user)
  # Resumen por estado para el usuario
  resumen_estado = qs.values('estado').annotate(total=Count('id'))
  # Conteos rápidos
  counts = {
    'pendientes': qs.filter(estado='PENDIENTE').count(),
    'observados': qs.filter(estado='OBSERVADO').count(),
    'aprobados': qs.filter(estado='APROBADO').count(),
    'total': qs.count(),
  }
  return render(request, 'documentos/lista.html', {
    'documentos': qs,
    'resumen_estado': resumen_estado,
    'counts': counts
  })

@login_required
def subir_documento(request):
  if request.method == 'POST':
    form = DocumentoForm(request.POST, request.FILES)
    if form.is_valid():
      doc = form.save(commit=False)
      doc.usuario = request.user
      doc.save()
      messages.success(request, "Documento cargado correctamente. Estado: Pendiente.")
      return redirect('documentos_lista')
  else:
    form = DocumentoForm()
  return render(request, 'documentos/subir.html', {'form': form})

@login_required
def detalle_documento(request, pk):
  doc = get_object_or_404(Documento, pk=pk)
  if doc.usuario != request.user and not request.user.has_perm('app_documentos.change_documento'):
    messages.error(request, "No tienes permiso para ver este documento.")
    return redirect('documentos_lista')
  return render(request, 'documentos/detalle.html', {'doc': doc})

@permission_required('app_documentos.change_documento', raise_exception=True)
def revisar_documento(request, pk):
  doc = get_object_or_404(Documento, pk=pk)
  if request.method == 'POST':
    estado = request.POST.get('estado')
    if estado in dict(Documento.ESTADO_CHOICES):
      doc.estado = estado
      doc.fecha_revision = timezone.now()
      doc.save()
      messages.success(request, "Estado actualizado.")
      return redirect('documentos_detalle', pk=doc.pk)
  return render(request, 'documentos/revisar.html', {'doc': doc})

def revisar_documento(request, pk):
    documento = get_object_or_404(Documento, pk=pk)
    return render(request, 'documentos/revisar.html', {'documento': documento})

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.db.models import Count
from .models import Documento
from .forms import DocumentoForm

# Google Drive OAuth
from .oauth_drive import get_drive_service_oauth
from googleapiclient.http import MediaFileUpload
import os

# ==== IDS DE CARPETAS DRIVE ====
FOLDER_RECIBIDOS = "1Jo-9AtRBt97A9Pr223GR6FkP9FtnmXbj"
FOLDER_CLASIFICADOS = "17smBWbsSlTd5pxBz-3pVyca3f-0u2Usy"
FOLDER_VENCIDOS = "1nqp2aECZr2ewC8qnh-OOu-kMrTZW0qPQ"
FOLDER_HISTORICO = "1oQMPZ4MGCk4ESl0KLrJvxcZXYFSEekYv"


@login_required
def lista_documentos(request):
    qs = Documento.objects.filter(usuario=request.user)

    resumen_estado = qs.values('estado').annotate(total=Count('id'))

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

            try:
                service = get_drive_service_oauth()

                ruta_archivo = doc.archivo.path
                nombre_archivo = os.path.basename(ruta_archivo)

                file_metadata = {
                    'name': nombre_archivo,
                    'parents': [FOLDER_RECIBIDOS]
                }

                media = MediaFileUpload(ruta_archivo, resumable=True)

                archivo_drive = service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()

                doc.drive_id = archivo_drive.get('id')
                doc.save()

                messages.success(request, "Documento subido a Google Drive correctamente.")

            except Exception as e:
                print("ERROR DRIVE:", e)
                messages.warning(
                    request,
                    "Documento guardado localmente, pero falló la subida a Drive."
                )

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

            try:
                if doc.drive_id:
                    service = get_drive_service_oauth()

                    if estado == 'PENDIENTE':
                        folder_destino = FOLDER_RECIBIDOS
                    elif estado == 'APROBADO':
                        folder_destino = FOLDER_CLASIFICADOS
                    elif estado == 'OBSERVADO':
                        folder_destino = FOLDER_VENCIDOS
                    else:
                        folder_destino = FOLDER_HISTORICO

                    archivo = service.files().get(
                        fileId=doc.drive_id,
                        fields='parents'
                    ).execute()

                    prev_parents = archivo.get('parents')
                    if prev_parents:
                      prev_parents = ",".join(prev_parents)
                    else:
                      prev_parents = ""

                    service.files().update(
                        fileId=doc.drive_id,
                        addParents=folder_destino,
                        removeParents=prev_parents,
                        supportsAllDrives=True,
                        fields='id, parents'
                    ).execute()

            except Exception as e:
                print("ERROR MOVIENDO DRIVE:", e)

            messages.success(request, "Estado actualizado y archivo organizado en Drive.")
            return redirect('documentos_detalle', pk=doc.pk)

    return render(request, 'documentos/revisar.html', {'doc': doc})
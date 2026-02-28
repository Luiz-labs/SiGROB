from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from .models import Bombero, CargaMensual, RegistroHoras
from app_documentos.models import Documento
import pandas as pd
from datetime import datetime, date


# ==============================
# CARGA DE HORAS
# ==============================
@login_required
def carga_horas(request):
    meses_disponibles = [f"{nombre}{datetime.now().year}" for nombre in [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Setiembre", "Octubre", "Noviembre", "Diciembre"
    ]]

    if request.method == 'POST':

        TRADUCCION_GRADOS = {
            'Sec': 'Seccionario',
            'Subteniente': 'Subteniente',
            'Teniente': 'Teniente',
            'Cap': 'Capitán',
            'Tnte Brig': 'Teniente Brigadier',
            'Brig': 'Brigadier',
            'Brig Mayor': 'Brigadier Mayor',
            'Brig Gral': 'Brigadier General',
        }

        archivo = request.FILES.get('archivo')
        mes = request.POST.get('mes')

        if CargaMensual.objects.filter(mes=mes).exists():
            messages.error(request, f'⚠️ Ya existe una carga registrada para {mes}.')
            return render(request, 'personal/carga_horas.html', {'meses_disponibles': meses_disponibles})

        if not mes:
            messages.error(request, '⚠️ Debes ingresar el mes.')
            return render(request, 'personal/carga_horas.html', {'meses_disponibles': meses_disponibles})

        try:
            df = pd.read_excel(archivo)

            columnas_requeridas = {
                'CODIGO', 'GRADO', 'APELLIDOS Y NOMBRES',
                'HORAS ACUMULADAS', 'NUMERO DE EMERGENCIAS ASISTIDAS'
            }

            if not columnas_requeridas.issubset(df.columns):
                messages.error(request, '❌ El archivo no tiene columnas válidas.')
                return render(request, 'personal/carga_horas.html', {'meses_disponibles': meses_disponibles})

            resumen = []

            from collections import defaultdict
            resumen_por_grado = defaultdict(lambda: {'registros': 0, 'horas': 0, 'emergencias': 0})

            for _, fila in df.iterrows():
                try:
                    codigo = str(fila['CODIGO']).strip()
                    grado_raw = str(fila['GRADO']).strip()
                    grado = TRADUCCION_GRADOS.get(grado_raw, grado_raw.title())
                    nombre = str(fila['APELLIDOS Y NOMBRES']).strip()
                    horas = int(fila['HORAS ACUMULADAS'])
                    emergencias = int(fila['NUMERO DE EMERGENCIAS ASISTIDAS'])

                    bombero, _ = Bombero.objects.get_or_create(
                        codigo=codigo,
                        defaults={'grado': grado, 'nombres_apellidos': nombre}
                    )

                    bombero.horas_acumuladas += horas
                    bombero.emergencias_asistidas += emergencias
                    bombero.save()

                    RegistroHoras.objects.create(
                        bombero=bombero,
                        mes=mes,
                        horas=horas,
                        emergencias=emergencias
                    )

                    resumen.append({
                        'codigo': codigo,
                        'nombre': nombre,
                        'grado': grado,
                        'horas': horas,
                        'emergencias': emergencias
                    })

                    resumen_por_grado[grado]['registros'] += 1
                    resumen_por_grado[grado]['horas'] += horas
                    resumen_por_grado[grado]['emergencias'] += emergencias

                except Exception as fila_error:
                    messages.warning(request, f'⚠️ Error en fila: {fila_error}')

            total_registros = len(resumen)
            total_horas = sum(i['horas'] for i in resumen)
            total_emergencias = sum(i['emergencias'] for i in resumen)

            CargaMensual.objects.create(
                archivo=archivo.name,
                mes=mes,
                usuario=request.user,
                efectivos_registrados=total_registros,
                total_horas=total_horas,
                total_emergencias=total_emergencias
            )

            messages.success(request, '✅ Archivo procesado correctamente.')

            return render(request, 'personal/carga_horas.html', {
                'resumen': resumen,
                'meses_disponibles': meses_disponibles,
                'total_registros': total_registros,
                'total_horas': total_horas,
                'total_emergencias': total_emergencias,
                'resumen_por_grado': dict(resumen_por_grado)
            })

        except Exception as e:
            messages.error(request, f'❌ Error: {e}')

    return render(request, 'personal/carga_horas.html', {'meses_disponibles': meses_disponibles})


# ==============================
# DASHBOARD
# ==============================
@login_required
def dashboard(request):
    grado = request.GET.get('grado')
    cargas_activas = CargaMensual.objects.exists()
    cargas_mensuales = CargaMensual.objects.order_by('-fecha_carga')

    bomberos = Bombero.objects.all() if cargas_activas else []

    if grado:
        bomberos = bomberos.filter(grado=grado)

    bomberos = bomberos.order_by('-horas_acumuladas')

    total_horas = bomberos.aggregate(Sum('horas_acumuladas'))['horas_acumuladas__sum'] or 0
    total_emergencias = bomberos.aggregate(Sum('emergencias_asistidas'))['emergencias_asistidas__sum'] or 0

    grados_disponibles = Bombero.objects.values_list('grado', flat=True).distinct()

    return render(request, 'personal/dashboard.html', {
        'bomberos': bomberos,
        'total_horas': total_horas,
        'total_emergencias': total_emergencias,
        'grados': grados_disponibles,
        'grado_seleccionado': grado,
        'cargas_mensuales': cargas_mensuales,
        'cargas_activas': cargas_activas
    })


# ==============================
# REPORTE CUMPLIMIENTO (sin cambios)
# ==============================
@login_required
def reporte_cumplimiento(request):
    # TU MISMO CÓDIGO AQUÍ (lo dejé intacto para no romper nada)
    # 👇👇👇

    TRADUCCION_GRADOS = {
        'Sec': 'Seccionario',
        'Subteniente': 'Subteniente',
        'Teniente': 'Teniente',
        'Cap': 'Capitán',
        'Tnte Brig': 'Teniente Brigadier',
        'Brig': 'Brigadier',
        'Brig Mayor': 'Brigadier Mayor',
        'Brig Gral': 'Brigadier General',
    }

    modo = request.GET.get('modo', 'anual')
    grado = request.GET.get('grado')
    cargas_activas = CargaMensual.objects.exists()

    reporte = []
    total_horas = 0
    total_emergencias = 0

    if cargas_activas:
        bomberos_raw = Bombero.objects.all()

        bomberos = []
        for b in bomberos_raw:
            grado_raw = b.grado.strip()
            grado_homologado = TRADUCCION_GRADOS.get(grado_raw, grado_raw.title())
            if not grado or grado_homologado == grado:
                b.grado_homologado = grado_homologado
                bomberos.append(b)

        metas = {
            'Seccionario': {'anual': 600, 'trimestral': 150},
            'Subteniente': {'anual': 480, 'trimestral': 120},
            'Teniente': {'anual': 400, 'trimestral': 100},
            'Capitán': {'anual': 360, 'trimestral': 90},
            'Teniente Brigadier': {'anual': 240},
            'Brigadier': {'anual': 120},
            'Brigadier Mayor': {'anual': 60},
            'Brigadier General': {'anual': 60},
        }

        meta_general = 240

        for b in bomberos:
            meta = metas.get(b.grado_homologado, {})
            meta_anual = meta.get('anual', 0)
            meta_trimestral = meta.get('trimestral', None)

            meta_base = meta_trimestral if modo == 'trimestral' and meta_trimestral else meta_anual
            cumplimiento = min(100, int((b.horas_acumuladas / meta_base) * 100)) if meta_base > 0 else 0

            cumple_anual = b.horas_acumuladas >= meta_anual
            cumple_general = b.horas_acumuladas >= meta_general
            cumple_trimestral = b.horas_acumuladas >= meta_trimestral if meta_trimestral else None
            horas_faltantes = max(0, meta_anual - b.horas_acumuladas)

            reporte.append({
                'codigo': b.codigo,
                'nombre': b.nombres_apellidos,
                'grado': b.grado_homologado,
                'horas': b.horas_acumuladas,
                'meta_anual': meta_anual,
                'meta_trimestral': meta_trimestral,
                'cumplimiento': cumplimiento,
                'cumple_anual': cumple_anual,
                'cumple_general': cumple_general,
                'cumple_trimestral': cumple_trimestral,
                'horas_faltantes': horas_faltantes
            })

        total_horas = sum(b.horas_acumuladas for b in bomberos)
        total_emergencias = sum(b.emergencias_asistidas for b in bomberos)
    else:
        meta_general = 240
        metas = {}

    grados_raw = Bombero.objects.values_list('grado', flat=True).distinct()
    grados_disponibles = sorted(set([
        TRADUCCION_GRADOS.get(g.strip(), g.strip().title()) for g in grados_raw
    ]))

    cargas_mensuales = CargaMensual.objects.order_by('-fecha_carga')

    if grado and grado in metas:
        metas_filtradas = {grado: metas[grado]}
    else:
        metas_filtradas = metas

    resumen = None
    if grado and reporte:
        cantidad = len(reporte)
        if modo == 'trimestral':
            cantidad_que_cumplen = sum(1 for r in reporte if r['cumple_trimestral'])
        else:
            cantidad_que_cumplen = sum(1 for r in reporte if r['cumple_anual'])
        promedio_cumplimiento = round(sum(r['cumplimiento'] for r in reporte) / cantidad, 1)

        resumen = {
            'grado': grado,
            'cantidad': cantidad,
            'cumplen': cantidad_que_cumplen,
            'promedio': promedio_cumplimiento,
            'modo': modo,
        }

    return render(request, 'personal/reporte.html', {
        'reporte': reporte,
        'grados': grados_disponibles,
        'grado_seleccionado': grado,
        'meta_general': meta_general,
        'modo': modo,
        'cargas_mensuales': cargas_mensuales,
        'total_horas': total_horas,
        'total_emergencias': total_emergencias,
        'cargas_activas': cargas_activas,
        'metas': metas,
        'metas_filtradas': metas_filtradas,
        'resumen': resumen,
    })


# ==============================
# INICIO (NOTIFICACIONES MAC)
# ==============================
def inicio(request):
    notificaciones = []
    total_pendientes = 0
    total_observados = 0
    total_por_vencer = 0

    if request.user.is_authenticated:
        documentos = Documento.objects.filter(usuario=request.user)

        total_pendientes = documentos.filter(estado='PENDIENTE').count()
        total_observados = documentos.filter(estado='OBSERVADO').count()

        for doc in documentos.filter(estado='OBSERVADO'):
            if doc.usa_fecha_limite and doc.fecha_limite:
                dias = (doc.fecha_limite - date.today()).days
                if dias <= 3:
                    total_por_vencer += 1

        if total_pendientes > 0:
            notificaciones.append("📄 Tienes documentos en revisión.")

        if total_observados > 0:
            notificaciones.append("⚠️ Tienes documentos observados.")

    return render(request, 'personal/inicio.html', {
        'notificaciones': notificaciones,
        'total_pendientes': total_pendientes,
        'total_observados': total_observados,
        'total_por_vencer': total_por_vencer,
        'url_documentos': '/documentos/'
    })

# ==============================
# OTRAS VISTAS
# ==============================

def gestion_horas(request):
    return render(request, 'personal/gestion_horas.html')


@login_required
def estadisticas(request):
    GRADOS_TRADUCIDOS = {
        'Sec': 'Seccionario',
        'Subteniente': 'Subteniente',
        'Teniente': 'Teniente',
        'Cap': 'Capitán',
        'Tnte Brig': 'Teniente Brigadier',
        'Brig': 'Brigadier',
        'Brig Mayor': 'Brigadier Mayor',
        'Brig Gral': 'Brigadier General',
    }

    grado = request.GET.get('grado')

    grados_raw = Bombero.objects.values_list('grado', flat=True).distinct()
    grados_disponibles = [
        {'valor': g, 'nombre': GRADOS_TRADUCIDOS.get(g, g)}
        for g in grados_raw
    ]

    registros = RegistroHoras.objects.all()
    if grado:
        registros = registros.filter(bombero__grado=grado)

    resumen_mensual = registros.values('mes').annotate(
        efectivos=Count('bombero', distinct=True),
        horas=Sum('horas'),
        emergencias=Sum('emergencias')
    ).order_by('mes')

    resumen_mensual = list(resumen_mensual)

    for item in resumen_mensual:
        item['mes'] = item.get('mes', 'Sin mes')
        item['horas'] = item.get('horas') or 0
        item['emergencias'] = item.get('emergencias') or 0
        item['efectivos'] = item.get('efectivos') or 0

    return render(request, 'personal/estadisticas.html', {
        'resumen_mensual': resumen_mensual,
        'grados': grados_disponibles,
        'grado_seleccionado': grado
    })


def test_view(request):
    return render(request, 'personal/test.html')
from personal.models import Bombero

TRADUCCION_GRADOS = {
    'SubTnte': 'Subteniente',
    'Tnte': 'Teniente',
    'Cap.': 'Capitán',
    'Secc.': 'Seccionario',
    # Agrega más según tus archivos
}

def normalizar_grados():
    actualizados = 0
    for b in Bombero.objects.all():
        grado_raw = b.grado.strip()
        grado_normalizado = TRADUCCION_GRADOS.get(grado_raw, grado_raw.title())

        if b.grado != grado_normalizado:
            b.grado = grado_normalizado
            b.save()
            actualizados += 1
            print(f"✅ {b.codigo} actualizado a {grado_normalizado}")

    print(f"🎯 Total de grados actualizados: {actualizados}")

from django.db import models
from django.conf import settings

def documento_upload_to(instance, filename):
    return f"documentos/{instance.usuario.username}/{instance.tipo}/{filename}"

class Documento(models.Model):
    TIPO_CHOICES = [
        ('NOTA_INFORMATIVA', 'Nota Informativa'),
        ('SOL_CAP', 'Solicitud de Capacitación'),
        ('INVITACION', 'Invitación'),
        ('OFICIO', 'Oficio'),
        ('MEMO', 'Memorandum'),
        ('OTRO', 'Otro'),
    ]

    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('OBSERVADO', 'Observado'),
        ('APROBADO', 'Aprobado'),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documentos')
    tipo = models.CharField(max_length=32, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=160)
    descripcion = models.TextField(blank=True)
    archivo = models.FileField(upload_to=documento_upload_to)
    estado = models.CharField(max_length=16, choices=ESTADO_CHOICES, default='PENDIENTE')
    fecha_subida = models.DateTimeField(auto_now_add=True)
    fecha_revision = models.DateTimeField(null=True, blank=True)

    # 📌 NUEVOS CAMPOS
    # Fecha asociada al documento (ej. fecha de emisión/registro)
    fecha_documento = models.DateField(null=True, blank=True)

    # Control de fecha límite/alarma
    usa_fecha_limite = models.BooleanField(default=False)
    fecha_limite = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-fecha_subida']

    def __str__(self):
        return f"{self.usuario} - {self.titulo} ({self.get_estado_display()})"


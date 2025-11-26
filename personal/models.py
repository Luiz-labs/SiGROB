from django.db import models

class Bombero(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    grado = models.CharField(max_length=50)
    nombres_apellidos = models.CharField(max_length=150)
    horas_acumuladas = models.PositiveIntegerField(default=0)
    emergencias_asistidas = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.codigo} - {self.nombres_apellidos}"

    def meta_anual(self):
        if self.grado.lower() in ['cap', 'tnte', 'subtnte']:
            return 100
        elif self.grado.lower() == 'brig':
            return 75
        else:
            return 50  # valor por defecto si el grado no está definido

    def horas_restantes(self):
        return max(0, self.meta_anual() - self.horas_acumuladas)

class CargaMensual(models.Model):
    archivo = models.FileField(upload_to='cargas/')
    mes = models.CharField(max_length=20)
    fecha_carga = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    efectivos_registrados = models.IntegerField(default=0)
    total_horas = models.IntegerField(default=0)
    total_emergencias = models.IntegerField(default=0)  # ✅ nuevo campo

    def __str__(self):
        return f"{self.mes} - {self.usuario.username}"

class RegistroAsistencia(models.Model):
    bombero = models.ForeignKey(Bombero, on_delete=models.CASCADE)
    mes = models.CharField(max_length=20)
    horas = models.PositiveIntegerField()
    emergencias = models.PositiveIntegerField()
    fecha_registro = models.DateTimeField(auto_now_add=True)

class RegistroHoras(models.Model):
    bombero = models.ForeignKey(Bombero, on_delete=models.CASCADE)
    mes = models.CharField(max_length=20)
    horas = models.PositiveIntegerField()
    emergencias = models.PositiveIntegerField()
    fecha_carga = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bombero.nombres_apellidos} - {self.mes}"

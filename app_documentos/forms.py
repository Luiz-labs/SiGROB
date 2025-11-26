from django import forms
from .models import Documento

ALLOWED_MIME = ['application/pdf', 'image/jpeg', 'image/png']
MAX_SIZE_MB = 10

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = [
            'tipo',
            'titulo',
            'descripcion',
            'archivo',
            'fecha_documento',   # 📌 nuevo campo: fecha del documento
            'usa_fecha_limite',  # 📌 nuevo campo: checkbox para activar fecha límite
            'fecha_limite',      # 📌 nuevo campo: fecha límite opcional
        ]
        widgets = {
            'fecha_documento': forms.DateInput(attrs={'type': 'date'}),
            'fecha_limite': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_archivo(self):
        f = self.cleaned_data['archivo']
        if f.size > MAX_SIZE_MB * 1024 * 1024:
            raise forms.ValidationError(f"El archivo supera {MAX_SIZE_MB} MB.")
        ct = getattr(f, 'content_type', None)
        if ct and ct not in ALLOWED_MIME:
            raise forms.ValidationError("Formato no permitido. Usa PDF, JPG o PNG.")
        return f


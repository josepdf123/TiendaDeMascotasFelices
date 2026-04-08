from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from PIL import Image

from .models import Producto, Categoria, Perfil, Direccion


TIPOS_PERMITIDOS = {"image/jpeg", "image/png", "image/webp"}
EXTENSIONES_PERMITIDAS = [".jpg", ".jpeg", ".png", ".webp"]
TAMANO_MAXIMO_MB = 3
ANCHO_MINIMO = 180
ALTO_MINIMO = 180


class AdminLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nombre de usuario',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••',
        })
    )


class ProductoForm(forms.ModelForm):
    imagen = forms.ImageField(required=False)

    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'stock', 'imagen', 'categoria', 'activo', 'destacado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre del producto'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Descripción del producto'}),
            'precio': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0.00', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0'}),
            'categoria': forms.Select(attrs={'class': 'form-input'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'destacado': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
        labels = {
            'nombre': 'Nombre del producto',
            'descripcion': 'Descripción',
            'precio': 'Precio (COP)',
            'stock': 'Cantidad en stock',
            'imagen': 'Imagen del producto',
            'categoria': 'Categoría',
            'activo': 'Producto activo (visible en catálogo)',
            'destacado': 'Destacar en inicio',
        }

    def clean_imagen(self):
        imagen = self.cleaned_data.get("imagen")

        if not imagen:
            return self.instance.imagen if self.instance and self.instance.pk else None

        if not hasattr(imagen, "content_type"):
            return imagen

        max_bytes = TAMANO_MAXIMO_MB * 1024 * 1024

        if imagen.size > max_bytes:
            raise ValidationError(f"La imagen supera el tamaño máximo permitido de {TAMANO_MAXIMO_MB} MB.")

        content_type = getattr(imagen, "content_type", None)
        if content_type not in TIPOS_PERMITIDOS:
            raise ValidationError("Formato no permitido. Usa JPG, PNG o WEBP.")

        nombre = imagen.name.lower()
        if not any(nombre.endswith(ext) for ext in EXTENSIONES_PERMITIDAS):
            raise ValidationError("La extensión del archivo no es válida. Usa .jpg, .jpeg, .png o .webp.")

        try:
            img = Image.open(imagen)
            ancho, alto = img.size
            img.verify()
        except Exception:
            raise ValidationError("El archivo subido no es una imagen válida o está corrupto.")

        if ancho < ANCHO_MINIMO or alto < ALTO_MINIMO:
            raise ValidationError(
                f"La imagen debe tener al menos {ANCHO_MINIMO}px de ancho y {ALTO_MINIMO}px de alto."
            )

        imagen.seek(0)
        return imagen
class RegistroForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    identificacion = forms.CharField()
    telefono = forms.CharField()
    direccion = forms.CharField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado")
        return email

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("confirm_password"):
            raise forms.ValidationError("Las contraseñas no coinciden")
        return cleaned_data


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'slug', 'icono', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: Alimentos'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: alimentos'
            }),
            'icono': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: 🍖'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Descripción de la categoría'
            }),
        }
        labels = {
            'nombre': 'Nombre de la categoría',
            'slug': 'Slug (URL amigable)',
            'icono': 'Ícono emoji',
            'descripcion': 'Descripción',
        }
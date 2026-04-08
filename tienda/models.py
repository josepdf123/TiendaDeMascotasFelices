from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from pathlib import Path
import hashlib
import uuid
import os


def producto_image_upload_to(instance, filename):
    ext = Path(filename).suffix.lower() or ".jpg"
    nombre_base = instance.nombre.strip().lower() if instance.nombre else "producto"
    semilla = f"{nombre_base}-{uuid.uuid4().hex}".encode("utf-8")
    nombre_hash = hashlib.sha256(semilla).hexdigest()[:20]
    return f"productos/{nombre_hash}{ext}"


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icono = models.CharField(max_length=10, blank=True, help_text="Emoji para la categoría")
    descripcion = models.TextField(blank=True, null=True)  # ← solo esto se agrega

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to=producto_image_upload_to, blank=True, null=True)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='productos'
    )
    activo = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False, help_text="Mostrar en sección destacada del inicio")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualización = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.nombre

    @property
    def disponible(self):
        return self.stock > 0 and self.activo


# ─── Señales para limpiar imágenes del disco ─────────────────────────────────

@receiver(post_delete, sender=Producto)
def eliminar_imagen_al_borrar(sender, instance, **kwargs):
    """Elimina el archivo de imagen cuando se borra el producto."""
    if instance.imagen:
        if os.path.isfile(instance.imagen.path):
            os.remove(instance.imagen.path)


@receiver(pre_save, sender=Producto)
def eliminar_imagen_al_editar(sender, instance, **kwargs):
    """Elimina la imagen anterior cuando se reemplaza por una nueva."""
    if not instance.pk:
        return
    try:
        imagen_anterior = Producto.objects.get(pk=instance.pk).imagen
    except Producto.DoesNotExist:
        return
    if imagen_anterior and imagen_anterior != instance.imagen:
        if os.path.isfile(imagen_anterior.path):
            os.remove(imagen_anterior.path)

class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    identificacion = models.CharField(max_length=50)
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return self.usuario.username


class Direccion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='direcciones')
    direccion = models.TextField()

    def __str__(self):
        return f"{self.usuario.username} - {self.direccion[:30]}"
    
@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)    

class Pedido(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username} - {self.estado}"
    def get_total(self):
        return sum(d.precio * d.cantidad for d in self.detalles.all())
    
    @property
    def total(self):
        return sum(detalle.subtotal for detalle in self.detalles.all())


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"   
    @property
    def subtotal(self):
        return self.cantidad * self.precio   

 
# ─── HU8: Notificaciones al administrador ────────────────────────────────────

class Notificacion(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='notificaciones')
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ['-fecha']

    def __str__(self):
        return f"Notif. Pedido #{self.pedido.id} — {'leída' if self.leida else 'no leída'}"


@receiver(post_save, sender=Pedido)
def crear_notificacion_nuevo_pedido(sender, instance, created, **kwargs):
    """Crea una notificación automáticamente cuando se genera un nuevo pedido."""
    if created:
        Notificacion.objects.create(pedido=instance)
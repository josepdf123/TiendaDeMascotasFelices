from django.contrib import admin
from .models import Producto, Categoria


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug', 'icono']
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'stock', 'categoria', 'activo', 'destacado', 'fecha_creacion']
    list_filter = ['activo', 'destacado', 'categoria']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['activo', 'destacado', 'stock']



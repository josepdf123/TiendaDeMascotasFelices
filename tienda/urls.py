
from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib import admin
from . import views

urlpatterns = [
    path('django-admin/', admin.site.urls),

    # Catálogo público (HU7)
    path('', views.catalogo, name='catalogo'),
    path('producto/<int:pk>/', views.detalle_producto, name='detalle_producto'),

    # Auth admin (HU1)
    path('admin/login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),

    # Panel admin (HU2, HU3, HU4)
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/producto/nuevo/', views.producto_crear, name='producto_crear'),
    path('admin-panel/producto/<int:pk>/editar/', views.producto_editar, name='producto_editar'),
    path('admin-panel/producto/<int:pk>/eliminar/', views.producto_eliminar, name='producto_eliminar'),

    # Usuarios
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_usuario, name='login'),
    path('perfil/', views.perfil, name='perfil'),

    # Direcciones
    path('agregar-direccion/', views.agregar_direccion, name='agregar_direccion'),
    path('eliminar-direccion/<int:id>/', views.eliminar_direccion, name='eliminar_direccion'),

    # Carrito
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_carrito'),
    path('carrito/generar-pedido/', views.generar_pedido, name='generar_pedido'),
    path('carrito/actualizar/<int:producto_id>/<str:accion>/', views.actualizar_cantidad, name='actualizar_cantidad'),

    # Pedidos
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('pedido/<int:pedido_id>/cancelar/', views.cancelar_pedido, name='cancelar_pedido'),

    # Notificaciones (HU8)
    path('admin-panel/notificaciones/', views.notificaciones_admin, name='notificaciones_admin'),
    path('admin-panel/notificaciones/<int:notif_id>/leer/', views.marcar_notificacion_leida, name='marcar_notificacion_leida'),
    path('admin-panel/notificaciones/leer-todas/', views.marcar_todas_leidas, name='marcar_todas_leidas'),
    path('admin-panel/pedido/<int:pedido_id>/', views.detalle_pedido_admin, name='detalle_pedido_admin'),
    # HU9: Gestión de estados de pedidos
    path('admin-panel/pedido/<int:pedido_id>/cambiar-estado/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
    
    # Categorías admin
    path('admin-panel/categorias/', views.categorias_lista, name='categorias_lista'),
    path('admin-panel/categorias/nueva/', views.categoria_crear, name='categoria_crear'),
    path('admin-panel/categorias/<int:pk>/editar/', views.categoria_editar, name='categoria_editar'),
    path('admin-panel/categorias/<int:pk>/eliminar/', views.categoria_eliminar, name='categoria_eliminar'),
    
    path('admin-panel/pedidos/', views.pedidos_admin, name='pedidos_admin'),
]

urlpatterns += [
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='tienda/password_reset.html'
    ), name='password_reset'),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='tienda/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='tienda/password_reset_confirm.html'
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='tienda/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    
    
]
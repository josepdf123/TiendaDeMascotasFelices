from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from .forms import RegistroForm, AdminLoginForm, ProductoForm, CategoriaForm
from .models import Perfil, Direccion, Pedido, DetallePedido, Producto, Categoria, Notificacion


# ─── Helper ───────────────────────────────────────────────────────────────────

def es_admin(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)


# ─── HU 7: Catálogo público ───────────────────────────────────────────────────

def catalogo(request):
    productos = Producto.objects.filter(activo=True).select_related('categoria')
    categorias = Categoria.objects.all()
    destacados = Producto.objects.filter(activo=True, destacado=True)[:6]

    categoria_slug = request.GET.get('categoria', '')
    if categoria_slug:
        productos = productos.filter(categoria__slug=categoria_slug)

    busqueda = request.GET.get('q', '')
    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) | Q(descripcion__icontains=busqueda)
        )

    context = {
        'productos': productos,
        'categorias': categorias,
        'destacados': destacados,
        'busqueda': busqueda,
        'categoria_activa': categoria_slug,
    }
    return render(request, 'tienda/catalogo.html', context)


def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk, activo=True)
    relacionados = Producto.objects.filter(
        activo=True, categoria=producto.categoria
    ).exclude(pk=pk)[:4]
    return render(request, 'tienda/detalle_producto.html', {
        'producto': producto,
        'relacionados': relacionados,
    })


# ─── HU 1: Login del Administrador ───────────────────────────────────────────

def admin_login(request):
    if request.user.is_authenticated and es_admin(request.user):
        return redirect('admin_panel')

    if request.method == 'POST':
        form = AdminLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if es_admin(user):
                login(request, user)
                messages.success(request, f'¡Bienvenido, {user.first_name or user.username}! 🐾')
                return redirect('admin_panel')
            else:
                messages.error(request, 'No tienes permisos de administrador.')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos. Intenta de nuevo.')
    else:
        form = AdminLoginForm(request)

    return render(request, 'tienda/admin_login.html', {'form': form})


def admin_logout(request):
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('catalogo')


# ─── Panel admin: gestión de productos ───────────────────────────────────────

@login_required(login_url='/login/')
@user_passes_test(es_admin, login_url='/login/')
def admin_panel(request):
    productos = Producto.objects.all().select_related('categoria')
    no_leidas = Notificacion.objects.filter(leida=False).count()
    return render(request, 'tienda/admin_panel.html', {
        'productos': productos,
        'no_leidas': no_leidas,
    })


@login_required(login_url='/login/')
@user_passes_test(es_admin, login_url='/login/')
def producto_crear(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'¡Producto "{producto.nombre}" creado exitosamente! 🎉')
            return redirect('admin_panel')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = ProductoForm()
    return render(request, 'tienda/producto_form.html', {'form': form, 'accion': 'Crear'})


@login_required(login_url='/login/')
@user_passes_test(es_admin, login_url='/login/')
def producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f'¡Producto "{producto.nombre}" actualizado! ✅')
            return redirect('admin_panel')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'tienda/producto_form.html', {
        'form': form,
        'accion': 'Editar',
        'producto': producto,
    })


@login_required(login_url='/login/')
@user_passes_test(es_admin, login_url='/login/')
def producto_eliminar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f'Producto "{nombre}" eliminado correctamente.')
        return redirect('admin_panel')
    return render(request, 'tienda/producto_confirmar_eliminar.html', {'producto': producto})


# ─── Usuarios ─────────────────────────────────────────────────────────────────

def registro(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Este correo ya está registrado ❌')
            return redirect('registro')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=request.POST.get('password'),
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name')
        )

        perfil = user.perfil
        perfil.identificacion = request.POST.get('identificacion')
        perfil.telefono = request.POST.get('telefono')
        perfil.save()

        Direccion.objects.create(
            usuario=user,
            direccion=request.POST.get('direccion')
        )

        messages.success(request, 'Cuenta creada correctamente 🎉')
        return redirect('login')

    return render(request, 'tienda/registro.html')


def login_usuario(request):
    if request.user.is_authenticated:
        return redirect('catalogo')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenido {user.first_name} 🐾')
            if user.is_staff or user.is_superuser:
                return redirect('admin_panel')
            else:
                return redirect('catalogo')
        else:
            messages.error(request, 'Correo o contraseña incorrectos')

    return render(request, 'tienda/login.html')


# ─── Carrito ──────────────────────────────────────────────────────────────────

def agregar_al_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    producto = Producto.objects.get(id=producto_id)
    cantidad_actual = carrito.get(str(producto_id), 0)

    if cantidad_actual < producto.stock:
        carrito[str(producto_id)] = cantidad_actual + 1
        messages.success(request, 'Producto agregado al carrito 🛒')
    else:
        messages.error(request, 'No hay suficiente stock disponible ❌')

    request.session['carrito'] = carrito
    return redirect('catalogo')


def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    productos = []
    total = 0

    for producto_id, cantidad in carrito.items():
        producto = Producto.objects.get(id=producto_id)
        subtotal = producto.precio * cantidad
        total += subtotal
        productos.append({
            'producto': producto,
            'cantidad': cantidad,
            'subtotal': subtotal
        })

    return render(request, 'tienda/carrito.html', {
        'productos': productos,
        'total': total
    })


def eliminar_del_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})

    if str(producto_id) in carrito:
        del carrito[str(producto_id)]

    request.session['carrito'] = carrito
    messages.success(request, 'Producto eliminado del carrito ❌')
    return redirect('ver_carrito')


def actualizar_cantidad(request, producto_id, accion):
    carrito = request.session.get('carrito', {})
    producto = get_object_or_404(Producto, id=producto_id)

    if str(producto_id) in carrito:
        if accion == 'sumar':
            if carrito[str(producto_id)] < producto.stock:
                carrito[str(producto_id)] += 1
            else:
                messages.warning(request, 'No hay más stock disponible ⚠️')
        elif accion == 'restar':
            carrito[str(producto_id)] -= 1
            if carrito[str(producto_id)] <= 0:
                del carrito[str(producto_id)]

    request.session['carrito'] = carrito
    return redirect('ver_carrito')


# ─── Pedidos ──────────────────────────────────────────────────────────────────

@login_required
def generar_pedido(request):
    carrito = request.session.get('carrito', {})

    if not carrito:
        messages.error(request, 'El carrito está vacío')
        return redirect('ver_carrito')

    pedido = Pedido.objects.create(usuario=request.user)

    for producto_id, cantidad in carrito.items():
        producto = Producto.objects.get(id=producto_id)

        if producto.stock < cantidad:
            messages.error(request, f'No hay suficiente stock para {producto.nombre}')
            pedido.delete()
            return redirect('ver_carrito')

        DetallePedido.objects.create(
            pedido=pedido,
            producto=producto,
            cantidad=cantidad,
            precio=producto.precio
        )

        producto.stock -= cantidad
        producto.save()

    request.session['carrito'] = {}
    messages.success(request, 'Pedido generado correctamente 🎉')
    return redirect('mis_pedidos')


@login_required
def mis_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'tienda/mis_pedidos.html', {
        'pedidos': pedidos
    })


@login_required
def cancelar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)

    if pedido.estado != 'pendiente':
        messages.error(request, 'Este pedido no se puede cancelar ❌')
        return redirect('mis_pedidos')

    for detalle in pedido.detalles.all():
        producto = detalle.producto
        producto.stock += detalle.cantidad
        producto.save()

    pedido.estado = 'cancelado'
    pedido.save()

    messages.success(request, 'Pedido cancelado correctamente 🔄')
    return redirect('mis_pedidos')


# ─── Perfil y Direcciones ─────────────────────────────────────────────────────

@login_required
def perfil(request):
    user = request.user
    perfil = user.perfil
    direcciones = user.direcciones.all()

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        perfil.telefono = request.POST.get('telefono')
        perfil.identificacion = request.POST.get('identificacion')
        user.save()
        perfil.save()
        messages.success(request, 'Perfil actualizado correctamente ✨')
        return redirect('perfil')

    return render(request, 'tienda/perfil.html', {
        'user': user,
        'perfil': perfil,
        'direcciones': direcciones
    })


@login_required
def agregar_direccion(request):
    if request.method == 'POST':
        direccion_texto = request.POST.get('direccion')
        if direccion_texto:
            Direccion.objects.create(
                usuario=request.user,
                direccion=direccion_texto
            )
            messages.success(request, 'Dirección agregada correctamente 📍')
    return redirect('perfil')


@login_required
def eliminar_direccion(request, id):
    direccion = Direccion.objects.get(id=id, usuario=request.user)
    direccion.delete()
    messages.success(request, 'Dirección eliminada ❌')
    return redirect('perfil')


# ─── HU8: Notificaciones ─────────────────────────────────────────────────────

@login_required(login_url='/login/')
@user_passes_test(es_admin, login_url='/login/')
def notificaciones_admin(request):
    notificaciones = Notificacion.objects.select_related('pedido__usuario').all()
    no_leidas = notificaciones.filter(leida=False).count()
    return render(request, 'tienda/notificaciones.html', {
        'notificaciones': notificaciones,
        'no_leidas': no_leidas,
    })


@login_required(login_url='/login/')
@user_passes_test(es_admin, login_url='/login/')
def marcar_notificacion_leida(request, notif_id):
    notif = get_object_or_404(Notificacion, id=notif_id)
    notif.leida = True
    notif.save()
    return redirect('detalle_pedido_admin', pedido_id=notif.pedido.id)


@login_required(login_url='/login/')
@user_passes_test(es_admin, login_url='/login/')
def marcar_todas_leidas(request):
    Notificacion.objects.filter(leida=False).update(leida=True)
    messages.success(request, 'Todas las notificaciones marcadas como leídas ✅')
    return redirect('notificaciones_admin')


@login_required(login_url='/login/')
@user_passes_test(es_admin, login_url='/login/')
def detalle_pedido_admin(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    detalles = pedido.detalles.select_related('producto').all()
    return render(request, 'tienda/detalle_pedido_admin.html', {
        'pedido': pedido,
        'detalles': detalles,
    })


@login_required(login_url='/login/')
@user_passes_test(es_admin, login_url='/login/')
def cambiar_estado_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    TRANSICIONES_PERMITIDAS = {
        'pendiente': 'en_proceso',
        'en_proceso': 'entregado',
    }

    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        estados_validos = [e[0] for e in Pedido.ESTADOS]

        if nuevo_estado not in estados_validos:
            messages.error(request, 'Estado no válido.')
            return redirect('detalle_pedido_admin', pedido_id=pedido.id)

        if pedido.estado == 'entregado':
            messages.error(request, 'Este pedido ya fue entregado y no puede modificarse.')
            return redirect('detalle_pedido_admin', pedido_id=pedido.id)

        if pedido.estado == 'cancelado':
            messages.error(request, 'No se puede cambiar el estado de un pedido cancelado.')
            return redirect('detalle_pedido_admin', pedido_id=pedido.id)

        estado_esperado = TRANSICIONES_PERMITIDAS.get(pedido.estado)
        if nuevo_estado != estado_esperado:
            messages.error(request, f'Solo puedes cambiar de "{pedido.get_estado_display()}" a "{dict(Pedido.ESTADOS).get(estado_esperado)}".')
            return redirect('detalle_pedido_admin', pedido_id=pedido.id)

        pedido.estado = nuevo_estado
        pedido.save()
        messages.success(request, f'Pedido #{pedido.id} actualizado a "{pedido.get_estado_display()}" ✅')
        return redirect('detalle_pedido_admin', pedido_id=pedido.id)

    return redirect('detalle_pedido_admin', pedido_id=pedido.id)


# ─── Categorías ───────────────────────────────────────────────────────────────

@login_required(login_url='/login/')
@user_passes_test(es_admin, login_url='/login/')
def categorias_lista(request):
    categorias = Categoria.objects.all()
    return render(request, 'tienda/categorias_lista.html', {
        'categorias': categorias
    })


@login_required(login_url='/login/')
@user_passes_test(es_admin, login_url='/login/')
def categoria_crear(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" creada ✅')
            return redirect('categorias_lista')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = CategoriaForm()
    return render(request, 'tienda/categoria_form.html', {
        'form': form,
        'accion': 'Crear'
    })


@login_required(login_url='/login/')
@user_passes_test(es_admin, login_url='/login/')
def categoria_editar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" actualizada ✅')
            return redirect('categorias_lista')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'tienda/categoria_form.html', {
        'form': form,
        'accion': 'Editar',
        'categoria': categoria
    })


@login_required(login_url='/login/')
@user_passes_test(es_admin, login_url='/login/')
def categoria_eliminar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        nombre = categoria.nombre
        categoria.delete()
        messages.success(request, f'Categoría "{nombre}" eliminada.')
        return redirect('categorias_lista')
    return render(request, 'tienda/categoria_confirmar_eliminar.html', {
        'categoria': categoria
    })


# ─── Pedidos Admin ────────────────────────────────────────────────────────────

@login_required(login_url='/login/')
@user_passes_test(es_admin, login_url='/login/')
def pedidos_admin(request):
    estado_filtro = request.GET.get('estado', '')
    pedidos = Pedido.objects.all().order_by('-fecha')

    if estado_filtro:
        pedidos = pedidos.filter(estado=estado_filtro)

    pedidos_totales = {
        'pendiente':  Pedido.objects.filter(estado='pendiente').count(),
        'en_proceso': Pedido.objects.filter(estado='en_proceso').count(),
        'entregado':  Pedido.objects.filter(estado='entregado').count(),
        'cancelado':  Pedido.objects.filter(estado='cancelado').count(),
    }

    return render(request, 'tienda/pedidos_admin.html', {
        'pedidos': pedidos,
        'estado_filtro': estado_filtro,
        'estados': Pedido.ESTADOS,
        'pedidos_totales': pedidos_totales,
    })
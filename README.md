<<<<<<< HEAD
# 🐾 Mascotas Felices — Aplicativo Web

Tienda de mascotas en línea desarrollada con **Django (MVC)**, **PostgreSQL** y desplegada en **Render**.

---

## 📋 Historias de usuario implementadas (Iteración 1 — Equipo 2)

| HU | Descripción | Estado |
|----|-------------|--------|
| HU1 | Login seguro para el administrador | ✅ |
| HU7 | Catálogo de productos (público y con sesión) | ✅ |
| HU2 | Crear productos (incluido en panel admin) | ✅ |
| HU3 | Eliminar productos | ✅ |
| HU4 | Editar productos | ✅ |

---

## 🗂️ Estructura del proyecto

```
mascotas_felices/
├── mascotas_felices/       # Configuración del proyecto
│   ├── settings.py         # Settings (PostgreSQL en Render, SQLite en local)
│   ├── urls.py             # URLs raíz
│   └── wsgi.py
├── tienda/                 # App principal
│   ├── models.py           # Producto + Categoría
│   ├── views.py            # Lógica de negocio (Controlador en MVC)
│   ├── forms.py            # Formularios Django
│   ├── urls.py             # URLs de la app
│   ├── admin.py            # Admin de Django
│   ├── migrations/         # Migraciones de base de datos
│   └── templates/tienda/   # Vistas HTML (View en MVC)
│       ├── base.html
│       ├── catalogo.html
│       ├── admin_login.html
│       ├── admin_panel.html
│       ├── producto_form.html
│       ├── producto_confirmar_eliminar.html
│       └── detalle_producto.html
├── media/                  # Imágenes subidas (ignorado en git)
├── static_root/            # Estáticos recopilados (ignorado en git)
├── manage.py
├── requirements.txt
├── build.sh                # Script de build para Render
├── render.yaml             # Infraestructura como código (opcional)
└── .gitignore
```

---

## ⚙️ Configuración local (VS Code)

### 1. Clonar y preparar entorno

```bash
# Clonar el repositorio
git clone <tu-repo-url>
cd mascotas_felices

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Variables de entorno

```bash
# Copia el archivo de ejemplo
cp .env.example .env
# Edita .env con tus valores (en local no necesitas DATABASE_URL)
```

### 3. Migrar y crear superusuario

```bash
python manage.py migrate
python manage.py createsuperuser
# Ingresa usuario, email y contraseña cuando te lo pida
```

### 4. Correr el servidor

```bash
python manage.py runserver
```

Abre http://127.0.0.1:8000 en tu navegador.

### URLs principales

| URL | Descripción |
|-----|-------------|
| `/` | Catálogo público (HU7) |
| `/login/` | Login del administrador (HU1) |
| `/admin-panel/` | Panel de gestión de productos |
| `/admin-panel/producto/nuevo/` | Crear producto |
| `/django-admin/` | Admin nativo de Django |

---

## ☁️ Deploy en Render

### Opción A — Manual (recomendada para aprender)

1. **Subir a GitHub**
   ```bash
   git init
   git add .
   git commit -m "feat: iteracion 1 - catalogo y login admin"
   git remote add origin <url-de-tu-repo>
   git push -u origin main
   ```

2. **Crear base de datos PostgreSQL en Render**
   - Dashboard → New → PostgreSQL
   - Nombre: `mascotas-felices-db`
   - Plan: Free
   - Copiar la **Internal Database URL**

3. **Crear Web Service en Render**
   - Dashboard → New → Web Service
   - Conectar tu repositorio de GitHub
   - Configurar:
     - **Build Command:** `./build.sh`
     - **Start Command:** `gunicorn mascotas_felices.wsgi:application`
     - **Plan:** Free

4. **Variables de entorno en Render**
   - `DATABASE_URL` → pega la Internal Database URL del paso 2
   - `SECRET_KEY` → genera una clave con: `python -c "import secrets; print(secrets.token_urlsafe(50))"`
   - `DEBUG` → `False`

5. **Crear superusuario en producción**
   - En Render, ir a tu Web Service → Shell
   ```bash
   python manage.py createsuperuser
   ```

### Opción B — Automática con render.yaml

Si conectas tu repo a Render y tienes el archivo `render.yaml`, Render detectará
la configuración automáticamente (base de datos + web service).

---

## 🗄️ ¿Por qué no se borra la base de datos en Render?

Se usa **PostgreSQL como servicio separado** en Render. A diferencia del sistema
de archivos del Web Service (que es efímero), la base de datos PostgreSQL de
Render **persiste entre deploys y reinicios**.

> ⚠️ Las **imágenes de productos** sí se pierden con cada redeploy porque se
> guardan en el sistema de archivos del contenedor. Para la siguiente iteración
> se recomienda integrar **Cloudinary** o **AWS S3** para imágenes persistentes.

---

## 🔐 Seguridad implementada

- `@login_required` + `@user_passes_test(es_admin)` en todas las vistas del panel
- Solo usuarios `is_staff` o `is_superuser` pueden acceder al panel
- CSRF token en todos los formularios
- Validación de formularios en servidor

---

## 📦 Tecnologías

- **Python 3.11**
- **Django 4.2**
- **PostgreSQL** (producción) / SQLite (desarrollo)
- **Whitenoise** — servir archivos estáticos sin necesidad de S3
- **Gunicorn** — servidor WSGI para producción
- **Pillow** — manejo de imágenes
- **Google Fonts:** Fredoka One + Nunito

---

## 👥 Equipo — Iteración 1

| Rol | Persona |
|-----|---------|
| Desarrollador (Equipo 2) | Jose Herrera |
| Tester (Equipo 2) | Johan Clavijo |
=======
# ProyectoTresMascotas
>>>>>>> 0c8fd6b07aa6bcf94161c952f10698e344724d9b

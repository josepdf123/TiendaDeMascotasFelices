from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
                ('icono', models.CharField(blank=True, help_text='Emoji para la categoría', max_length=10)),
            ],
            options={
                'verbose_name': 'Categoría',
                'verbose_name_plural': 'Categorías',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('descripcion', models.TextField(blank=True)),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stock', models.PositiveIntegerField(default=0)),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='productos/')),
                ('activo', models.BooleanField(default=True)),
                ('destacado', models.BooleanField(default=False, help_text='Mostrar en sección destacada del inicio')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('categoria', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='productos',
                    to='tienda.categoria',
                )),
            ],
            options={
                'verbose_name': 'Producto',
                'verbose_name_plural': 'Productos',
                'ordering': ['-fecha_creacion'],
            },
        ),
    ]

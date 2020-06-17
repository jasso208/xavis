# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class BlogBlog(models.Model):
    nombre_blog = models.CharField(max_length=200)
    id_estatus = models.ForeignKey('BlogEstatusBlog', models.DO_NOTHING)
    imagen_blog = models.CharField(max_length=50, blank=True, null=True)
    fecha = models.DateTimeField()
    autor = models.CharField(max_length=50, blank=True, null=True)
    puesto_autor = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'blog_blog'


class BlogContenidoblog(models.Model):
    contenido_blog = models.TextField()
    id_blog = models.ForeignKey(BlogBlog, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'blog_contenidoblog'


class BlogEstatusBlog(models.Model):
    estatus = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'blog_estatus_blog'


class BlogProductosRelacionados(models.Model):
    id_blog = models.ForeignKey(BlogBlog, models.DO_NOTHING)
    id_producto_relacionado = models.ForeignKey('InventarioProductos', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'blog_productos_relacionados'
        unique_together = (('id_blog', 'id_producto_relacionado'),)


class BlogRelBlogBlog(models.Model):
    id_blog = models.ForeignKey(BlogBlog, models.DO_NOTHING)
    id_blog_relacionado = models.ForeignKey(BlogBlog, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'blog_rel_blog_blog'
        unique_together = (('id_blog', 'id_blog_relacionado'),)


class ContabilidadAuxReporteGastoIngreso(models.Model):
    c1 = models.CharField(max_length=100, blank=True, null=True)
    c2 = models.CharField(max_length=100, blank=True, null=True)
    c3 = models.CharField(max_length=100, blank=True, null=True)
    c4 = models.CharField(max_length=100, blank=True, null=True)
    c5 = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contabilidad_aux_reporte_gasto_ingreso'


class ContabilidadConceptoGasto(models.Model):
    desc_concepto_gasto = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'contabilidad_concepto_gasto'


class ContabilidadConceptoIngreso(models.Model):
    desc_concepto_ingreso = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'contabilidad_concepto_ingreso'


class ContabilidadMovsGasto(models.Model):
    importe = models.DecimalField(max_digits=20, decimal_places=2)
    fecha = models.DateField()
    id_concepto_gasto = models.ForeignKey(ContabilidadConceptoGasto, models.DO_NOTHING, blank=True, null=True)
    id_v = models.ForeignKey('VentasVenta', models.DO_NOTHING, blank=True, null=True)
    descripcion = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'contabilidad_movs_gasto'


class ContabilidadMovsIngreso(models.Model):
    importe = models.DecimalField(max_digits=20, decimal_places=2)
    fecha = models.DateField()
    id_concepto_ingreso = models.ForeignKey(ContabilidadConceptoIngreso, models.DO_NOTHING, blank=True, null=True)
    id_v = models.ForeignKey('VentasVenta', models.DO_NOTHING, blank=True, null=True)
    descripcion = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'contabilidad_movs_ingreso'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class InventarioAtributos(models.Model):
    atributo = models.CharField(max_length=50)
    valor_atributo = models.CharField(max_length=50)
    id_producto = models.ForeignKey('InventarioProductos', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'inventario_atributos'
        unique_together = (('id_producto', 'atributo'),)


class InventarioCategoria1(models.Model):
    categoria_1 = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'inventario_categoria_1'


class InventarioCategoria2(models.Model):
    categoria_2 = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'inventario_categoria_2'


class InventarioCategorias(models.Model):
    categoria = models.CharField(max_length=50)
    categoria_1 = models.ForeignKey(InventarioCategoria1, models.DO_NOTHING)
    categoria_2 = models.ForeignKey(InventarioCategoria2, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'inventario_categorias'
        unique_together = (('categoria', 'categoria_1', 'categoria_2'),)


class InventarioEstado(models.Model):
    estado = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'inventario_estado'


class InventarioEstatus(models.Model):
    estatus = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'inventario_estatus'


class InventarioImgProducto(models.Model):
    nom_img = models.CharField(max_length=7)
    id_producto = models.ForeignKey('InventarioProductos', models.DO_NOTHING)
    orden = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'inventario_img_producto'
        unique_together = (('id_producto', 'orden'),)


class InventarioMunicipio(models.Model):
    municipio = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'inventario_municipio'


class InventarioPais(models.Model):
    pais = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'inventario_pais'


class InventarioProductos(models.Model):
    nombre = models.CharField(max_length=60)
    desc_producto = models.TextField()
    id_estatus = models.ForeignKey(InventarioEstatus, models.DO_NOTHING)
    descuento = models.IntegerField()
    precio = models.DecimalField(max_digits=26, decimal_places=2)
    marca = models.CharField(max_length=100)
    id_proveedor = models.ForeignKey('InventarioProveedor', models.DO_NOTHING, blank=True, null=True)
    clave_prod_proveedor = models.CharField(max_length=20, blank=True, null=True)
    precio_proveedor = models.DecimalField(max_digits=26, decimal_places=2)
    publicado_ml = models.ForeignKey(InventarioEstatus, models.DO_NOTHING)
    porcentaje_ganancia = models.DecimalField(max_digits=26, decimal_places=2)
    porcentaje_ganancia_ml = models.DecimalField(max_digits=26, decimal_places=2)
    precio_ml = models.DecimalField(max_digits=26, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'inventario_productos'


class InventarioProductosRelacionados(models.Model):
    id_producto = models.ForeignKey(InventarioProductos, models.DO_NOTHING)
    id_producto_relacionado = models.ForeignKey(InventarioProductos, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'inventario_productos_relacionados'
        unique_together = (('id_producto', 'id_producto_relacionado'),)


class InventarioProductosTemp(models.Model):
    id_producto = models.IntegerField(unique=True)

    class Meta:
        managed = False
        db_table = 'inventario_productos_temp'


class InventarioProveedor(models.Model):
    proveedor = models.CharField(max_length=40)
    id_estatus = models.ForeignKey(InventarioEstatus, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'inventario_proveedor'


class InventarioRelProductoCategoria(models.Model):
    id_categoria = models.ForeignKey(InventarioCategorias, models.DO_NOTHING)
    id_producto = models.ForeignKey(InventarioProductos, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'inventario_rel_producto_categoria'
        unique_together = (('id_producto', 'id_categoria'),)


class InventarioTallas(models.Model):
    talla = models.CharField(max_length=10)
    id_producto = models.ForeignKey(InventarioProductos, models.DO_NOTHING)
    entrada = models.IntegerField()
    salida = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'inventario_tallas'
        unique_together = (('id_producto', 'talla'),)


class SeguridadCliente(models.Model):
    nombre = models.CharField(max_length=20)
    apellido_p = models.CharField(max_length=20)
    apellido_m = models.CharField(max_length=20)
    telefono = models.CharField(max_length=10)
    e_mail = models.CharField(unique=True, max_length=50)
    rfc = models.CharField(max_length=13, blank=True, null=True)
    psw = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'seguridad_cliente'


class SeguridadClientesLogueados(models.Model):
    session = models.CharField(max_length=18)
    cliente = models.ForeignKey(SeguridadCliente, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'seguridad_clientes_logueados'


class SeguridadDireccionEnvioCliente(models.Model):
    calle = models.CharField(max_length=50)
    numero_exterior = models.CharField(max_length=10)
    cp = models.CharField(max_length=10)
    municipio = models.CharField(max_length=50)
    estado = models.CharField(max_length=50)
    pais = models.CharField(max_length=50)
    referencia = models.CharField(max_length=200)
    cliente = models.ForeignKey(SeguridadCliente, models.DO_NOTHING, blank=True, null=True)
    numero_interior = models.CharField(max_length=10)
    colonia = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'seguridad_direccion_envio_cliente'


class SeguridadDireccionEnvioClienteTemporal(models.Model):
    session = models.CharField(max_length=18)
    nombre = models.CharField(max_length=20)
    apellido_p = models.CharField(max_length=20)
    apellido_m = models.CharField(max_length=20, blank=True, null=True)
    telefono = models.CharField(max_length=10)
    e_mail = models.CharField(max_length=50)
    rfc = models.CharField(max_length=13, blank=True, null=True)
    calle = models.CharField(max_length=50)
    numero_interior = models.CharField(max_length=10, blank=True, null=True)
    numero_exterior = models.CharField(max_length=10)
    cp = models.CharField(max_length=10)
    municipio = models.CharField(max_length=50)
    estado = models.CharField(max_length=50)
    pais = models.CharField(max_length=50)
    referencia = models.CharField(max_length=200)
    colonia = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'seguridad_direccion_envio_cliente_temporal'


class SeguridadEMailNotificacion(models.Model):
    e_mail = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'seguridad_e_mail_notificacion'


class SeguridadRecuperaPws(models.Model):
    e_mail = models.CharField(max_length=50)
    session = models.CharField(max_length=18)
    fecha = models.DateField()

    class Meta:
        managed = False
        db_table = 'seguridad_recupera_pws'


class VentasCarritoCompras(models.Model):
    session = models.CharField(max_length=18)
    cantidad = models.IntegerField()
    id_producto = models.ForeignKey(InventarioProductos, models.DO_NOTHING)
    talla = models.ForeignKey(InventarioTallas, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'ventas_carrito_compras'


class VentasDetalleVenta(models.Model):
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=20, decimal_places=2)
    descuento = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    iva = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    precio_total = models.DecimalField(max_digits=20, decimal_places=2)
    id_producto = models.ForeignKey(InventarioProductos, models.DO_NOTHING, blank=True, null=True)
    id_venta = models.ForeignKey('VentasVenta', models.DO_NOTHING)
    talla = models.ForeignKey(InventarioTallas, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ventas_detalle_venta'


class VentasDireccionEnvioVenta(models.Model):
    nombre_recibe = models.CharField(max_length=20)
    apellido_p = models.CharField(max_length=20)
    apellido_m = models.CharField(max_length=20, blank=True, null=True)
    calle = models.CharField(max_length=50)
    cp = models.CharField(max_length=10)
    municipio = models.CharField(max_length=50)
    estado = models.CharField(max_length=50)
    pais = models.CharField(max_length=50)
    telefono = models.CharField(max_length=20)
    correo_electronico = models.CharField(max_length=50)
    referencia = models.CharField(max_length=200)
    id_venta = models.ForeignKey('VentasVenta', models.DO_NOTHING)
    numero_exterior = models.CharField(max_length=10, blank=True, null=True)
    numero_interior = models.CharField(max_length=10, blank=True, null=True)
    colonia = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ventas_direccion_envio_venta'


class VentasEstatusVenta(models.Model):
    estatus_venta = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'ventas_estatus_venta'


class VentasMedioVenta(models.Model):
    desc_medio = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'ventas_medio_venta'


class VentasVenta(models.Model):
    fecha = models.DateTimeField()
    sub_total = models.DecimalField(max_digits=20, decimal_places=2)
    descuento = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    iva = models.DecimalField(max_digits=20, decimal_places=2)
    total = models.DecimalField(max_digits=20, decimal_places=2)
    id_estatus_venta = models.ForeignKey(VentasEstatusVenta, models.DO_NOTHING)
    link_seguimiento = models.CharField(max_length=200, blank=True, null=True)
    cliente = models.ForeignKey(SeguridadCliente, models.DO_NOTHING, blank=True, null=True)
    costo_envio = models.DecimalField(max_digits=20, decimal_places=2)
    id_medio_venta = models.ForeignKey(VentasMedioVenta, models.DO_NOTHING, blank=True, null=True)
    comision = models.DecimalField(max_digits=20, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'ventas_venta'

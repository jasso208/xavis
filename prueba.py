
#SELECT * from ventas_carrito_compras where ((DATE_PART('day', current_timestamp::timestamp - fecha::timestamp) * 24 +                DATE_PART('hour', current_timestamp::timestamp - fecha::timestamp)) * 60 +               DATE_PART('minute', current_timestamp::timestamp - fecha::timestamp)>10);
#pip install PyGreSQL
#pip install psycopg2
#pip install pygresql
#select t1.session,t1.id_producto_id,t1.talla_id,t1.cantidad,t2.entrada,t2.salida,t2.apartado from ventas_carrito_compras t1 inner join inventario_tallas t2 on t1.id_producto_id=t2.id_producto_id and t1.talla_id=t2.id;
#update inventario_tallas t2 set entrada=entrada+cantidad,apartado=apartado-cantidad from ventas_carrito_compras t1 where t1.id_producto_id=t2.id_producto_id and t1.talla_id=t2.id and  ((DATE_PART('day', current_timestamp::timestamp - fecha::timestamp) * 24 +                DATE_PART('hour', current_timestamp::timestamp - fecha::timestamp)) * 60 +               DATE_PART('minute', current_timestamp::timestamp - fecha::timestamp)>10);
import psycopg2
from datetime import datetime
conexion = psycopg2.connect("dbname= jassdel  user=postgres password=Blanca1985 host=localhost port=5433")
cur=conexion.cursor()

#actualizamos la existencia de los productos que se van a liberar
cur.execute("update inventario_tallas t2 set entrada=entrada+cantidad,apartado=apartado-cantidad from ventas_carrito_compras t1 where t1.id_producto_id=t2.id_producto_id and t1.talla_id=t2.id and  ((DATE_PART('day', current_timestamp::timestamp - fecha::timestamp) * 24 +                DATE_PART('hour', current_timestamp::timestamp - fecha::timestamp)) * 60 +               DATE_PART('minute', current_timestamp::timestamp - fecha::timestamp)>10);")

#borramos todos los productos que tengan mas de 10 min en el carrito y que ya se libero la existencia  en el paso anterior
cur.execute("delete from ventas_carrito_compras where ((DATE_PART('day', current_timestamp::timestamp - fecha::timestamp) * 24+DATE_PART('hour', current_timestamp::timestamp - fecha::timestamp)) * 60 + DATE_PART('minute', current_timestamp::timestamp - fecha::timestamp))>10;")

conexion.commit()

conexion.close()




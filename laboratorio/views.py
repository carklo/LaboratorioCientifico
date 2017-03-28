# coding=utf-8

import decimal
import json
import time
from datetime import datetime
from django.utils.timezone import localtime

from decimal import Decimal

import sys
from django.core import serializers

from django.core.exceptions import ObjectDoesNotExist
from django.http.response import JsonResponse, HttpResponse

from django.shortcuts import render
from django.db.models import Q

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from psycopg2.extensions import JSON

from laboratorio.modelos_vista import BodegaVista, Convertidor, ProductoVista, ProductosBodegaVista, RecursoBusquedaVista, RecursoBusquedaDetalleVista, TransaccionVista, json_default
from laboratorio.models import Tipo, Usuario, Bodega, Experimento, ProductoProtocolo, Producto, Protocolo
from laboratorio.models import TransaccionInventario, Producto, ProductosEnBodega
from laboratorio.utils.utils import utils

# Navegacion de paginas

"""Metodo a navegar index.
"""
def ir_index(request):
    return render(request,"laboratorio/index.html")

"""Metodo a navegar pie de pagina.
"""
def ir_pie(request):
    return render(request,"laboratorio/pie.html")

"""Metodo a navegar encabezado.
"""
def ir_encabezado(request):
    return render(request,"laboratorio/encabezado.html")

"""Metodo a navegar crear bodega.
"""
def ir_crear_bodega(request):
    return render(request, "laboratorio/crearBodega.html")

"""Metodo a navegar lista de bodegas.
"""
def ir_bodegas(request):
    return render(request, "laboratorio/bodegas.html")

#HU: SA-LCINV-3
#SA
#Metodo a navegar al menu de registro de materiales e insumos
def ir_recursos(request):
    return render(request, "laboratorio/recursos.html")
#HU: SA-LCINV-3
#SA
#Metodo a navegar al formulario de registro de insumos
def ir_regitrarInsumos(request):
    return render(request, "laboratorio/registroInsumos.html")
#HU: SA-LCINV-3
#SA
#Metodo a navegar a la lista de recursos
def ir_ver_recursos(request):
    return render(request, "laboratorio/verRecursos.html")
#HU: SA-LCINV-3
#SA
#Metodo a navegar al formulario de edicion de insumos
def ir_editarRecurso(request, recurso_id=1):
    return render(request, "laboratorio/edicionInsumos.html")

def ir_crear_transaccion(request):
    return render(request,"laboratorio/crearTransaccion.html")

def ir_transacciones(request):
    return render(request,"laboratorio/transacciones.html")


"""Metodo obtener los tipos de bodega.
HU: EC-LCINV2: Crear Bodega
Sirve para obtener de la tabla Tipos los tipos de bodega en el sistema
request, es la peticion dada por el usuario
return, formato json con los tipos de bodega
"""
@csrf_exempt
def obtenerTiposBodega(request):
    qs = Tipo.objects.filter(grupo="BODEGA")
    qs_json = serializers.serialize('json', qs)
    return JsonResponse(qs_json, safe=False)

"""Metodo obtener los tipos de unidad de medida.
HU: EC-LCINV4 - EC-LCINV14: Mostrar Unidades de Medida
Sirve para obtener de la tabla Tipos los tipos de unidad de medida
request, es la peticion dada por el usuario
return, formato json con los tipos de unidad de medida
"""
@csrf_exempt
def obtenerUnidadesMedida(request):
    qs = Tipo.objects.filter(grupo__contains="CONVERSION").distinct('nombre')
    qs_json = serializers.serialize('json', qs)
    return JsonResponse(qs_json, safe=False)


"""Metodo obtener los usuarios del sistema.
HU: EC-LCINV2: Crear Bodega
Sirve para obtener los usuarios que existen en el sistema
request, es la peticion dada por el usuario
return, formato json con los usuarios
"""
@csrf_exempt
def obtenerUsuarios(request):
    qs = Usuario.objects.all()
    qs_json = serializers.serialize('json', qs)
    return JsonResponse(qs_json, safe=False)

"""Metodo crear bodega.
HU: EC-LCINV2: Crear Bodega
Sirve para la creacion o actualizacion de bodegas del sistema
request, es la peticion dada por el usuario
return, formato json con un mensaje indicando si fue exitoso o no
"""
@csrf_exempt
def crearBodega(request):
    mensaje = ""
    if request.method == 'POST':
        dosLugares = Decimal('00.01')
        if request.POST.get('id_bodega_guardada', None) == None or request.POST.get('id_bodega_guardada', None) == "":
            bodega = Bodega(serial=request.POST['serial'],
                        nombre=request.POST['nombre'],
                        niveles=int(request.POST['niveles']),
                        secciones=int(request.POST['secciones']),
                        temperatura_minima=Decimal(request.POST['temperatura_minima']),
                        temperatura_media=Decimal(request.POST['temperatura_media']),
                        ubicacion = request.POST['ubicacion'],
                        fecha_creacion = datetime.now(),
                        tipo_bodega = Tipo.objects.filter(id=request.POST['tipo_bodega']).first(),
                        usuario=Usuario.objects.filter(id=request.POST['responsable']).first(),
                        unidad_medida=Tipo.objects.filter(id=request.POST['unidad_medida']).first())

            if not Bodega.objects.filter(serial=bodega.serial).exists():
                bodega.temperatura_minima.quantize(dosLugares, 'ROUND_DOWN')
                bodega.temperatura_media.quantize(dosLugares, 'ROUND_DOWN')
                bodega.save()
                mensaje = "ok"
            else:
                mensaje = "La bodega con ese serial ya existe"
        else:
            bodegass = Bodega.objects.filter(id=int(request.POST['id_bodega_guardada']))
            if (bodegass.exists()):
                bodega = bodegass.first()
                bodega.serial=request.POST['serial']
                bodega.nombre=request.POST['nombre']
                bodega.niveles = int(request.POST['niveles'])
                bodega.secciones = int(request.POST['secciones'])
                bodega.temperatura_minima =Decimal(request.POST['temperatura_minima'])
                bodega.temperatura_media =Decimal(request.POST['temperatura_media'])
                bodega.ubicacion = request.POST['ubicacion']
                bodega.tipo_bodega = Tipo.objects.filter(id=request.POST['tipo_bodega']).first()
                bodega.usuario = Usuario.objects.filter(id=request.POST['responsable']).first()
                bodega.unidad_medida = Tipo.objects.filter(id=request.POST['unidad_medida']).first()

                bodegaBDs = Bodega.objects.filter(serial=bodega.serial)
                actualizar = True
                if bodegaBDs.exists() and bodega.id != bodegaBDs.first().id:
                    actualizar = False

                if actualizar:
                    bodega.temperatura_minima.quantize(dosLugares, 'ROUND_DOWN')
                    bodega.temperatura_media.quantize(dosLugares, 'ROUND_DOWN')
                    bodega.fecha_actualizacion = datetime.now()
                    bodega.save()
                    mensaje = "ok"
                else:
                    mensaje = "La bodega con ese serial ya existe"

    return JsonResponse({"mensaje": mensaje})


# HU: LCINV-5
# FB.
# Hace una búsqueda para saber en qué bodega está y cuál fue su última fecha de transacción.
# request: Petición desde el form de usuario.
# return: Página html con la plantilla y los resultados de la búsqueda asociada.
@csrf_exempt
def verProductoBusqueda(request):
    global bproducto
    global bBodega
    global bFechaTransaccion

    bproducto = ""
    bBodega = ""
    bFechaTransaccion = ""

    # Capturar el valor de los campos
    if request.method == 'POST':
        bproducto = request.POST.get('producto', "")
        bBodega = request.POST.get('bodega', "")
        bFechaTransaccion = request.POST.get('fechatransaccion', "")

    busquedaProducto(request)
    return render(request, "laboratorio/busquedaproducto.html")


# HU: LCINV-5
# FB.
# Hace una búsqueda para saber en qué bodega está y cuál fue su última fecha de transacción.
# Aquí puntualmente es donde se hace el filtro.
# request: Petición desde el form de usuario.
# return: json con los datos encontrados
@csrf_exempt
def busquedaProducto(request):
    # Filtra por la expresion; si no hay nada, muestra todos los productos
    if bproducto == "" and bBodega == "":  # Sin filtro
        qs = ProductosEnBodega.objects.all()
    else: # Filtro
        if bproducto != "" and bBodega == "":  # Si solo se filtra por producto
            qs = ProductosEnBodega.objects.filter(producto__codigo=bproducto)
        elif bproducto == "" and bBodega != "": # Si solo se filtra por bodega
            qs = ProductosEnBodega.objects.filter(bodega__serial=bBodega)
        else: #Filtro por producto y bodega
            qs = ProductosEnBodega.objects.filter(producto__codigo=bproducto, bodega__serial=bBodega)

    listaRecurso = []

    for peb in qs:
        req = RecursoBusquedaVista()
        req.id = peb.id
        req.nombre = peb.producto.nombre
        req.unidadesExistentes = peb.cantidad
        req.unidad_medida = peb.producto.unidad_medida.nombre
        req.fechaTransaccion = obtenerBodegaAcutalxPEBxTransaccion(peb, 2)

        localizacion = ""
        if str(peb.nivel) != "":
            localizacion = ", Nivel " + str(peb.nivel)
        if str(peb.seccion) != "":
            localizacion = localizacion + ", Seccion " + str(peb.seccion)

        req.bodegaActual = peb.bodega.nombre + localizacion
        req.hidden1 = "bFechaTransaccion:" + bFechaTransaccion + " req.fechaTransaccion:" + req.fechaTransaccion  #Variable oculta para debug en html

        if bFechaTransaccion == "":
            listaRecurso.append(req)
        else:
            if bFechaTransaccion in req.fechaTransaccion:
                listaRecurso.append(req)

    json_string = json.dumps(listaRecurso, cls=Convertidor)

    return JsonResponse(json_string, safe=False)


# HU: LCINV-5
# FB.
# Obtiene la última transacción ordenada por fecha de ejecucuón (la más reciente).
# peb: Petición desde el form de usuario.
# campo: El campo que se requiere retornar.
# return: El dato puntual solicitado.
def obtenerBodegaAcutalxPEBxTransaccion(peb, campo):
    qs = TransaccionInventario.objects.filter(producto_bodega_destino=peb).order_by('-fecha_ejecucion')[:1]
    retorno="N/A"
    if qs.exists():
        if campo == 1:
            retorno = qs[0].bodega_destino.nombre
        if campo == 2:
            fecha = localtime(qs[0].fecha_ejecucion)
            retorno = fecha.strftime('%Y-%m-%d %H:%M:%S')
        if campo == 3:
            retorno = localtime(qs[0].fecha_ejecucion)
    return retorno


# HU: LCINV-5
# FB.
# Obtiene el nombre completo del usuario consultado.
# usuario: Id de usuario.
# return: Nombre de usuario compuesto por Nombre y Apellido.
def obtenerNombreUsuarioxId(usuario):
    qs = Usuario.objects.filter(id=usuario)[:1]

    retorno = "N/A"

    retorno = qs[0].first_name + " " + qs[0].last_name

    return retorno


# HU: LCINV-5
# FB.
# Muestra el detalle de transacciones para un Producto dado.
# request: Petición desde el form de usuario.
# return: Página html con la plantilla y los resultados de la búsqueda asociada.
@csrf_exempt
def verProductoBusquedaDetalle(request):
    global globvar
    globvar = request.GET.get('id')
    busquedaProductoDetalle(request)
    return render(request, "laboratorio/busquedaproductodetalle.html")


# HU: LCINV-5
# FB.
# Muestra el detalle de transacciones para un Producto dado. Esta es la búsqueda como tal.
# request: Petición desde el form de usuario.
# return: json con los datos encontrados
def busquedaProductoDetalle(request):
    idpeb = int(globvar)
    qs = TransaccionInventario.objects.filter(producto_bodega_destino_id=idpeb).order_by('-fecha_creacion')

    listaTrans = []

    for transaccion in qs:
        req = RecursoBusquedaDetalleVista()
        req.id = transaccion.id
        req.recurso = transaccion.producto.nombre
        fecha = localtime(transaccion.fecha_ejecucion)
        req.fecha = fecha.strftime('%Y-%m-%d %H:%M:%S')
        req.tipoTransaccion = transaccion.tipo.nombre  # TIPOTRX
        req.estadoTrans = transaccion.estado.nombre  # STATUSTRX

        localizacion1 = ""
        if str(transaccion.nivel_origen) != "":
            localizacion1 = localizacion1 + ", Nivel " + str(transaccion.nivel_origen)
        if str(transaccion.seccion_origen) != "":
            localizacion1 = localizacion1 + ", Seccion " + str(transaccion.seccion_origen)

        # req.bodegaOrigen = transaccion.producto_bodega_origen.bodega.nombre + ", nivel " + str(transaccion.nivel_origen) + ", seccion " + str(transaccion.seccion_origen)
        req.bodegaOrigen = transaccion.producto_bodega_origen.bodega.nombre + localizacion1
        req.nivel_origen = ""  # n/a
        req.seccion_origen = ""  # n/a

        localizacion2 = ""
        if str(transaccion.nivel_destino) != "":
            localizacion2 = localizacion2 + ", Nivel " + str(transaccion.nivel_destino)
        if str(transaccion.seccion_destino) != "":
            localizacion2 = localizacion2 + ", Seccion " + str(transaccion.seccion_destino)

        # req.bodegaDestino = transaccion.producto_bodega_destino.bodega.nombre + ", nivel " + str(transaccion.nivel_destino) + ", seccion " + str(transaccion.seccion_destino)
        req.bodegaDestino = transaccion.producto_bodega_destino.bodega.nombre + localizacion2
        req.nivel_destino = ""  # n/a
        req.seccion_destino = ""  # n/a
        req.cantidad = str(transaccion.cantidad)
        req.unidad_medida = transaccion.unidad_medida.nombre
        #req.usuario = transaccion.usuario.first_name + " " + transaccion.usuario.last_name
        #req.autoriza = transaccion.autoriza.first_name + " " + transaccion.autoriza.last_name
        # req.usuario = obtenerNombreUsuarioxId(transaccion.usuario.id)
        # req.autoriza = obtenerNombreUsuarioxId(transaccion.autoriza.id)
        req.comentarios = transaccion.comentarios
        listaTrans.append(req)

    json_string = json.dumps(listaTrans, cls=Convertidor)
    return JsonResponse(json_string, safe=False)


# HU: LCINV-5
# FB.
# Lista los productos, esto se utiliza para mostrar el listado en el html para la búsqueda.
# request: Petición desde el form de usuario.
# return: json con los datos encontrados
@csrf_exempt
def llenarListadoProductosBusqueda(request):
    qs = Producto.objects.all().order_by('nombre')
    qs_json = serializers.serialize('json', qs)
    return JsonResponse(qs_json, safe=False)


# HU: LCINV-5
# FB.
# Lista las bodegas, esto se utiliza para mostrar el listado en el html para la búsqueda.
# request: Petición desde el form de usuario.
# return: json con los datos encontrados
@csrf_exempt
def llenarListadoBodegasBusqueda(request):
    qs = Bodega.objects.all().order_by('nombre')
    qs_json = serializers.serialize('json', qs)
    return JsonResponse(qs_json, safe=False)


@csrf_exempt
def obtenerBodegas(request):
    qs = Bodega.objects.all()
    listaBodegas = []
    for bodega in qs:
        bod = BodegaVista()
        bod.id = bodega.id
        bod.nombre = bodega.nombre
        bod.serial = bodega.serial
        bod.niveles = bodega.niveles
        bod.secciones = bodega.secciones
        bod.temperatura_minima = str(bodega.temperatura_minima)
        bod.temperatura_media = str(bodega.temperatura_media)
        bod.ubicacion = bodega.ubicacion
        bod.tipo_bodega = bodega.tipo_bodega.nombre
        bod.unidad_medida = bodega.unidad_medida.nombre
        if bodega.estado:
            bod.estado = "Activo"
        else:
            bod.estado = "Inactivo"
        bod.responsable = bodega.usuario.first_name + " " + bodega.usuario.last_name
        listaBodegas.append(bod)
    json_string = json.dumps(listaBodegas, cls=Convertidor)
    return JsonResponse(json_string, safe=False)

@csrf_exempt
def obtenerTransacciones(request):
    qs = TransaccionInventario.objects.all()
    listaTransacciones = []
    for transaccion in qs:
        trx = TransaccionVista()
        trx.id = transaccion.id
        trx.tipo = transaccion.tipo.nombre
        trx.bodega_origen = transaccion.bodega_origen.nombre
        trx.nivel_origen = transaccion.nivel_origen
        trx.seccion_origen = transaccion.seccion_origen
        trx.bodega_destino = transaccion.bodega_destino.nombre
        trx.nivel_destino = transaccion.nivel_destino
        trx.seccion_destino = transaccion.seccion_destino
        trx.producto = transaccion.producto.nombre
        trx.cantidad = transaccion.cantidad
        trx.unidad_medida = transaccion.unidad_medida.nombre
        trx.estado = transaccion.estado.nombre
        trx.fecha_creacion = transaccion.fecha_creacion
        trx.fecha_ejecucion = transaccion.fecha_ejecucion
        trx.comentarios = transaccion.comentarios
        trx.usuario = transaccion.usuario
        #bod.responsable = bodega.usuario.first_name + " " + bodega.usuario.last_name
        listaTransacciones.append(trx)
    json_string = json.dumps(listaTransacciones, cls=Convertidor, ensure_ascii=False, default=json_default)
    return JsonResponse(json_string, safe=False)

#HU-LCINV-13
#GZ
#Obtiene la lista de transacciones para mostrarla en la tabla del UI
@csrf_exempt
def obtenerTransaccion(request):
    time.sleep(0.3)
    qs = TransaccionInventario.objects.filter(id=request.GET['id_transaccion'])
    qs_json = serializers.serialize('json', qs)
    struct = json.loads(qs_json)
    json_bodega = json.dumps(struct[0])
    return JsonResponse({"transaccion": json_bodega})
  
@csrf_exempt
def obtenerBodega(request):
    time.sleep(0.3)
    qs = Bodega.objects.filter(id=request.GET['id_bodega'])
    qs_json = serializers.serialize('json', qs)
    struct = json.loads(qs_json)
    json_bodega = json.dumps(struct[0])
    return JsonResponse({"bodega": json_bodega})

#HU-LCINV-13
#GZ
#Crea una transaccion de inventario:
#Recibe bodega origen con localizacion (Nivel, Seccion)
#Bodega destino con localizacion (Nivel, Seccion)
#Producto y cantidad a mover

@csrf_exempt
def crear_transaccion(request):
    if request.method == 'POST':
        json_tran = json.loads(request.body);
        print >> sys.stdout, "Prod" + json_tran['producto']
        print >> sys.stdout, "PRODProd" + json_tran['producto_bodega_origen']
        transaccion = TransaccionInventario(
            tipo=Tipo.objects.get(pk=json_tran['tipo']),
            bodega_origen= Bodega.objects.get(pk=json_tran['bodega_origen']),
            nivel_origen=json_tran['nivel_origen'],
            seccion_origen=json_tran['seccion_origen'],
            bodega_destino = Bodega.objects.get(pk=json_tran['bodega_destino']),
            nivel_destino=json_tran['nivel_destino'],
            seccion_destino=json_tran['seccion_destino'],
            producto_bodega_origen = ProductosEnBodega.objects.filter(id=json_tran['producto_bodega_origen']).first(),
            producto=Producto.objects.get(pk=json_tran['producto']),
            cantidad=json_tran['cantidad'],
            unidad_medida=Tipo.objects.get(nombre=json_tran['unidad_medida'], grupo='MEDIDAPRODUCTO'),
            estado=Tipo.objects.get(pk=Tipo.objects.filter(nombre='Ejecutada', grupo='STATUSTRX').first().id),
            fecha_creacion=datetime.now(),
            fecha_ejecucion=datetime.now(),
            usuario=Usuario.objects.get(pk=1),
            comentarios=json_tran['comentarios']
        )
        ejecutar_transaccion(transaccion)
        transaccion.save()
        tran_json = json.loads(serializers.serialize('json', [transaccion]));
        return JsonResponse(tran_json, safe=False)


# HU-LCINV-13
# GZ
#Ejecuta la transaccion de inventario: Afecta las cantidades de producto por un movimento pedido
#Resta de la bodega origen y suma o crea registro en la bodega destino

@csrf_exempt
def ejecutar_transaccion(transaccion):
    try:
        if transaccion.tipo.nombre != "Recepcion de Proveedor":
            producto_bodega_origen = ProductosEnBodega.objects.get(pk=transaccion.producto_bodega_origen.pk)
            producto_bodega_origen.cantidad = int(producto_bodega_origen.cantidad) - int(transaccion.cantidad)
            producto = producto_bodega_origen.producto
        else:
            producto = transaccion.producto


        producto_bodega_destino_list = ProductosEnBodega.objects.filter(bodega=transaccion.bodega_destino)
        producto_bodega_destino_list = producto_bodega_destino_list.filter(producto=transaccion.producto)
        producto_bodega_destino_list = producto_bodega_destino_list.filter(nivel=transaccion.nivel_destino)
        producto_bodega_destino_list = producto_bodega_destino_list.filter(seccion=transaccion.seccion_destino)

        if producto_bodega_destino_list.exists():
            producto_bodega_destino = producto_bodega_destino_list.first()
            producto_bodega_destino.cantidad = int(producto_bodega_destino.cantidad) + int(transaccion.cantidad)
        else:
            producto_bodega_destino = ProductosEnBodega(
                                    bodega=transaccion.bodega_destino,
                                    producto = producto,
                                    nivel = transaccion.nivel_destino,
                                    seccion = transaccion.seccion_destino,
                                    cantidad = transaccion.cantidad,
                                    unidad_medida=transaccion.unidad_medida

            )

        producto_bodega_destino.save()
        transaccion.fecha_ejecucion=datetime.now()
        transaccion.producto_bodega_destino = producto_bodega_destino
        transaccion.estado = Tipo.objects.get(pk=Tipo.objects.filter(nombre='Ejecutada').first().id)
        transaccion.save()
        if transaccion.tipo.nombre != "Recepcion de Proveedor":
                producto_bodega_origen.save()


    except Exception as e:
        print 'EXCEPCION: %s (%s)' % (e.message, type(e))

# HU-LCINV-13
# GZ
#Funcion GET que trae listas de valores segun el tipo
@csrf_exempt
def obtenerTipos(request):
    grupo = request.GET['grupo']
    qs = Tipo.objects.filter(grupo=grupo)
    qs_json = serializers.serialize('json', qs)
    return JsonResponse(qs_json, safe=False)

# HU-LCINV-13
# GZ
# Obtiene los productos de la bodega seleccionada
@csrf_exempt
def obtenerProductosBodega(request):
    bodega = request.GET['bodega']
    pb_bodAll = ProductosEnBodega.objects.filter(bodega=Bodega.objects.get(pk=bodega))
    pb_bod = pb_bodAll.filter(cantidad__gt=0)
    listaProductosBodegas = []

    for productoBodega in pb_bod:
        pb = ProductosBodegaVista()
        pb.id = productoBodega.id
        pb.bodega = productoBodega.bodega.pk
        pb.producto = Producto.objects.get(pk=productoBodega.producto.pk).nombre
        pb.prod_id = Producto.objects.get(pk=productoBodega.producto.pk).pk
        pb.cantidad = productoBodega.cantidad
        pb.nivel = productoBodega.nivel
        pb.seccion = productoBodega.seccion
        pb.unidad_medida = Tipo.objects.get(pk=productoBodega.unidad_medida.id).nombre
        listaProductosBodegas.append(pb)
    json_pb = json.dumps(listaProductosBodegas, cls=Convertidor)
    return JsonResponse(json_pb, safe=False)        
        
        
@csrf_exempt
def obtenerExperimentos(request):
    qs = Experimento.objects.all().prefetch_related('asignado')
    qs_json = serializers.serialize('json', qs)
    respT = []
    for exp in qs:
        asignado = exp.asignado.values('username', 'id')[0]
        struct = json.loads(qs_json)[0]
        resp = {'experimento': struct, 'asignado': asignado}
        respT.append(resp)
    return JsonResponse(respT, safe=False)

@csrf_exempt
def obtenerExperimentosPorUsuario(request):
    usuario = Usuario.objects.get(username=request.GET['username'])
    exp_usuario = Experimento.objects.filter(asignado=usuario)
    qs_json = serializers.serialize('json', exp_usuario)
    return JsonResponse(qs_json, safe=False)

@csrf_exempt
def obtenerProtocolosPorExperimento(request):
    exp = Experimento.objects.filter(codigo=request.GET['codigo'])
    prots_exp = Protocolo.objects.filter(experimento=exp)
    qs_json = serializers.serialize('json', prots_exp)
    return JsonResponse(qs_json, safe=False)

@csrf_exempt
def obtenerPPPorProtocolo(request):
    prot = Protocolo.objects.filter(id=request.GET['id'])
    prods_prot = ProductoProtocolo.objects.filter(protocolo=prot).select_related('producto')
    qs_json = serializers.serialize('json', prods_prot)
    producto = {'nombre':prods_prot.first().producto.nombre,
                'id': prods_prot.first().producto.pk}
    struct = json.loads(qs_json)[0]
    resp = {'productoprotocolo': struct, 'producto': producto}
    return JsonResponse(resp, safe=False)

def experimentos(request):
    return render(request, "laboratorio/experimentos.html")

#HU: SA-LCINV-3
#SA
#Metodo que representa el servicio REST que hace el registro de un nuevo recurso (Insumo/Reactivo)
#Recibe los campos ingresados en el formulario de registro de recursos
#Si no hay otro recurso con el mismo codigo o nombre se hace el registro y se retorna un mensaje ok en formato JSON
#En caso contrario se indica el respectivo mensaje de error en formato JSON
@csrf_exempt
def registrarInsumoReactivo(request):
    mensaje = ""
    dosLugares = Decimal('00.01')
    if request.method == 'POST':
        codigo = request.POST['codigo']
        nombre = request.POST['nombre']
        descripcion = request.POST['descripcion']
        if request.POST['valor'] == "":
            valor = 0
        else:
            valor = int(request.POST['valor'])
        if request.POST['unidades'] == "":
            unidadesExistentes = 0
        else:
            unidadesExistentes = int(request.POST['unidades'])
        clasificacion = request.POST['clasificacion']
        if request.POST['cantidad'] == "":
            unitaria = 0.0
        else:
            unitaria = Decimal(request.POST['cantidad'])
        imageFile = request.FILES.get('imageFile', None)

        if codigo != "" and nombre != "" and descripcion != "" and valor != 0 and unidadesExistentes != 0 and unitaria != 0 and imageFile != None and request.POST['cantidad'] != "" and request.POST['proveedor'] != "":
            if Producto.objects.filter(codigo=codigo).first() != None or Producto.objects.filter(nombre=nombre).first() !=None:
                mensaje = "El insumo/reactivo con el codigo o nombre ingresado ya existe."
            else:
                #Es un producto con un codigo y un nombre nuevos
                producto = Producto(codigo=codigo,
                                    nombre=nombre,
                                    descripcion=descripcion,
                                    valorUnitario=valor,
                                    unidadesExistentes=unidadesExistentes,
                                    clasificacion=clasificacion,
                                    unidad_medida=Tipo.objects.filter(id=request.POST['medida']).first(),
                                    unidad_unitaria=unitaria,
                                    imageFile=imageFile,
                                    proveedor=Usuario.objects.filter(id=request.POST['proveedor']).first())

                producto.unidad_unitaria.quantize(dosLugares, 'ROUND_DOWN')
                producto.save()
                mensaje = "ok"
        else:
            mensaje = "Todos los campos deben estar debidamente diligenciados"

    return JsonResponse({"mensaje":mensaje})

#HU: SA-LCINV-3
#SA
#Metodo que representa el servicio REST para retornar un JSON con un arreglo las medidas (unidades del S.I)
#con las que se caracteriza un recurso
@csrf_exempt
def obtenerTiposMedida(request):
    qs = Tipo.objects.filter(grupo="MEDIDAPRODUCTO")
    qs_json = serializers.serialize('json', qs)
    return JsonResponse(qs_json, safe=False)

#HU: SA-LCINV-3
#SA
#Metodo que representa el servicio REST para retornar todos los recursos/productos guardados
#en la base de datos en un arreglo con formato JSON
@csrf_exempt
def obtenerRecursos(request):
    qs = Producto.objects.all()
    listaProductos = []
    for producto in qs:
        prod = ProductoVista()
        prod.id = producto.id
        prod.codigo = producto.codigo
        prod.nombre = producto.nombre
        prod.descripcion = producto.descripcion
        prod.valorUnitario = str(producto.valorUnitario)
        prod.unidadesExistentes = str(producto.unidadesExistentes)
        prod.clasificacion = producto.get_clasificacion_display()
        prod.unidad_medida = producto.unidad_medida.nombre
        prod.unidad_unitaria = str(producto.unidad_unitaria)
        prod.imageFile = str(producto.imageFile)
        prod.proveedor = producto.proveedor.first_name
        listaProductos.append(prod)
    json_string = json.dumps(listaProductos, cls=Convertidor)
    return JsonResponse(json_string, safe=False)

#HU: SA-LCINV-3
#SA
#Metodo que representa el servicio REST para retornar un recurso en formato JSON cuando en el
#request de la peticion llega el id de ese recurso
@csrf_exempt
def obtenerRecurso(request):
    time.sleep(0.3)
    qs = Producto.objects.filter(id=request.GET['recurso_id'])
    qs_json = serializers.serialize('json', qs)
    struct = json.loads(qs_json)
    json_recurso = json.dumps(struct[0])
    return JsonResponse({"producto": json_recurso})

#HU: SA-LCINV-3
#SA
#Metodo que representa el servicio REST para guardar la edicion que se ha hecho de un recurso
#Solo se guardara la edicion si no se presentan conflictos de codigo o nombre con otros recursos
#y si estan todos los campos completos a excepcion de la imagen que es opcional, se retorna un
#mensaje en formato JSON
@csrf_exempt
def guardarEdicionInsumo(request):

    mensaje = ""
    if request.method == 'POST':
        codigo = request.POST['codigo']
        nombre = request.POST['nombre']
        descripcion = request.POST['descripcion']
        if request.POST['valor'] == "":
            valor = 0
        else:
            valor = int(request.POST['valor'])
        if request.POST['unidades'] == "":
            unidadesExistentes = 0
        else:
            unidadesExistentes = int(request.POST['unidades'])
        clasificacion = request.POST['clasificacion']
        if request.POST['cantidad'] == "":
            unitaria = 0.0
        else:
            unitaria = Decimal(request.POST['cantidad'])
        clasificacion = request.POST['clasificacion']
        imageFile = request.FILES.get('imageFile',None)
        proveedor = request.POST['proveedor']
        producto = Producto.objects.filter(id=int(request.POST['id_producto_guardado'])).first()


        modificacion = False
        error = False
        if producto != None:
            if codigo != "" and nombre != "" and descripcion != "" and valor != 0 and unidadesExistentes != 0 and unitaria != 0 and request.POST['cantidad'] != "" and request.POST['proveedor'] != "":
                if producto.codigo != codigo or producto.nombre != nombre:
                    try:
                        Producto.objects.get(codigo=codigo)
                        if producto.codigo != codigo:
                            error = True
                        else:
                            try:
                                Producto.objects.get(nombre=nombre)
                                if producto.nombre != nombre:
                                    error = True
                                else:
                                    modificacion = True
                            except ObjectDoesNotExist:
                                modificacion = True

                    except ObjectDoesNotExist:
                        modificacion = True
                        try:
                            Producto.objects.get(nombre=nombre)
                            if producto.nombre != nombre:
                                error = True
                            else:
                                modificacion = True
                        except ObjectDoesNotExist:
                            modificacion = True

                elif producto.codigo == codigo and producto.nombre == nombre:
                    modificacion = True

                if error:
                    mensaje="El insumo/reactivo con el codigo o nombre ingresado ya existe."
                else:
                    if modificacion == True:
                        producto.codigo = codigo
                        producto.nombre = nombre
                        producto.descripcion = descripcion
                        producto.valorUnitario = valor
                        producto.unidadesExistentes = unidadesExistentes
                        producto.clasificacion = clasificacion
                        producto.unidad_medida = Tipo.objects.filter(id=request.POST['medida']).first()
                        producto.unidad_unitaria = unitaria
                        if (imageFile != None):
                            producto.imageFile = imageFile
                        producto.proveedor = Usuario.objects.filter(id=proveedor).first()
                        producto.save()
                        mensaje = "ok"

            else:
                mensaje = "Todos los campos deben estar debidamente diligenciados"
        else:
            mensaje = "El id del insumo/reactivo que se quiere editar no existe"

    return JsonResponse({"mensaje": mensaje})

#HU: LCINV-4, 12
#SA - EC
#Metodo que representa el servicio REST para la conversion de unidades que sera
#invocado en la capa de presentacion, retorna el valor numerico de la conversion solicitada en formato JSON
@csrf_exempt
def convertirUnidad(request):

    cantidad = request.GET['cantidad']
    medidaOrigen = request.GET['medidaOrigen']
    medidaDestino = request.GET['medidaDestino']
    res = utils.convertir(cantidad=cantidad, medidaOrigen=medidaOrigen, medidaDestino=medidaDestino)
    return JsonResponse({"conversion":res})

#HU: SA-LCVIN-3
#SA
#Metodo que representa el servicio REST para obtener los proveedores actuales de insumos
#se retornara una lista de los proveedores en formato JSON
@csrf_exempt
def obtenerProveedores(request):

    proveedores = Usuario.objects.filter(roles__nombre="Proveedor")
    qs_json = serializers.serialize('json', proveedores)
    return JsonResponse(qs_json, safe=False)
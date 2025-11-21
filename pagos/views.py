from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.conf import settings
import qrcode
import os
import datetime
import random
import string
from django.db import transaction


def generar_codigo_qr(boleto_id):

    codigo = f"BOLETO-{boleto_id}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
    
    # Crear directorio si no existe
    qr_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
    os.makedirs(qr_dir, exist_ok=True)
    
    # Generar QR
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(codigo)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    qr_path = os.path.join(qr_dir, f"{codigo}.png")
    img.save(qr_path)
    
    return codigo


def procesar_pago(request, evento_id, categoria_id, cantidad):

    if 'usuario_id' not in request.session:
        return redirect('usuarios:login')
    
    usuario_id = request.session['usuario_id']
    try:
        cantidad = int(cantidad)
    except (ValueError, TypeError):
        messages.error(request, 'Cantidad inválida')
        return redirect('eventos:detalle', evento_id=evento_id)

    # Obtener información del evento y categoría y verificar disponibilidad
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT e.nombre, ce.nombre_categoria, ce.precio, ce.cantidad_asientos
            FROM Eventos e
            INNER JOIN Categorias_Evento ce ON e.id_evento = ce.id_evento
            WHERE e.id_evento = %s AND ce.id_categoria = %s
        """, [evento_id, categoria_id])

        info = cursor.fetchone()
        if not info:
            messages.error(request, 'Evento o categoría no encontrada')
            return redirect('eventos:lista')

        evento_nombre = info[0]
        categoria_nombre = info[1]
        precio_unitario = info[2]
        cantidad_asientos = info[3] or 0

        # contar vendidos
        cursor.execute("""
            SELECT COUNT(*) FROM Boletos
            WHERE id_evento = %s AND id_categoria = %s AND estado IN ('pagado','validado')
        """, [evento_id, categoria_id])
        vendidos = cursor.fetchone()[0]
        disponibles = cantidad_asientos - vendidos if cantidad_asientos else None

        if disponibles is not None and cantidad > disponibles:
            messages.error(request, f'Solo hay {disponibles} boletos disponibles en esta categoría')
            return redirect('boletos:comprar', evento_id=evento_id)

        total = precio_unitario * cantidad
    
    if request.method == 'POST':
        metodo_pago = request.POST.get('metodo_pago', 'tarjeta')
        
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    # Crear compra
                    cursor.execute("""
                        INSERT INTO Compras (id_cliente, fecha_compra, total, metodo_pago, estado)
                        VALUES (%s, %s, %s, %s, %s)
                    """, [usuario_id, datetime.datetime.now(), total, metodo_pago, 'pendiente'])

                    cursor.execute("SELECT LAST_INSERT_ID()")
                    compra_id = cursor.fetchone()[0]

                    # Crear registro de pago
                    cursor.execute("""
                        INSERT INTO Pagos (id_compra, fecha_pago, monto, metodo, estado)
                        VALUES (%s, %s, %s, %s, %s)
                    """, [compra_id, datetime.datetime.now(), total, metodo_pago, 'exitoso'])

                    # Re-verificar disponibilidad dentro de la transacción
                    cursor.execute("""
                        SELECT ce.cantidad_asientos
                        FROM Categorias_Evento ce
                        WHERE ce.id_categoria = %s
                    """, [categoria_id])
                    cantidad_asientos_db = cursor.fetchone()[0] if cursor.rowcount != 0 else 0

                    cursor.execute("""
                        SELECT COUNT(*) FROM Boletos
                        WHERE id_evento = %s AND id_categoria = %s AND estado IN ('pagado','validado')
                    """, [evento_id, categoria_id])
                    vendidos_tx = cursor.fetchone()[0]
                    disponibles_tx = (cantidad_asientos_db or 0) - vendidos_tx if cantidad_asientos_db else None

                    if disponibles_tx is not None and cantidad > disponibles_tx:
                        raise Exception(f'Solo hay {disponibles_tx} boletos disponibles en esta categoría')

                    # Crear boletos y detalle de compra
                    for i in range(cantidad):
                        cursor.execute("""
                            INSERT INTO Boletos (id_evento, id_categoria, precio, estado, id_cliente)
                            VALUES (%s, %s, %s, %s, %s)
                        """, [evento_id, categoria_id, precio_unitario, 'pagado', usuario_id])

                        cursor.execute("SELECT LAST_INSERT_ID()")
                        boleto_id = cursor.fetchone()[0]

                        # Generar código QR y actualizar el boleto
                        codigo_qr = generar_codigo_qr(boleto_id)
                        cursor.execute("""
                            UPDATE Boletos SET codigo = %s WHERE id_boleto = %s
                        """, [codigo_qr, boleto_id])

                        # Crear detalle de compra (precio unitario)
                        cursor.execute("""
                            INSERT INTO Detalle_Compras (id_compra, id_boleto, precio)
                            VALUES (%s, %s, %s)
                        """, [compra_id, boleto_id, precio_unitario])

                    # Marcar compra como completada
                    cursor.execute("""
                        UPDATE Compras SET estado = 'completado' WHERE id_compra = %s
                    """, [compra_id])

            messages.success(request, 'Pago procesado correctamente')
            return redirect('pagos:confirmacion', compra_id=compra_id)
            
        except Exception as e:
            messages.error(request, f'Error al procesar pago: {str(e)}')
    
    context = {
        'evento_nombre': evento_nombre,
        'categoria_nombre': categoria_nombre,
        'cantidad': cantidad,
        'precio_unitario': precio_unitario,
        'total': total,
    }
    
    return render(request, 'pagos/procesar.html', context)


def confirmacion_pago(request, compra_id):
    """
    Vista para mostrar la confirmación de compra
    """
    if 'usuario_id' not in request.session:
        return redirect('usuarios:login')
    
    with connection.cursor() as cursor:
        # Obtener información de la compra
        cursor.execute("""
            SELECT c.id_compra, c.fecha_compra, c.total,
                   p.metodo, p.estado
            FROM Compras c
            INNER JOIN Pagos p ON c.id_compra = p.id_compra
            WHERE c.id_compra = %s
        """, [compra_id])
        
        compra_row = cursor.fetchone()
        if not compra_row:
            messages.error(request, 'Compra no encontrada')
            return redirect('eventos:lista')
        
        compra = {
            'id': compra_row[0],
            'fecha': compra_row[1],
            'total': compra_row[2],
            'metodo_pago': compra_row[3],
            'estado': compra_row[4],
        }
        
        # Obtener boletos de la compra
        cursor.execute("""
             SELECT b.id_boleto, b.codigo, e.nombre as evento_nombre,
                 ce.nombre_categoria, b.precio
            FROM Boletos b
            INNER JOIN Detalle_Compras dc ON b.id_boleto = dc.id_boleto
            INNER JOIN Eventos e ON b.id_evento = e.id_evento
            LEFT JOIN Categorias_Evento ce ON b.id_categoria = ce.id_categoria
            WHERE dc.id_compra = %s
        """, [compra_id])
        
        boletos = []
        for row in cursor.fetchall():
            boletos.append({
                'id': row[0],
                'codigo_qr': row[1],
                'evento_nombre': row[2],
                'categoria': row[3],
                'precio': row[4],
            })
    
    context = {
        'compra': compra,
        'boletos': boletos,
    }
    
    return render(request, 'pagos/confirmacion.html', context)


def procesar_pago_sin_categoria(request, evento_id, cantidad):
    """
    Procesar compra cuando no hay categorías definidas para el evento.
    Se guarda la compra y los boletos con id_categoria = NULL.
    """
    if 'usuario_id' not in request.session:
        return redirect('usuarios:login')

    usuario_id = request.session['usuario_id']

    try:
        cantidad = int(cantidad)
    except (ValueError, TypeError):
        messages.error(request, 'Cantidad inválida')
        return redirect('eventos:detalle', evento_id=evento_id)

    # Obtener información del evento para mostrar en resumen
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT nombre FROM Eventos WHERE id_evento = %s
        """, [evento_id])
        row = cursor.fetchone()
        if not row:
            messages.error(request, 'Evento no encontrado')
            return redirect('eventos:lista')
        evento_nombre = row[0]

    precio_unitario = 0
    total = 0

    if request.method == 'POST':
        metodo_pago = request.POST.get('metodo_pago', 'tarjeta')
        
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    # Crear compra
                    cursor.execute("""
                        INSERT INTO Compras (id_cliente, fecha_compra, total, metodo_pago, estado)
                        VALUES (%s, %s, %s, %s, %s)
                    """, [usuario_id, datetime.datetime.now(), total, metodo_pago, 'pendiente'])

                    cursor.execute("SELECT LAST_INSERT_ID()")
                    compra_id = cursor.fetchone()[0]

                    # Crear registro de pago
                    cursor.execute("""
                        INSERT INTO Pagos (id_compra, fecha_pago, monto, metodo, estado)
                        VALUES (%s, %s, %s, %s, %s)
                    """, [compra_id, datetime.datetime.now(), total, metodo_pago, 'exitoso'])

                    # Crear boletos sin categoría
                    for i in range(cantidad):
                        cursor.execute("""
                            INSERT INTO Boletos (id_evento, id_categoria, precio, estado, id_cliente)
                            VALUES (%s, %s, %s, %s, %s)
                        """, [evento_id, None, precio_unitario, 'pagado', usuario_id])

                        cursor.execute("SELECT LAST_INSERT_ID()")
                        boleto_id = cursor.fetchone()[0]

                        codigo_qr = generar_codigo_qr(boleto_id)
                        cursor.execute("""
                            UPDATE Boletos SET codigo = %s WHERE id_boleto = %s
                        """, [codigo_qr, boleto_id])

                        cursor.execute("""
                            INSERT INTO Detalle_Compras (id_compra, id_boleto, precio)
                            VALUES (%s, %s, %s)
                        """, [compra_id, boleto_id, precio_unitario])

                    cursor.execute("""
                        UPDATE Compras SET estado = 'completado' WHERE id_compra = %s
                    """, [compra_id])

            messages.success(request, 'Pago procesado correctamente')
            return redirect('pagos:confirmacion', compra_id=compra_id)

        except Exception as e:
            messages.error(request, f'Error al procesar pago: {str(e)}')

    context = {
        'evento_nombre': evento_nombre,
        'categoria_nombre': None,
        'cantidad': cantidad,
        'precio_unitario': precio_unitario,
        'total': total,
    }

    return render(request, 'pagos/procesar.html', context)

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
import datetime


def comprar_boleto(request, evento_id):

    if 'usuario_id' not in request.session:
        messages.error(request, 'Debes iniciar sesión para comprar boletos')
        return redirect('usuarios:login')
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT e.id_evento, e.nombre, e.descripcion, e.fecha_inicio, e.lugar
            FROM Eventos e
            WHERE e.id_evento = %s AND e.estado = 'activo'
        """, [evento_id])
        
        evento_row = cursor.fetchone()
        if not evento_row:
            messages.error(request, 'Evento no disponible')
            return redirect('eventos:lista')
        
        evento = {
            'id': evento_row[0],
            'nombre': evento_row[1],
            'descripcion': evento_row[2],
            'fecha_inicio': evento_row[3],
            'lugar': evento_row[4],
        }
        
        cursor.execute("""
            SELECT ce.id_categoria, ce.nombre_categoria, ce.precio, ce.cantidad_asientos
            FROM Categorias_Evento ce
            WHERE ce.id_evento = %s
        """, [evento_id])
        
        categorias = []
        for row in cursor.fetchall():
            categorias.append({
                'id': row[0],
                'nombre': row[1],
                'precio': row[2],
                'cantidad_asientos': row[3],
            })
    
    if request.method == 'POST':
        categoria_id = request.POST.get('categoria')
        cantidad = int(request.POST.get('cantidad', 1))
        
        return redirect('pagos:procesar', evento_id=evento_id, categoria_id=categoria_id, cantidad=cantidad)
    
    context = {
        'evento': evento,
        'categorias': categorias,
    }
    
    return render(request, 'boletos/comprar.html', context)


def mis_boletos(request):
    """
    Vista para ver los boletos del usuario
    """
    if 'usuario_id' not in request.session:
        return redirect('usuarios:login')
    
    usuario_id = request.session['usuario_id']
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT b.id_boleto, b.codigo_qr, b.fecha_compra, b.estado,
                   e.nombre as evento_nombre, e.fecha_inicio, e.lugar,
                   ce.nombre_categoria, ce.precio
            FROM Boletos b
            INNER JOIN Eventos e ON b.id_evento = e.id_evento
            LEFT JOIN Categorias_Evento ce ON b.id_categoria = ce.id_categoria
            INNER JOIN Compras c ON b.id_boleto = c.id_compra
            WHERE c.id_cliente = %s
            ORDER BY b.fecha_compra DESC
        """, [usuario_id])
        
        boletos = []
        for row in cursor.fetchall():
            boletos.append({
                'id': row[0],
                'codigo_qr': row[1],
                'fecha_compra': row[2],
                'estado': row[3],
                'evento_nombre': row[4],
                'evento_fecha': row[5],
                'evento_lugar': row[6],
                'categoria': row[7],
                'precio': row[8],
            })
    
    return render(request, 'boletos/mis_boletos.html', {'boletos': boletos})


def validar_boleto(request):
    """
    Vista para validar boletos con código QR
    """
    if request.method == 'POST':
        codigo_qr = request.POST.get('codigo_qr')
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT b.id_boleto, b.estado, e.nombre as evento_nombre,
                       ce.nombre_categoria
                FROM Boletos b
                INNER JOIN Eventos e ON b.id_evento = e.id_evento
                LEFT JOIN Categorias_Evento ce ON b.id_categoria = ce.id_categoria
                WHERE b.codigo_qr = %s
            """, [codigo_qr])
            
            boleto_row = cursor.fetchone()
            
            if not boleto_row:
                messages.error(request, 'Boleto no encontrado')
            elif boleto_row[1] == 'usado':
                messages.warning(request, 'Este boleto ya fue usado')
            elif boleto_row[1] == 'vendido':
                
                cursor.execute("""
                    UPDATE Boletos SET estado = 'usado' WHERE id_boleto = %s
                """, [boleto_row[0]])
                
                messages.success(request, f'Boleto válido: {boleto_row[2]} - {boleto_row[3]}')
            else:
                messages.error(request, 'Boleto no válido')
    
    return render(request, 'boletos/validar.html')

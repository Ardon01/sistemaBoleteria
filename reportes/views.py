"""
Vistas para el módulo de reportes
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection


def historial_compras(request):
    """
    Vista para ver el historial de compras del usuario
    """
    if 'usuario_id' not in request.session:
        return redirect('usuarios:login')
    
    usuario_id = request.session['usuario_id']
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT c.id_compra, c.fecha_compra, c.total,
                   p.metodo, p.estado,
                   COUNT(dc.id_boleto) as cantidad_boletos
            FROM Compras c
            INNER JOIN Pagos p ON c.id_compra = p.id_compra
            LEFT JOIN Detalle_Compras dc ON c.id_compra = dc.id_compra
            WHERE c.id_cliente = %s
            GROUP BY c.id_compra
            ORDER BY c.fecha_compra DESC
        """, [usuario_id])
        
        compras = []
        for row in cursor.fetchall():
            compras.append({
                'id': row[0],
                'fecha': row[1],
                'total': row[2],
                'metodo_pago': row[3],
                'estado': row[4],
                'cantidad_boletos': row[5],
            })
    
    return render(request, 'reportes/historial.html', {'compras': compras})


def reporte_ventas(request):
    """
    Vista para ver reporte de ventas (solo vendedores y admins)
    """
    if 'usuario_id' not in request.session:
        return redirect('usuarios:login')
    
    if request.session.get('usuario_rol') not in ['vendedor', 'administrador']:
        messages.error(request, 'No tienes permisos para ver este reporte')
        return redirect('eventos:lista')
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT e.nombre, COUNT(b.id_boleto) as boletos_vendidos,
                   SUM(b.precio) as total_ventas
            FROM Eventos e
            LEFT JOIN Boletos b ON e.id_evento = b.id_evento AND b.estado = 'pagado'
            GROUP BY e.id_evento
            ORDER BY total_ventas DESC
        """)
        
        ventas = []
        for row in cursor.fetchall():
            ventas.append({
                'evento': row[0],
                'boletos_vendidos': row[1] or 0,
                'total_ventas': row[2] or 0,
            })
    
    return render(request, 'reportes/ventas.html', {'ventas': ventas})

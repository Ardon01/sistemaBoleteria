from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.views.decorators.http import require_http_methods
import datetime


def lista_eventos(request):
   
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT e.id_evento, e.nombre, e.descripcion, e.fecha_inicio, 
                   e.fecha_fin, e.lugar, e.estado, v.nombre_negocio
            FROM Eventos e
            LEFT JOIN Vendedores v ON e.id_vendedor = v.id_usuario
            WHERE e.estado = 'activo'
            ORDER BY e.fecha_inicio DESC
        """)
        
        eventos = []
        for row in cursor.fetchall():
            eventos.append({
                'id': row[0],
                'nombre': row[1],
                'descripcion': row[2],
                'fecha_inicio': row[3],
                'fecha_fin': row[4],
                'lugar': row[5],
                'estado': row[6],
                'vendedor': row[7],
            })
    
    return render(request, 'eventos/lista.html', {'eventos': eventos})


def detalle_evento(request, evento_id):
 
    with connection.cursor() as cursor:
        
        cursor.execute("""
            SELECT e.id_evento, e.nombre, e.descripcion, e.fecha_inicio, 
                   e.fecha_fin, e.lugar, e.tipo_evento, e.creado_en, 
                   e.estado, v.nombre_negocio
            FROM Eventos e
            LEFT JOIN Vendedores v ON e.id_vendedor = v.id_usuario
            WHERE e.id_evento = %s
        """, [evento_id])
        
        evento_row = cursor.fetchone()
        if not evento_row:
            messages.error(request, 'Evento no encontrado')
            return redirect('eventos:lista')
        
        evento = {
            'id': evento_row[0],
            'nombre': evento_row[1],
            'descripcion': evento_row[2],
            'fecha_inicio': evento_row[3],
            'fecha_fin': evento_row[4],
            'lugar': evento_row[5],
            'tipo_evento': evento_row[6],
            'creado_en': evento_row[7],
            'estado': evento_row[8],
            'vendedor': evento_row[9],
        }
        
        cursor.execute("""
            SELECT ce.id_categoria, ce.nombre_categoria, ce.precio, ce.cantidad_asientos
            FROM Categorias_Evento ce
            WHERE ce.id_evento = %s
        """, [evento_id])
        
        categorias = []
        for row in cursor.fetchall():

            cursor.execute("""
                SELECT COUNT(*) FROM Boletos 
                WHERE id_evento = %s AND estado = 'vendido'
            """, [evento_id])
            
            vendidos = cursor.fetchone()[0]
            disponibles = row[3] - vendidos
            
            categorias.append({
                'id': row[0],
                'nombre': row[1],
                'precio': row[2],
                'cantidad_asientos': row[3],
                'disponibles': disponibles,
            })
    
    context = {
        'evento': evento,
        'categorias': categorias,
    }
    
    return render(request, 'eventos/detalle.html', context)


def crear_evento(request):

    if 'usuario_id' not in request.session:
        messages.error(request, 'Debes iniciar sesión')
        return redirect('usuarios:login')
    
    if request.session.get('usuario_rol') not in ['vendedor', 'administrador']:
        messages.error(request, 'No tienes permisos para crear eventos')
        return redirect('eventos:lista')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        lugar = request.POST.get('lugar')
        tipo_evento = request.POST.get('tipo_evento')
        
        try:
            with connection.cursor() as cursor:
              
                cursor.execute("""
                    SELECT id_usuario FROM Vendedores WHERE id_usuario = %s
                """, [request.session['usuario_id']])
                
                vendedor = cursor.fetchone()
                vendedor_id = vendedor[0] if vendedor else request.session['usuario_id']
                
                cursor.execute("""
                    INSERT INTO Eventos (nombre, descripcion, fecha_inicio, fecha_fin, 
                                       lugar, id_vendedor, tipo_evento, creado_en, estado)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [nombre, descripcion, fecha_inicio, fecha_fin, lugar, 
                      vendedor_id, tipo_evento, datetime.datetime.now(), 'activo'])
                
            messages.success(request, 'Evento creado correctamente')
            return redirect('eventos:lista')
            
        except Exception as e:
            messages.error(request, f'Error al crear evento: {str(e)}')
    
    return render(request, 'eventos/crear.html')


def editar_evento(request, evento_id):
    """
    Vista para editar un evento existente
    """
    if 'usuario_id' not in request.session:
        return redirect('usuarios:login')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        lugar = request.POST.get('lugar')
        estado = request.POST.get('estado')
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE Eventos 
                    SET nombre = %s, descripcion = %s, fecha_inicio = %s, 
                        fecha_fin = %s, lugar = %s, estado = %s
                    WHERE id_evento = %s
                """, [nombre, descripcion, fecha_inicio, fecha_fin, 
                      lugar, estado, evento_id])
                
            messages.success(request, 'Evento actualizado correctamente')
            return redirect('eventos:detalle', evento_id=evento_id)
            
        except Exception as e:
            messages.error(request, f'Error al actualizar evento: {str(e)}')
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id_evento, nombre, descripcion, fecha_inicio, fecha_fin, 
                   lugar, tipo_evento, estado
            FROM Eventos
            WHERE id_evento = %s
        """, [evento_id])
        
        evento_row = cursor.fetchone()
        if not evento_row:
            messages.error(request, 'Evento no encontrado')
            return redirect('eventos:lista')
        
        evento = {
            'id': evento_row[0],
            'nombre': evento_row[1],
            'descripcion': evento_row[2],
            'fecha_inicio': evento_row[3],
            'fecha_fin': evento_row[4],
            'lugar': evento_row[5],
            'tipo_evento': evento_row[6],
            'estado': evento_row[7],
        }
    
    return render(request, 'eventos/editar.html', {'evento': evento})


@require_http_methods(["POST"])
def eliminar_evento(request, evento_id):
    """
    Vista para eliminar (desactivar) un evento
    """
    if 'usuario_id' not in request.session:
        return redirect('usuarios:login')
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE Eventos SET estado = 'cancelado' WHERE id_evento = %s
            """, [evento_id])
            
        messages.success(request, 'Evento cancelado correctamente')
    except Exception as e:
        messages.error(request, f'Error al cancelar evento: {str(e)}')
    
    return redirect('eventos:lista')

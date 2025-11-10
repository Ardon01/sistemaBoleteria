"""
Vistas para el módulo de usuarios y autenticación
Todas las operaciones usan SQL puro sin ORM
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.http import require_http_methods
import datetime


def registro(request):
    """
    Vista para registro de nuevos usuarios
    """
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')
        telefono = request.POST.get('telefono', '')
        direccion = request.POST.get('direccion', '')
        tipo_usuario = request.POST.get('tipo_usuario', 'cliente')
        
        # Validar que el correo no exista
        with connection.cursor() as cursor:
            cursor.execute("SELECT id_usuario FROM Usuarios WHERE correo = %s", [correo])
            if cursor.fetchone():
                messages.error(request, 'El correo ya está registrado')
                return render(request, 'usuarios/registro.html')
        
        try:
            with connection.cursor() as cursor:
                # Insertar en tabla Usuarios
                cursor.execute("""
                    INSERT INTO Usuarios (nombre, primer_nombre, segundo_nombre, correo, contrasena, 
                                        telefono, direccion, fecha_registro, estado)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [nombre, apellido, '', correo, make_password(contrasena), 
                      telefono, direccion, datetime.datetime.now(), 'activo'])
                
                # Obtener el ID del usuario recién creado
                cursor.execute("SELECT LAST_INSERT_ID()")
                usuario_id = cursor.fetchone()[0]
                
                # Obtener ID del rol por defecto (cliente = 1)
                cursor.execute("SELECT id_rol FROM Roles WHERE nombre_rol = %s", [tipo_usuario])
                rol_result = cursor.fetchone()
                rol_id = rol_result[0] if rol_result else 1
                
                # Asignar rol al usuario
                cursor.execute("""
                    INSERT INTO Usuarios_Roles (id_usuario, id_rol)
                    VALUES (%s, %s)
                """, [usuario_id, rol_id])
                
                # Crear registro en tabla Clientes
                if tipo_usuario == 'cliente':
                    cursor.execute("""
                        INSERT INTO Clientes (id_usuario, primer_nombre, segundo_nombre, 
                                            primer_apellido, segundo_apellido, correo, 
                                            telefono, direccion)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, [usuario_id, nombre, '', apellido, '', correo, telefono, direccion])
                
            messages.success(request, 'Registro exitoso. Ahora puedes iniciar sesión')
            return redirect('usuarios:login')
            
        except Exception as e:
            messages.error(request, f'Error al registrar usuario: {str(e)}')
            return render(request, 'usuarios/registro.html')
    
    return render(request, 'usuarios/registro.html')


def login_view(request):
    """
    Vista para inicio de sesión
    """
    if request.method == 'POST':
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')
        
        with connection.cursor() as cursor:
            # Buscar usuario por correo
            cursor.execute("""
                SELECT u.id_usuario, u.correo, u.contrasena, u.nombre, u.estado,
                       r.nombre_rol
                FROM Usuarios u
                LEFT JOIN Usuarios_Roles ur ON u.id_usuario = ur.id_usuario
                LEFT JOIN Roles r ON ur.id_rol = r.id_rol
                WHERE u.correo = %s
            """, [correo])
            
            usuario = cursor.fetchone()
            
            if usuario and check_password(contrasena, usuario[2]):
                if usuario[4] != 'activo':
                    messages.error(request, 'Tu cuenta está inactiva')
                    return render(request, 'usuarios/login.html')
                
                # Guardar datos en sesión
                request.session['usuario_id'] = usuario[0]
                request.session['usuario_correo'] = usuario[1]
                request.session['usuario_nombre'] = usuario[3]
                request.session['usuario_rol'] = usuario[5] or 'cliente'
                
                messages.success(request, f'Bienvenido {usuario[3]}')
                return redirect('eventos:lista')
            else:
                messages.error(request, 'Correo o contraseña incorrectos')
    
    return render(request, 'usuarios/login.html')


def logout_view(request):
    """
    Vista para cerrar sesión
    """
    request.session.flush()
    messages.success(request, 'Has cerrado sesión correctamente')
    return redirect('usuarios:login')


def perfil(request):
    """
    Vista para ver y editar el perfil del usuario
    """
    if 'usuario_id' not in request.session:
        return redirect('usuarios:login')
    
    usuario_id = request.session['usuario_id']
    
    if request.method == 'POST':
        # Actualizar datos del usuario
        nombre = request.POST.get('nombre')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE Usuarios 
                    SET nombre = %s, telefono = %s, direccion = %s
                    WHERE id_usuario = %s
                """, [nombre, telefono, direccion, usuario_id])
                
            messages.success(request, 'Perfil actualizado correctamente')
        except Exception as e:
            messages.error(request, f'Error al actualizar perfil: {str(e)}')
    
    # Obtener datos del usuario
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT u.id_usuario, u.nombre, u.primer_nombre, u.correo, 
                   u.telefono, u.direccion, u.fecha_registro, r.nombre_rol
            FROM Usuarios u
            LEFT JOIN Usuarios_Roles ur ON u.id_usuario = ur.id_usuario
            LEFT JOIN Roles r ON ur.id_rol = r.id_rol
            WHERE u.id_usuario = %s
        """, [usuario_id])
        
        usuario = cursor.fetchone()
    
    context = {
        'usuario': {
            'id': usuario[0],
            'nombre': usuario[1],
            'apellido': usuario[2],
            'correo': usuario[3],
            'telefono': usuario[4],
            'direccion': usuario[5],
            'fecha_registro': usuario[6],
            'rol': usuario[7],
        }
    }
    
    return render(request, 'usuarios/perfil.html', context)

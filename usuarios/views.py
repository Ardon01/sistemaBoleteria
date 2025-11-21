
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.http import require_http_methods
import datetime


def registro(request):
    if request.method == 'POST':

        dni_usuario = request.POST.get('dni_usuario', '').strip()
        primer_nombre = request.POST.get('primer_nombre', '').strip()
        segundo_nombre = request.POST.get('segundo_nombre', '').strip()
        primer_apellido = request.POST.get('primer_apellido', '').strip()
        segundo_apellido = request.POST.get('segundo_apellido', '').strip()
        correo = request.POST.get('correo', '').strip()
        contrasena = request.POST.get('contrasena', '')
        telefono = request.POST.get('telefono', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        fecha_registro = datetime.datetime.now()
        
        if not dni_usuario:
            messages.error(request, 'El DNI/Cédula es obligatorio')
            return render(request, 'usuarios/registro.html')
        
        if not dni_usuario.isdigit():
            messages.error(request, 'El DNI/Cédula debe contener solo números')
            return render(request, 'usuarios/registro.html')
            
        if not primer_nombre or not primer_apellido or not correo or not contrasena:
            messages.error(request, 'Todos los campos marcados con * son obligatorios')
            return render(request, 'usuarios/registro.html')

        with connection.cursor() as cursor:
            cursor.execute("SELECT id_usuario FROM usuarios WHERE dni_usuario = %s", [dni_usuario])
            if cursor.fetchone():
                messages.error(request, 'El DNI/Cédula ya está registrado')
                return render(request, 'usuarios/registro.html')
            
            cursor.execute("SELECT id_usuario FROM usuarios WHERE correo = %s", [correo])
            if cursor.fetchone():
                messages.error(request, 'El correo ya está registrado')
                return render(request, 'usuarios/registro.html')
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO usuarios (
                        dni_usuario, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido,
                        correo, contrasena, telefono, direccion, fecha_registro, estado
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    dni_usuario,
                    primer_nombre, 
                    segundo_nombre, 
                    primer_apellido, 
                    segundo_apellido,
                    correo, 
                    make_password(contrasena), 
                    telefono, 
                    direccion, 
                    datetime.datetime.now(), 
                    'activo'
                ])
                
                usuario_id = cursor.lastrowid
                
                cursor.execute("SELECT id_rol FROM roles WHERE nombre_rol = 'cliente'")
                rol_result = cursor.fetchone()
                
                if rol_result:
                    rol_id = rol_result[0]
                else:
                    cursor.execute("INSERT INTO roles (nombre_rol) VALUES ('cliente')")
                    rol_id = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO usuarios_roles (id_usuario, id_rol)
                    VALUES (%s, %s)
                """, [usuario_id, rol_id])
                
                # Insertar en Clientes (tabla solo guarda id_usuario según el esquema)
                cursor.execute("""
                    INSERT INTO Clientes (id_usuario) VALUES (%s)
                """, [usuario_id])
                
                messages.success(request, 'Registro exitoso. Ahora puedes iniciar sesión')
                return redirect('usuarios:login')
            
        except Exception as e:
            messages.error(request, f'Error al registrar usuario: {str(e)}')
            return render(request, 'usuarios/registro.html')
    
    return render(request, 'usuarios/registro.html')

def login_view(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.id_usuario, u.correo, u.contrasena, 
                       CONCAT(u.primer_nombre, ' ', u.primer_apellido) as nombre_completo,
                       u.estado, r.nombre_rol
                FROM usuarios u
                LEFT JOIN usuarios_roles ur ON u.id_usuario = ur.id_usuario
                LEFT JOIN roles r ON ur.id_rol = r.id_rol
                WHERE u.correo = %s
            """, [correo])
            
            usuario = cursor.fetchone()
            
            if usuario and check_password(contrasena, usuario[2]):
                if usuario[4] != 'activo':
                    messages.error(request, 'Tu cuenta está inactiva')
                    return render(request, 'usuarios/login.html')
                
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
        primer_nombre = request.POST.get('primer_nombre')
        segundo_nombre = request.POST.get('segundo_nombre', '')
        primer_apellido = request.POST.get('primer_apellido')
        segundo_apellido = request.POST.get('segundo_apellido', '')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE usuarios 
                    SET primer_nombre = %s, segundo_nombre = %s, 
                        primer_apellido = %s, segundo_apellido = %s,
                        telefono = %s, direccion = %s
                    WHERE id_usuario = %s
                """, [primer_nombre, segundo_nombre, primer_apellido, 
                      segundo_apellido, telefono, direccion, usuario_id])
                
            messages.success(request, 'Perfil actualizado correctamente')
        except Exception as e:
            messages.error(request, f'Error al actualizar perfil: {str(e)}')
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT u.id_usuario, u.primer_nombre, u.segundo_nombre, 
                   u.primer_apellido, u.segundo_apellido, u.correo, 
                   u.telefono, u.direccion, u.fecha_registro, r.nombre_rol
            FROM usuarios u
            LEFT JOIN usuarios_roles ur ON u.id_usuario = ur.id_usuario
            LEFT JOIN roles r ON ur.id_rol = r.id_rol
            WHERE u.id_usuario = %s
        """, [usuario_id])
        
        usuario = cursor.fetchone()
    
    context = {
        'usuario': {
            'id': usuario[0],
            'primer_nombre': usuario[1],
            'segundo_nombre': usuario[2],
            'primer_apellido': usuario[3],
            'segundo_apellido': usuario[4],
            'correo': usuario[5],
            'telefono': usuario[6],
            'direccion': usuario[7],
            'fecha_registro': usuario[8],
            'rol': usuario[9],
        }
    }
    
    return render(request, 'usuarios/perfil.html', context)
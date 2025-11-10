# Sistema de Boletería de Eventos

Sistema completo de gestión de boletos para eventos desarrollado con Django y MySQL usando consultas SQL puras (sin ORM).

## Requisitos

- Python 3.8+
- MySQL 8.0+
- pip

## Instalación

1. Clonar el repositorio
2. Crear un entorno virtual:
\`\`\`bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
\`\`\`

3. Instalar dependencias:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. Configurar base de datos MySQL:
   - Crear base de datos: `CREATE DATABASE boleteria_eventos;`
   - Ejecutar el script SQL proporcionado en `scripts/query_Base_de_Datos.sql`
   - Configurar credenciales en `boleteria/settings.py`

5. Configurar variables de entorno en `boleteria/settings.py`:
   - DB_NAME
   - DB_USER
   - DB_PASSWORD
   - DB_HOST
   - DB_PORT

6. Ejecutar el servidor:
\`\`\`bash
python manage.py runserver
\`\`\`

7. Acceder a: http://localhost:8000

## Estructura del Proyecto

\`\`\`
boleteria_eventos/
├── boleteria/          # Configuración principal
├── usuarios/           # Gestión de usuarios y autenticación
├── eventos/            # CRUD de eventos
├── boletos/            # Gestión de boletos
├── pagos/              # Procesamiento de pagos
├── reportes/           # Reportes e historial
├── templates/          # Plantillas HTML
├── static/             # Archivos estáticos
└── scripts/            # Scripts SQL
\`\`\`

## Módulos

1. **Usuarios**: Registro, login, roles (cliente, vendedor, admin)
2. **Eventos**: CRUD de eventos, categorías
3. **Boletos**: Compra y gestión de boletos
4. **Pagos**: Simulación de pagos y generación de QR
5. **Reportes**: Historial de compras y validación de acceso

## Usuarios de Prueba

Se crearán automáticamente con el script SQL inicial.

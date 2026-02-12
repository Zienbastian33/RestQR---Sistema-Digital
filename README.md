# RestQR - Sistema Digital de Menú y Pedidos

RestQR es una aplicación web moderna diseñada para restaurantes que permite la gestión digital de menús y pedidos a través de códigos QR. El sistema facilita tanto los pedidos locales como los pedidos para delivery, mejorando la eficiencia operativa del restaurante.

## 🚀 Características Principales

### 📱 Menú Digital
- **Acceso vía QR**: Cada mesa tiene su código QR único
- **Menú Interactivo**: Visualización atractiva de platos con imágenes
- **Categorías**: Organización clara del menú (Handrolls, Gohan, Bebidas, Extras)
- **Carrito de Compras**: Sistema intuitivo para agregar y modificar pedidos
- **Sesiones Individuales**: Cada mesa/cliente tiene su propio carrito de compras

### 👨‍💼 Panel de Administración
- **Generador de QR**:
  - Creación de códigos QR únicos por mesa
  - Gestión de tokens y códigos de activación
  - Vista de URLs completas para cada QR
- **Gestión de Mesas**:
  - Activación/desactivación de mesas
  - Monitoreo de sesiones activas
  - Control de estado de las mesas

### 👨‍🍳 Vista de Cocina
- **Panel Dividido**:
  - Columna para pedidos locales
  - Columna para pedidos delivery (en desarrollo)
- **Gestión de Pedidos**:
  - Visualización en tiempo real
  - Detalles completos de cada pedido
  - Sistema de marcado de pedidos completados
- **Actualizaciones Automáticas**:
  - Refresco automático cada 30 segundos
  - Reloj en tiempo real
  - Eliminación automática de pedidos completados

### 🔒 Seguridad
- Validación de tokens para acceso al menú
- Sistema de códigos de activación para mesas
- Protección de rutas administrativas
- Sesiones individuales para cada cliente

## 🔄 Historial de Desarrollo

### Última Sesión - Correcciones Críticas (Febrero 2026)

#### Implementación de Mejoras Críticas del Sistema
Se completaron las siguientes tareas del plan de correcciones críticas:

1. **Gestión de Tokens QR Mejorada**
   - Implementación de reutilización de tokens existentes para evitar duplicados
   - Función `get_or_create_table_token` para gestión eficiente de tokens
   - Validación de unicidad de tokens activos por mesa
   - Tests de propiedades para garantizar idempotencia

2. **Seguimiento de Número de Mesa en Pedidos**
   - Función helper `create_order_from_token` para extracción automática del número de mesa
   - Validación de tokens activos y no expirados antes de crear pedidos
   - Actualización de vista de cocina para mostrar números de mesa
   - Manejo de pedidos legacy sin número de mesa

3. **Consolidación del Carrito de Compras**
   - Implementación de `CartManager` como única fuente de verdad
   - localStorage como almacenamiento persistente del carrito
   - Eliminación de código duplicado en templates
   - Sincronización automática entre estado y UI

4. **Carga Dinámica de Menú desde Base de Datos**
   - Eliminación de menús hardcodeados en templates
   - Consulta dinámica de items desde la tabla MenuItem
   - Agrupación automática por categorías
   - Renderizado con Jinja2 para flexibilidad total

5. **Página de Confirmación de Pedidos**
   - Nueva ruta `/order/confirmation/<order_id>`
   - Template con detalles completos del pedido
   - Cálculo automático de totales
   - Redirección automática después de enviar pedido

6. **Tests de Integración Completos**
   - Test de flujo completo: QR → menú → carrito → pedido → confirmación
   - Test de actualización de cocina con SocketIO
   - Test de generación de QR con reutilización de tokens
   - Validación de compatibilidad hacia atrás

### Sesión Anterior (10/12/2024)

#### Mejoras en la Gestión de Mesas
1. **Sistema de Activación de Mesas**
   - Implementación de tokens únicos por mesa
   - Códigos de activación de 6 dígitos
   - Validación de sesiones activas
   - Control de duración de sesiones (1-4 horas)

2. **Panel de Administración Mejorado**
   - Vista en tiempo real de mesas activas
   - Interfaz para activación/desactivación de mesas
   - Visualización de tiempos de inicio y fin de sesión
   - Actualización automática cada 30 segundos

3. **Vista de Cocina**
   - Panel dividido para pedidos locales y delivery
   - Actualización en tiempo real de pedidos
   - Sistema de marcado de pedidos completados
   - Filtrado automático por tipo de pedido

4. **Correcciones y Optimizaciones**
   - Arreglo del sistema de carrito por sesión
   - Corrección de errores en la desactivación de mesas
   - Mejora en el manejo de errores y mensajes al usuario
   - Optimización de consultas a la base de datos

### Stack Tecnológico Actualizado
- **Backend**: Flask 2.0.1
- **ORM**: Flask-SQLAlchemy 2.5.1
- **Migraciones**: Flask-Migrate 3.1.0
- **Frontend**: Bootstrap 5, JavaScript vanilla
- **Base de Datos**: SQLAlchemy con SQLite
- **Autenticación**: Sistema personalizado de tokens

### Estructura de la Base de Datos
```sql
# Principales Modelos

MenuItem:
  - id (PK)
  - name
  - description
  - price
  - category
  - available (boolean)

Order:
  - id (PK)
  - table_number
  - status
  - timestamp
  - total
  - is_delivery
  - delivery_address
  - customer_phone

TableToken:
  - id (PK)
  - table_number
  - token
  - activation_code
  - session_active
  - session_start
  - session_end
  - is_active
  - created_at
  - last_used
```



## 🚀 Instalación y Configuración

### Desarrollo Local

1. Clonar el repositorio:
```bash
git clone [url-del-repositorio]
cd RestQR---Sistema-Digital
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Inicializar la base de datos:
```bash
flask db upgrade
python fix_database.py  # Poblar la base de datos con items de menú de ejemplo
```

5. Ejecutar la aplicación:
```bash
python run.py
```

### Despliegue en Producción

Para desplegar en Vercel (recomendado):

```bash
# Opción 1: Script automático (Windows)
deploy.bat

# Opción 2: Script automático (Mac/Linux)
chmod +x deploy.sh
./deploy.sh
```

Ver [QUICK_START.md](QUICK_START.md) para guía rápida de 5 minutos.

Ver [DEPLOYMENT.md](DEPLOYMENT.md) para guía completa de despliegue.

## 🎯 Uso del Sistema

### Para Clientes
1. Escanear el código QR de la mesa
2. Navegar por el menú digital
3. Agregar items al carrito
4. Confirmar el pedido

### Para Administradores
1. Acceder al panel de administración
2. Generar códigos QR para las mesas
3. Monitorear pedidos activos
4. Gestionar estados de las mesas

### Para la Cocina
1. Acceder a la vista de cocina
2. Visualizar pedidos entrantes
3. Ver detalles de cada pedido
4. Marcar pedidos como completados

## 📝 Notas Adicionales
- El sistema se ha diseniado por defecto para un restaurante de sushi pero es adaptable a cualquier tipo de restaurante
- Interfaz responsive que se adapta a diferentes dispositivos
- Sistema de actualización en tiempo real para la cocina
- Diseño moderno y fácil de usar

## 🔧 Solución de Problemas

### El menú no muestra items
Si el menú aparece vacío para los clientes, la base de datos necesita ser poblada con items:

```bash
# Activar el entorno virtual
venv\Scripts\activate  # Windows

# Poblar la base de datos
python init_db.py
```

Esto creará items de ejemplo en las categorías: Handrolls, Sushi, Bebidas y Extras.

### Verificar items en la base de datos
```bash
python check_db.py
```

Este script mostrará cuántos items hay en la base de datos y sus detalles.

## 🤝 Contribuir
Las contribuciones son bienvenidas. Por favor, abre un issue primero para discutir los cambios que te gustaría realizar.

## 🌐 Despliegue

### Despliegue Rápido en Vercel

Tu código ya está en GitHub y listo para desplegar en Vercel:

**Repositorio:** https://github.com/Zienbastian33/RestQR---Sistema-Digital

#### Pasos para Desplegar:

1. **Ir a Vercel:**
   - Visita https://vercel.com
   - Inicia sesión con GitHub

2. **Importar Proyecto:**
   - Click "Add New..." → "Project"
   - Busca "RestQR---Sistema-Digital"
   - Click "Import"

3. **Configurar Variables de Entorno:**
   
   En la sección "Environment Variables", agrega:
   
   ```
   SECRET_KEY = [generar clave segura - ver abajo]
   FLASK_ENV = production
   ```
   
   Para generar SECRET_KEY, ejecuta en tu terminal:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

4. **Desplegar:**
   - Click "Deploy"
   - Espera 2-3 minutos
   - ¡Tu app estará en línea!

5. **Inicializar Base de Datos:**
   
   Después del despliegue, ejecuta localmente:
   ```bash
   python fix_database.py
   ```

#### Actualizaciones Futuras:

Cada vez que hagas cambios y los subas a GitHub, Vercel desplegará automáticamente:

```bash
git add .
git commit -m "Tus cambios"
git push origin main
```

### Características del Despliegue

- ✅ Despliegue automático desde GitHub
- ✅ HTTPS incluido
- ✅ CDN global
- ✅ Escalado automático
- ✅ Dominio personalizado disponible

### URL del Proyecto

- **GitHub:** https://github.com/Zienbastian33/RestQR---Sistema-Digital
- **Vercel:** (se generará después del despliegue)

## 📄 Licencia
Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE.md para más detalles.

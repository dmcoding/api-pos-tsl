# POS API - Sistema de Punto de Venta

API REST desarrollada con FastAPI para un sistema de punto de venta (POS) que incluye gestión de usuarios, productos y transacciones.

## Características

- **Autenticación JWT**: Sistema de autenticación seguro con tokens JWT
- **Gestión de Usuarios**: CRUD completo con roles de usuario y administrador
- **Gestión de Productos**: CRUD con control de stock y categorías
- **Transacciones**: Sistema completo de ventas con control de stock automático
- **Documentación Automática**: Swagger UI y ReDoc integrados
- **Base de Datos**: SQLAlchemy ORM con soporte para PostgreSQL y SQLite
- **Modular**: Arquitectura modular con routers separados

## Estructura del Proyecto

```
api-pos-mono/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación principal
│   ├── config.py            # Configuración
│   ├── database.py          # Configuración de base de datos
│   ├── models.py            # Modelos de SQLAlchemy
│   ├── schemas.py           # Esquemas de Pydantic
│   ├── auth.py              # Sistema de autenticación
│   └── routers/             # Routers modulares
│       ├── __init__.py
│       ├── auth.py          # Rutas de autenticación
│       ├── users.py         # Rutas de usuarios
│       ├── products.py      # Rutas de productos
│       └── transactions.py  # Rutas de transacciones
├── requirements.txt         # Dependencias
├── env.example             # Variables de entorno de ejemplo
└── README.md               # Este archivo
```

## Instalación

1. **Clonar el repositorio**:

```bash
git clone <repository-url>
cd api-pos-mono
```

2. **Crear entorno virtual**:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**:

```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**:

```bash
cp env.example .env
# Editar .env con tus configuraciones
```

## Configuración

### Variables de Entorno

Crea un archivo `.env` con las siguientes variables:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/pos_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Base de Datos

Por defecto, la aplicación usa SQLite para desarrollo. Para producción, se recomienda PostgreSQL.

**SQLite (desarrollo)**:

```env
DATABASE_URL=sqlite:///./pos.db
```

**PostgreSQL (producción)**:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/pos_db
```

## Uso

### Ejecutar la aplicación

```bash
# Desarrollo
uvicorn app.main:app --reload

# Producción
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Acceder a la documentación

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Usuario por defecto

Al iniciar la aplicación por primera vez, se crea automáticamente un usuario administrador:

- **Username**: admin
- **Password**: admin123
- **Email**: admin@pos.com

**⚠️ Importante**: Cambia la contraseña del administrador en producción.

## Endpoints Principales

### Autenticación

- `POST /auth/login` - Iniciar sesión
- `GET /auth/me` - Obtener usuario actual

### Usuarios

- `POST /users/` - Crear usuario (admin)
- `GET /users/` - Listar usuarios (admin)
- `GET /users/{id}` - Obtener usuario
- `PUT /users/{id}` - Actualizar usuario
- `DELETE /users/{id}` - Eliminar usuario (admin)

### Productos

- `POST /products/` - Crear producto
- `GET /products/` - Listar productos (con filtros)
- `GET /products/{id}` - Obtener producto
- `PUT /products/{id}` - Actualizar producto
- `DELETE /products/{id}` - Eliminar producto (admin)
- `PATCH /products/{id}/stock` - Actualizar stock

### Transacciones

- `POST /transactions/` - Crear transacción
- `GET /transactions/` - Listar transacciones (con filtros)
- `GET /transactions/{id}` - Obtener transacción
- `PUT /transactions/{id}` - Actualizar transacción
- `DELETE /transactions/{id}` - Eliminar transacción (admin)
- `GET /transactions/user/{id}/summary` - Resumen de transacciones

## Autenticación

La API usa autenticación JWT. Para acceder a los endpoints protegidos:

1. Inicia sesión en `/auth/login`
2. Copia el `access_token` de la respuesta
3. Incluye el token en el header: `Authorization: Bearer <token>`

## Permisos

- **Usuarios normales**: Pueden ver y modificar sus propios datos y transacciones
- **Administradores**: Acceso completo a todos los endpoints y datos

## Ejemplos de Uso

### Crear un producto

```bash
curl -X POST "http://localhost:8000/products/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Coca Cola",
    "description": "Bebida gaseosa",
    "price": 2.50,
    "stock": 100,
    "sku": "COCA-001",
    "category": "Bebidas"
  }'
```

### Crear una transacción

```bash
curl -X POST "http://localhost:8000/transactions/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": "769f390e-295f-4c3f-99f9-8eaa9b3d406f",  # Store ID válido
    "pos_id": "POS-001",  # Cambia el ID del POS según tu caso
    "transaction_type": "SALE",  # Cambia el tipo de transacción si es necesario
    "transaction_number": f"TRX-{datetime.now().strftime('%Y%m%d%H%M%S')}",  # Número de transacción único basado en timestamp
    "transaction_date": datetime.now().isoformat(),  # Fecha actual en formato ISO8601
    "total_amount": 10.0,  # Agrega el total de la transacción
    "customer_external_id": "DEFAULT",  # Opcional: external_id del cliente desde el sistema externo
    "items": [
        {
            "sku": "ELEC-001",  # Cambia por el SKU de un producto válido en tu base de datos
            "quantity": 2,  # Cambia la cantidad según el caso de prueba
            "unit_price": 12.5,  # Cambia el precio unitario
            "discount": 0.0,  # Cambia el descuento si aplica
            "total": 25.0  # Cambia el total si es necesario
        },
        {
            "sku": "ELEC-002",  # Cambia por el SKU de un producto válido en tu base de datos
            "quantity": 1,  # Cambia la cantidad según el caso de prueba
            "unit_price": 12.5,  # Cambia el precio unitario
            "discount": 0.0,  # Cambia el descuento si aplica
            "total": 12.5  # Cambia el total si es necesario
        }
    ],
    "payments": [
        {
            "payment_method": "CASH",  # Cambia el método de pago si es necesario
            "amount": 5.5,  # Cambia el monto del pago
            "provider": "manual"  # Cambia el proveedor si aplica
        },
        {
            "payment_method": "CREDIT_CARD",  # Cambia el método de pago si es necesario
            "amount": 32.0,  # Cambia el monto del pago
            "provider": "Getnet"  # Cambia el proveedor si aplica
        }
    ],
    "metadata": {
        "notes": "Test transaction from simulated POS"  # Cambia las notas para otras pruebas
    }
}'
```

## Desarrollo

### Estructura de la Base de Datos

- **users**: Usuarios del sistema
- **products**: Productos disponibles
- **transactions**: Transacciones de venta
- **transaction_items**: Items de cada transacción

### Agregar Nuevas Funcionalidades

1. Crear el modelo en `models.py`
2. Crear los esquemas en `schemas.py`
3. Crear el router en `routers/`
4. Incluir el router en `main.py`

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

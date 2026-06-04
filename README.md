# BecaGo

Sistema de gestión de horas de beca para estudiantes de la Universidad del Valle de Guatemala (UVG). Permite a los becarios ver sus horas requeridas, inscribirse en tareas y llevar un seguimiento de su progreso.

## Stack

- **Backend:** Django 5.1.7 + Gunicorn
- **Base de datos:** SQLite
- **Archivos estáticos:** WhiteNoise
- **Gráficas:** Matplotlib
- **Excel:** pandas + openpyxl
- **Contenedor:** Docker + Docker Compose

## Funcionalidades

- Login / registro de usuarios
- Dashboard con gráfica de progreso de horas de beca
- Listado de tareas disponibles con inscripción
- Vista de tareas inscritas
- Resumen de horas completadas vs requeridas
- Perfil de usuario con foto y carrera universitaria

## Requisitos previos

- Docker
- Docker Compose

## Levantar el proyecto

```bash
# 1. Clonar el repo
git clone git@github.com:her24770/Becago-proyect.git
cd Becago-proyect

# 2. Copiar y configurar el compose
cp docker-compose.yml.example docker-compose.yml

# 3. Crear el archivo de variables de entorno
cp .env.example .env   # editar con valores reales

# 4. Crear archivos requeridos si no existen
touch db.sqlite3
mkdir -p media

# 5. Levantar
docker compose up -d --build
```

La app queda disponible en `http://127.0.0.1:3102` (o el puerto que hayas configurado).

## Variables de entorno (.env)

| Variable | Descripción | Ejemplo |
|---|---|---|
| `SECRET_KEY` | Clave secreta de Django | `django-insecure-...` |
| `DEBUG` | Modo debug | `False` en producción |
| `ALLOWED_HOSTS` | Hosts permitidos separados por coma | `becago.jhgo.online` |

## Archivos requeridos en el directorio raíz

| Archivo | Descripción |
|---|---|
| `db.sqlite3` | Base de datos (se crea vacía con `touch db.sqlite3`) |
| `media/` | Carpeta de archivos subidos por usuarios |
| `Horas_Beca.xlsx` | Excel con columnas `Usuario` y `Horas Beca` por becario |

> Estos archivos están en `.gitignore` — deben crearse manualmente en cada entorno.

## Estructura del proyecto

```
Becago-proyect/
├── djangocrud/          # Configuración de Django (settings, urls, wsgi)
├── tasks/               # App principal (models, views, forms, templates)
├── static/              # Archivos estáticos
├── media/               # Archivos subidos (no versionado)
├── Dockerfile
├── docker-compose.yml.example
├── entrypoint.sh        # collectstatic + migrate + gunicorn
├── requirements.txt
└── Horas_Beca.xlsx      # Excel de horas por becario (no versionado)
```

## Despliegue con Nginx (producción)

El contenedor solo escucha en `127.0.0.1:3102`. Nginx hace el proxy:

```nginx
server {
    listen 80;
    server_name becago.jhgo.online;

    location / {
        proxy_pass http://127.0.0.1:3102;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Usuario admin por defecto

Crear superusuario manualmente:

```bash
docker compose exec web python manage.py createsuperuser
```

Panel de administración disponible en `/admin/`.

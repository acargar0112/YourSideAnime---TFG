# YourSideAnime

Desarrollado por **Andrés Cárdenas García** - DAW

Es una aplicación web para gestionar tu lista personal de animes (separados por temporadas) , permite registrar los animes en 4 categorías, vistos, viendo, dropeados y whitelist (lista de espera), con sistema de puntuaciones, reseñas globales y perfil de usuario personalizable.

---

## Requesitos previos

- Debes tener [Docker](https://www.docker.com/) y [Docker Compose](https://docs.docker.com/compose/) instalados
- Git

> Para instalar git nos sirve con un par de comandos: ```sudo apt-get update``` | ```sudo apt-get install git```

---

## Configuración inicial (Con docker)

A continuación estan redactados los pasos para el uso del proyecto en local con docker.

> Es aconsejable utilizar `Debug=True` cuando utilizas el proyecto en local.

### 1. Clonar el repositorio

```
git clone https://github.com/acargar0112/YourSideAnime---TFG.git
cd YourSideAnime---TFG
```

### 2. Crear el fichero de variables de entorno

Creamos el fichero `.env` en la raíz del proyecto con la siguiente estructura:

```
# Configuración de la Base de datos (MySQL)
MYSQL_ROOT_PASSWORD=password_elegida
MYSQL_DATABASE=yoursideanime_db
MYSQL_USER=usuario_elegido
MYSQL_PASSWORD=password_elegida

# Configuración Django
SECRET_KEY=secret_key_django
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yoursideanime.duckdns.org
```

---

## Comandos de uso

Comandos necesarios para el uso del proyecto

### 1. Arrancar el proyecto

```
docker compose up --build
```

Esto debe levantar los siguientes contenedores:

- **db** -> Base de datos MySQL 8.0
- **web** -> Aplicación Django servida con Gunicorn
- **nginx** -> Servidor web que actúa como proxy inverso

Finalmente la aplicación estará disponible en `http://localhost` (Puerto 80).

### 2. Parar contenedores

```
docker compose down
```

> Si no quieres perder todos los datos nunca lo hagas con `-v`, ya que esto eliminaría todos los volumenes.

### 3. Ver logs en tiempo real

```
docker compose logs -f
```

---

## Comandos que pueden ser útiles

Esto debes ejecutarlo dentro del contenedor `web`:

```
# Abrir shell dentro del contenedor
docker compose exec web bash

# Crear un superusuario para el panel de administración
python manage.py createsuperuser

# Aplicar migraciones
python manage.py migrate

# Recopilar archivos estáticos
python manage.py collectstatic
```

El panel de administrador de Django está en `/admin/`.

---

## Instrucciones de uso del proyecto sin docker

### 1. Clonar el repositorio

```
git clone https://github.com/acargar0112/YourSideAnime---TFG.git
cd YourSideAnime---TFG
```

### 2. Crear y activar entorno virtual

```
python -m venv venv
source venv/bin/activate                # Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```
pip install -r requirements.txt
```

### 4. Crear .env en la raiz

```
USE_SQLITE=true
SECRET_KEY=secret_key_elegida
DEBUG=True
```

### 5. Crear superusuario (opcional)

```
python manage.py createsuperuser
```

### 6. Migrar y arrancar

```
python manage.py migrate
python manage.py runserver
```

Finalmente la aplicación estará disponible en `http://127.0.0.1:8000`.

## Estructura del proyecto

```
YourSideAnime/
|
|--YourSideAnime/                       # Configuración principal del proyecto Django
|   |-- settings.py                     # Ajustes globales (DB, apps instaladas, staticfiles)
|   |-- urls.py                         # Enrutamiento raíz de la aplicación
|   |-- wsgi.py                         # Punto de entrada para servidores WSGI (Gunicorn)
|   |__ asgi.py                         # Punto de entrada para servidores ASGI
|
|--animes/                              # App principal: gestión del catálogo de animes
|   |-- models.py                       # Modelos Anime y Review con validaciones
|   |-- views.py                        # Vistas para listar, crear , editar, detalles del anime y implementación de la API (Anilist)
|   |-- urls.py                         # Rutas de la app animes
|   |-- utils.py                        # Funciones auxiliares
|   |__ templates/animes/               # Plantillas HTML de la app
|       |-- home.html                   # Página principal con estadisticas del usuario
|       |-- ficha.html                  # Detalle de un anime con reseñas y rating (Anilist)
|       |-- buscar.html                 # Buscador de animes integrado con la API
|       |-- add_anime.html              # Formulario para añadir un anime a tu lista (Modal)
|       |-- edit_anime.html             # Formulario para editar un anime que ya esta en tu lista (Modal)
|       |-- view_anime.html             # Details de un anime (Modal)
|       |-- viendo.html                 # Lista de animes en estado "Viendo"
|       |-- vistos.html                 # Lista de animes en estado "Vistos"
|       |-- dropeados.html              # Lista de animes en estado "Dropeados"
|       |-- whitelist.html              # Lista de animes en estado "Whitelist"
|       |__ base_list.html              # Plantilla base para los estados de los animes
|
|-- users/                              # App de usuarios personalizados 
|   |--models.py                        # CustomUser: extiende AbstractUser con avatar y bio
|   |--views.py                         # Vistas de registro, login, logout y perfil
|   |--urls.py                          # Rutas de la app users
|   |--forms.py                         # Formularios de registro y edición de perfil
|   |--admin.py                         # Registro del modelo CustomUser
|   |__ templates/users/                # Plantillas HTML de la app
|       |-- login.html                  # Página de inicio de sesión
|       |-- register.html               # Página de registro de nuevo usuario
|       |-- logout_confirm.html         # Confimación de cierre de sesión (No utilizado)
|       |-- profile.html                # Perfil del usuario
|       |__ profile_edit.html           # Formulario de edición del perfil
|
|-- core/                               # App auxiliar
|   |-- static/                         # Carpeta con todos los archivos static
|   |   |-- css/style.css               # Estilos globales del proyecto
|   |   |__ img/                        # Imágenes estáticas (logo, avatares por defecto, etc)
|   |__ templates/                      # Plantillas HTML de la app
|       |-- base.html                   # Plantilla base HTML de la que heredan todas las páginas
|       |__ components/                 # Componentes reutilizables
|           |-- navbar.html             # Barra de navegación (escritorio)
|           |-- mobile_nav.html         # Barra de navegacíon (movil)
|           |-- footer.html             # Pie de página
|           |-- profile_header.html     # Cabecera del perfil de usuario
|           |__ rating.html             # Puntuación con estrellas
|           
|-- nginx/                              
|   |__ nginx.conf                      # Configuración de Nginx (proxy inverso, SSL y archivos estáticos)
|
|-- Dockerfile                          # Imagen Docker de la app Django
|-- docker-compose.yml                  # Orquestación de los tres servicios utilizados en el proyecto (db, web y nginx)
|-- requirements.txt                    # Dependencias Python del proyecto
|-- manage.py                           # CLI de Django para tareas de administración
|__ .gitignore                          # Fichero para la exclusión de archivos 
```

---

## Modelos de datos

### Anime

Representa un anime en la lista de un usuario. Cada entrada pertenece a un usuario concreto, este tiene los siguientes estados:

| Estado | Descripción                      |
|---|----------------------------------|
|`viendo`| El usuario está viendo el anime  |
|`visto`| El usuario ha terminado el anime |
| `dropeado`| El usuario abandonó el anime |
| `whitelist`| El usuario quiere verlo en el futuro |

Incluye validaciones: coherencia de fechas, progreso de episodios y restricciones por estado.

### Review

Reseña de texto que un usuario puede poner en un anime que ya está en su lista.

### CustomUser
Extiendo el modelo de usuario de Django con:
- `avatar`: imagen de perfil (JPG/PNG, 2MB max)
- `bio`: Descripción personalizada
- Validación de dominio de correo electrónico (Gmail y Hotmail)

---

## Tecnologías utilizadas

| Tecnología                  | Versión | Uso                                                                        |
|-----------------------------|---------|----------------------------------------------------------------------------|
| **Python**                  | 3.12    | Lenguaje base del backend                                                  |
| **Django**                  | 6.03    | Framework web principal                                                    |
| **MySQL**                   | 8.0     | Base de datos relacional                                                   |
| **SQLite**                  | 3.53.1  | Base de datos usada en desarrollo local sin Docker                         |       
| **Gunicorn**                | Latest  | Servidor WSGI para producción                                              |
| **Nginx**                   | 1.29.6  | Proxy inverso y servidor de archivos estáticos                             |
| **Docker / Docker Compose** | -       | Ejecutar la aplicación en contenedores y gestionar varios servicios juntos |
| **Bootstrap**               | 5.3.3   | Framework CSS para el diseño responsive y estilos                          |
| **Bootstrap Icons**         | 1.11.3  | Librería de iconos                                                         |
| **Poppins (Google Fonts)**  | -       | Tipografía principal                                                       |
| **Pillow**                  | Latest  | Procesamiento de imágenes (avatares)                                       |
| **mysqlcliente**            | Latest  | Conector Python para MySQL                                                 |
| **deep-translator**         | Latest  | Traducción automática, utilizada para la sinopsis                          |
| **AniList GraphQL API**     | Latest  | API utilizada como fuente de datos externa para obtener información de animes  |
| **Let's Encrypt / Certbot** | Latest  | Certificados SSL gratuitos para servir la aplicación con HTTPS             |
| **DuckDNS**                 | Latest  | Servicio de DNS dinámico gratuito utilizado para el dominio en producción  |
| **Git**                     | 2.54.0  | Control de versiones del código fuente del proyecto                        |
| **AWS**                     | v2      | Despliegue del proyecto (EC2)                                              |





---

## SSL / HTTPS

El proyecto está configurado para servirse con HTTPS usando certificados de **Let's Encrypt** a través de DuckDNS. Nginx redirige automáticamente todo el tráfico HTTP a HTTPS.

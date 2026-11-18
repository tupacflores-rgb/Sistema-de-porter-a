<div align="center">

# Sistema de Gestión de Asistencia Escolar

**Aplicación web para administrar usuarios y registrar, consultar y respaldar la asistencia de una comunidad educativa.**

Desarrollada con Flask y SQLite, con acceso por roles, lectura de códigos QR y registro manual de asistencia.

</div>

---

## Descripción

El sistema centraliza la gestión de alumnos, preceptores, directivos y personal de entrada. Permite registrar entradas y consultar información de asistencia desde una interfaz web adaptable, con almacenamiento local en SQLite.

La identificación para registrar llegadas se realiza mediante códigos QR o carga manual. Las fotos de perfil se almacenan como imágenes y no se procesan con reconocimiento facial.

## Funcionalidades

- **Gestión de usuarios y roles:** administración de alumnos, preceptores, directivos y personal de entrada.
- **Asistencia:** registro manual o mediante QR, control de presentes, ausentes y tardanzas, e historial por fecha, mes o curso.
- **Carga masiva:** importación de alumnos desde Excel (.xlsx), con asociación de columnas, vista previa y validación antes de confirmar.
- **Códigos QR:** generación y validación para agilizar la identificación de usuarios.
- **Copias de seguridad:** creación y administración de respaldos de la base de datos.
- **Acceso móvil:** escaneo con la cámara del teléfono a través de HTTPS.

## Notificaciones

La aplicación puede enviar avisos automáticos por email y Telegram cuando un alumno llega tarde mediante QR. También puede notificar por email cuando un preceptor marca manualmente una tardanza. Las notificaciones son opcionales y no impiden registrar la asistencia si el servicio externo no está disponible.

Los canales se administran desde **Panel de Dirección → Funciones experimentales**, donde se pueden activar o desactivar y enviar pruebas de correo y Telegram. El estado se guarda en la base de datos (tabla `ajustes`). Por defecto ambos canales quedan activados, pero solo se envía algo si las credenciales están configuradas.

## Roles del sistema

| Rol | Acceso principal |
| --- | --- |
| Directivo | Gestión de usuarios, carga masiva, reportes y administración del sistema. |
| Preceptor | Registro y consulta de asistencia de los cursos asignados. |
| Entrada | Escaneo de QR y registro de llegada de alumnos. |
| Alumno | Consulta de su propio historial de asistencia. |

## Tecnologías

- Python 3.10 o 3.11
- Flask y Jinja2
- SQLite
- Pillow, OpenPyXL y `qrcode`
- Bootstrap, JavaScript y jsQR en la interfaz web

## Requisitos

- Python de 64 bits. En Windows, se recomienda Python 3.11.
- Las dependencias definidas en `requirements.txt`.

## Instalación y ejecución

Ejecuta los siguientes pasos desde la raíz del repositorio. La aplicación se encuentra dentro de `ProyectoGestion de asistencia/`.

### Windows (PowerShell)

```powershell
Set-Location 'ProyectoGestion de asistencia'
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python app.py
```

### Linux (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install -y python3 python3-venv
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
cd 'ProyectoGestion de asistencia'
python app.py
```

Al iniciar, la aplicación crea o actualiza automáticamente la base SQLite local. Abre en el navegador la dirección HTTPS que aparece en la terminal (normalmente `https://127.0.0.1:5000`). El modo HTTPS predeterminado utiliza un certificado temporal; el navegador puede mostrar una advertencia.

### Acceso inicial de desarrollo

En una base de datos nueva se crea una cuenta inicial:

- **Correo:** `admin@colegio.com`
- **Contraseña:** `admin123`

Estas credenciales son únicamente para desarrollo local. Cámbialas inmediatamente y no expongas la aplicación en Internet con la configuración predeterminada.

## Configuración

La aplicación acepta estas variables de entorno:

| Variable | Predeterminado | Descripción |
| --- | --- | --- |
| `FLASK_HOST` | `0.0.0.0` | Interfaz de red en la que escucha Flask. |
| `FLASK_PORT` | `5000` | Puerto del servidor. |
| `FLASK_DEBUG` | `0` | Activa el modo debug cuando su valor es `1`. Mantener desactivado fuera del desarrollo. |
| `FLASK_HTTPS` | `1` | Usa HTTPS ad-hoc por defecto. Establecer en `0` para desactivar HTTPS. |
| `FLASK_SSL_CERT` | — | Ruta al certificado TLS propio. Debe configurarse junto con `FLASK_SSL_KEY`. |
| `FLASK_SSL_KEY` | — | Ruta a la clave privada asociada al certificado TLS. |
| `TELEGRAM_BOT_TOKEN` | — | Token del bot que enviará avisos de llegadas tarde. |
| `TELEGRAM_CHAT_ID` | — | Chat o grupo de Telegram que recibirá los avisos. |
| `SMTP_HOST` | — | Servidor SMTP para enviar avisos por email. |
| `SMTP_PORT` | `587` | Puerto SMTP. El puerto `465` usa SSL directo; otros puertos usan STARTTLS. |
| `SMTP_USERNAME` | — | Usuario de autenticación SMTP. |
| `SMTP_PASSWORD` | — | Contraseña o clave de aplicación SMTP. |
| `SMTP_FROM_EMAIL` | `SMTP_USERNAME` | Dirección que aparecerá como remitente. |

Para permitir el acceso desde un teléfono, ambos dispositivos deben estar en una red de confianza. Configura un certificado confiable para la IP o el nombre de host del servidor. Consulta [HTTPS_MOVIL.md](HTTPS_MOVIL.md) para las instrucciones de Windows y `mkcert`.

Para activar Telegram, crea un bot con `@BotFather`, inicia una conversación con él o agrégalo al grupo destinatario, obtiene el `chat_id` correspondiente y configura ambas variables antes de iniciar Flask:

```powershell
$env:TELEGRAM_BOT_TOKEN = 'token-del-bot'
$env:TELEGRAM_CHAT_ID = 'id-del-chat'
python app.py
```

Para activar los avisos por email, configura el servidor SMTP y el correo de cada alumno en su usuario. Ejemplo con STARTTLS:

```powershell
$env:SMTP_HOST = 'smtp.example.com'
$env:SMTP_PORT = '587'
$env:SMTP_USERNAME = 'avisos@example.com'
$env:SMTP_PASSWORD = 'clave-de-aplicacion'
$env:SMTP_FROM_EMAIL = 'avisos@example.com'
python app.py
```

Usa una clave de aplicación cuando el proveedor de correo tenga autenticación en dos pasos y no guardes estas variables en el repositorio.

### Configuración con archivo `.env`

La aplicación carga automáticamente un archivo `.env` ubicado en `ProyectoGestion de asistencia/`. Podés copiar `.env.example` y completar los valores:

```powershell
Set-Location 'ProyectoGestion de asistencia'
Copy-Item .env.example .env
notepad .env
```

Ejemplo con Gmail (requiere una contraseña de aplicación):

```dotenv
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu-cuenta@gmail.com
SMTP_PASSWORD=clave-de-aplicacion
SMTP_FROM_EMAIL=tu-cuenta@gmail.com

TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_CHAT_ID=123456789
```

Después de modificar `.env`, reiniciá `python app.py` para que se apliquen los cambios.

También podés completar o actualizar estas credenciales desde **Funciones experimentales → Guardar configuración**. La aplicación escribe los valores en `.env` de forma atómica, conserva los comentarios y el resto de las variables, y aplica los cambios sin necesidad de reiniciar. Por seguridad, la contraseña SMTP y el token del bot no se muestran: si dejás esos campos vacíos se conserva el valor guardado.

### Activar y probar las notificaciones

1. Iniciá sesión con una cuenta de rol **directivo**.
2. En el **Panel de Dirección**, entrá a **Funciones experimentales**.
3. Completá y guardá las credenciales de correo y/o Telegram desde las tarjetas.
4. Revisá la configuración detectada en cada tarjeta.
5. Usá **Probar envío** para el correo o **Probar envío por Telegram** para confirmar que las credenciales funcionan.
6. Activá cada canal con su botón. Mientras esté desactivado, el sistema no envía avisos automáticos, aunque la configuración sea válida.

Para Telegram, crea el bot con `@BotFather`, iniciá una conversación con el bot (o agregalo al grupo), envía un mensaje y obtén el `chat_id`. Para correo, cada alumno debe tener una dirección válida cargada en su usuario.

## Pruebas

Desde la carpeta del proyecto y con el entorno virtual activado:

```bash
python -m unittest discover -s tests -v
```

La aplicación fue validada mediante comprobación de sintaxis, carga de Flask e interpretación de las plantillas principales. El escáner QR no requiere componentes nativos.

## Estructura del proyecto

```text
ProyectoGestion de asistencia/
├── app.py                  # Aplicación Flask, rutas y lógica de negocio
├── templates/              # Vistas HTML/Jinja2
├── static/                 # Recursos estáticos y fotos cargadas
├── backup_db/              # Copias de seguridad de la base de datos
├── tests/                  # Pruebas automatizadas
├── HTTPS_MOVIL.md          # Configuración HTTPS para acceso móvil
└── RECONOCIMIENTO_FACIAL.md # Registro de la funcionalidad retirada
```

El archivo de dependencias se encuentra en la raíz del repositorio: `requirements.txt`.

## Privacidad y seguridad

- Los datos de asistencia, las cuentas, las fotografías y los respaldos pueden contener información personal. Protege el equipo y restringe el acceso a la base de datos y a las carpetas de carga y copias de seguridad.
- La configuración inicial incluye una clave de sesión fija y una cuenta administrativa conocida. **El proyecto requiere endurecimiento de seguridad antes de cualquier despliegue real**: sustituye estos valores, utiliza un servidor WSGI apropiado, configura HTTPS confiable, limita el acceso de red y establece políticas de protección, retención y eliminación de datos.
- No incluyas en Git la base de datos real, certificados, claves privadas, fotos ni copias de seguridad con datos personales.

El motivo de la retirada del reconocimiento facial y las verificaciones realizadas están documentados en [RECONOCIMIENTO_FACIAL.md](ProyectoGestion%20de%20asistencia/RECONOCIMIENTO_FACIAL.md).

## Estado

Proyecto funcional para uso local y evaluación. Antes de utilizarlo en un entorno institucional o productivo, realiza una revisión de seguridad, privacidad, precisión y requisitos legales.

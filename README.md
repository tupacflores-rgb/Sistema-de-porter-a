<div align="center">

# Sistema de Gestión de Asistencia Escolar

**Aplicación web para administrar usuarios y registrar, consultar y respaldar la asistencia de una comunidad educativa.**

Desarrollada con Flask y SQLite, con acceso por roles, lectura de códigos QR y reconocimiento facial opcional con consentimiento.

</div>

---

## Descripción

El sistema centraliza la gestión de alumnos, preceptores, directivos y personal de entrada. Permite registrar entradas y consultar información de asistencia desde una interfaz web adaptable, con almacenamiento local en SQLite.

El reconocimiento facial es una alternativa opcional al QR para registrar la llegada de alumnos. El procesamiento se realiza en el servidor local y solo se habilita cuando existe consentimiento registrado. El sistema también permite continuar utilizando QR cuando esta función no está instalada o no se desea utilizar.

## Funcionalidades

- **Gestión de usuarios y roles:** administración de alumnos, preceptores, directivos y personal de entrada.
- **Asistencia:** registro manual o mediante QR, control de presentes, ausentes y tardanzas, e historial por fecha, mes o curso.
- **Reconocimiento facial opcional:** detección y comparación local de rostros para registrar la entrada, sujeto a consentimiento explícito.
- **Carga masiva:** importación de alumnos desde Excel (.xlsx), con asociación de columnas, vista previa y validación antes de confirmar.
- **Códigos QR:** generación y validación para agilizar la identificación de usuarios.
- **Copias de seguridad:** creación y administración de respaldos de la base de datos.
- **Acceso móvil:** escaneo con la cámara del teléfono a través de HTTPS.

## Roles del sistema

| Rol | Acceso principal |
| --- | --- |
| Directivo | Gestión de usuarios, carga masiva, reportes y administración del sistema. |
| Preceptor | Registro y consulta de asistencia de los cursos asignados. |
| Entrada | Escaneo de QR y registro de llegada de alumnos. |
| Alumno | Consulta de su propio historial de asistencia. |

## Tecnologías

- Python 3.10 o 3.11 (recomendado para compatibilidad con `dlib` en Windows)
- Flask y Jinja2
- SQLite
- OpenCV, `face_recognition` y `dlib` para reconocimiento facial
- Pillow, NumPy, OpenPyXL y `qrcode`
- Bootstrap, JavaScript y jsQR en la interfaz web

## Requisitos

- Python de 64 bits. En Windows, se recomienda Python 3.11.
- Compilador de C++ y CMake disponibles para compilar `dlib` si no hay un paquete binario compatible.
- Las dependencias definidas en `requirements.txt`.

> **Nota para Windows:** `dlib` requiere componentes nativos. Si la instalación falla, consulta la guía detallada [RECONOCIMIENTO_FACIAL.md](RECONOCIMIENTO_FACIAL.md), que incluye los pasos para configurar Visual Studio Build Tools.

## Instalación y ejecución

Ejecuta los siguientes pasos desde la carpeta que contiene `app.py` y `requirements.txt`.

### Windows (PowerShell)

```powershell
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install cmake
python -m pip install -r requirements.txt
python app.py
```

### Linux (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-dev build-essential cmake libopenblas-dev liblapack-dev libx11-dev
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
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
| `FACE_MATCH_TOLERANCE` | `0.48` | Umbral de distancia facial; debe validarse según las condiciones reales de uso. |

Para permitir el acceso desde un teléfono, ambos dispositivos deben estar en una red de confianza. Configura un certificado confiable para la IP o el nombre de host del servidor. Consulta [HTTPS_MOVIL.md](HTTPS_MOVIL.md) para las instrucciones de Windows y `mkcert`.

## Pruebas

Desde la carpeta del proyecto y con el entorno virtual activado:

```bash
python -m unittest discover -s tests -v
```

Las pruebas disponibles validan funciones del servicio facial sin requerir cámara ni cargar el modelo nativo de `dlib`.

## Estructura del proyecto

```text
ProyectoGestion de asistencia/
├── app.py                  # Aplicación Flask, rutas y lógica de negocio
├── face_service.py         # Validación de imágenes y utilidades faciales
├── requirements.txt        # Dependencias Python
├── templates/              # Vistas HTML/Jinja2
├── static/                 # Recursos estáticos y fotos cargadas
├── backup_db/              # Copias de seguridad de la base de datos
├── tests/                  # Pruebas automatizadas
├── HTTPS_MOVIL.md          # Configuración HTTPS para acceso móvil
└── RECONOCIMIENTO_FACIAL.md # Guía técnica y configuración facial
```

## Privacidad y seguridad

- Los datos de asistencia, las cuentas, las fotografías y los respaldos pueden contener información personal. Protege el equipo y restringe el acceso a la base de datos y a las carpetas de carga y copias de seguridad.
- El uso de reconocimiento facial requiere consentimiento explícito. Los embeddings faciales son datos biométricos sensibles; revisa la normativa aplicable, en especial cuando se trate de menores.
- El reconocimiento implementado no ofrece detección de vida. Mantén un método alternativo y verificación humana para incidencias.
- La configuración inicial incluye una clave de sesión fija y una cuenta administrativa conocida. **El proyecto requiere endurecimiento de seguridad antes de cualquier despliegue real**: sustituye estos valores, utiliza un servidor WSGI apropiado, configura HTTPS confiable, limita el acceso de red y establece políticas de protección, retención y eliminación de datos.
- No incluyas en Git la base de datos real, certificados, claves privadas, fotos ni copias de seguridad con datos personales.

Para conocer más detalles sobre el tratamiento facial, los límites técnicos y la instalación, consulta [RECONOCIMIENTO_FACIAL.md](RECONOCIMIENTO_FACIAL.md).

## Estado

Proyecto funcional para uso local y evaluación. Antes de utilizarlo en un entorno institucional o productivo, realiza una revisión de seguridad, privacidad, precisión y requisitos legales.

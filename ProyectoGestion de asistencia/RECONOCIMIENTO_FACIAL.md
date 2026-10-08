# Asistencia local con reconocimiento facial

## Arquitectura integrada

- La cámara sigue abierta dentro del escáner de pantalla completa. El navegador intenta leer QR localmente con `jsQR`; si no encuentra uno, envía una captura JPEG pequeña al servidor local aproximadamente cada 1,1 segundos.
- `face_service.py` usa OpenCV para decodificar/reducir la imagen y `face_recognition`/dlib para detectar rostros y producir embeddings de 128 dimensiones. Una captura con cero rostros no genera asistencia; con más de un rostro no identifica a nadie.
- Solo se comparan embeddings de alumnos con consentimiento guardado. La comparación es distancia euclidiana con umbral inicial `0.48`, configurable con `FACE_MATCH_TOLERANCE`.
- Un rostro coincidente registra la asistencia de hoy. Se conservan los estados SQLite existentes `presente` y `tardanza` para no romper reportes; la interfaz los presenta como **A tiempo** y **Llegada tarde**. La hora oficial individual se almacena en `usuarios.hora_entrada_oficial` y se compara con la hora local del servidor.
- El registro es transaccional, limita una entrada por alumno y fecha, y comunica el cooldown de cinco minutos ante un reintento rápido. La detección facial solo permite registrar alumnos; QR continúa funcionando para el resto de los roles.
- El esquema SQLite se amplía automáticamente al iniciar la aplicación. `face_encoding` contiene JSON con 128 números y `face_consent` documenta el consentimiento.

## Registro de un rostro

1. Iniciá sesión como directivo y creá o editá el alumno.
2. En el paso **Perfil**, asigná turno y horario oficial. Los defaults son 08:00 para mañana y 13:00 para tarde; la hora se puede ajustar por usuario.
3. En el paso **Foto y registro facial**, capturá o subí una foto frontal clara con una sola persona.
4. Marcá la casilla de consentimiento y guardá. Sin consentimiento, el usuario puede seguir usando QR y el sistema no guarda embedding facial. Para dar consentimiento a un alumno menor, quien lo gestiona debe contar con autorización del responsable.
5. Si la captura no contiene exactamente un rostro o el servicio facial no está disponible, se informa un error y no se sobrescribe el registro facial anterior.

## Instalación en Windows (recomendado: Python 3.10 o 3.11)

`dlib` contiene código nativo C++. Para esta pila, usa Python 3.11 de 64 bits. El intérprete 3.14 configurado actualmente para el workspace no es el adecuado para instalar esta versión de `dlib`.

### 1. Instalar o habilitar el compilador C++

- **Si tienes el Visual Studio IDE** (Community/Professional/Enterprise), no hace falta instalar Build Tools aparte si ya tiene la carga de trabajo **Desarrollo para el escritorio con C++**. Abre **Visual Studio Installer** desde Inicio, pulsa **Modificar** junto a tu instalación, marca esa carga y confirma **MSVC v143** y un **Windows 10/11 SDK**. **C++ CMake tools for Windows** también es recomendable.
- Si instalaste **solo Visual Studio Code**, eso no incluye compilador ni SDK. En ese caso instala **Build Tools for Visual Studio 2022** desde la página oficial de Visual Studio y marca la misma carga de trabajo C++.
- CMake debe quedar disponible. Puedes instalarlo desde Visual Studio Installer o con `python -m pip install cmake` después de activar el entorno virtual.

### 2. Instalar y comprobar Python

Instala Python **3.11 x64** desde python.org y activa **Add Python to PATH** en el instalador. Abre una PowerShell nueva y comprueba que el lanzador lo encuentra:

   ```powershell
   py -0p
   py -3.11 -c "import sys, struct; print(sys.version); print(struct.calcsize('P') * 8, 'bits')"
   ```

La segunda orden debe indicar Python 3.11 y **64 bits**. Si `py -3.11` no se reconoce, instala Python 3.11 primero; no uses el Python 3.14 del workspace para este entorno.

### 3. Crear un entorno aislado e instalar dependencias

Abre PowerShell en la carpeta del proyecto que contiene `app.py` y `requirements.txt`:

   ```powershell
   py -3.11 -m venv .venv
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip setuptools wheel
   python -m pip install cmake
   python -m pip install -r requirements.txt
   ```

Cuando la instalación termine, comprueba que los módulos nativos cargan correctamente:

   ```powershell
   python -c "import cv2, dlib, face_recognition; print('OpenCV', cv2.__version__, '| dlib', dlib.__version__)"
   ```

Si Windows pregunta por permisos de firewall al iniciar Flask, permite solo las redes privadas/de confianza que necesites.

### 4. Iniciar la aplicación y seleccionar su intérprete

Con `(.venv)` visible en PowerShell, ejecuta `python app.py` desde la carpeta del proyecto. En VS Code selecciona **Python: Select Interpreter** y elige `.venv\Scripts\python.exe`. El bloque principal de esta aplicación usa HTTPS ad-hoc por defecto; para móviles, configura `FLASK_SSL_CERT` y `FLASK_SSL_KEY` con un certificado confiable para el nombre/IP del servidor.

### Problemas frecuentes en Windows

- Si `pip` informa que no puede compilar `dlib`, comprueba que la PowerShell nueva ve MSVC/CMake y que el entorno usa Python 3.11 x64. También puedes abrir **Developer PowerShell for VS 2022** y activar allí el entorno `.venv`.
- Si la instalación de `face_recognition` falla debido a un `wheel` de `dlib` no disponible, no borres las dependencias ni cambies a Python 3.14: revisa la carga de trabajo C++ y las herramientas. Como alternativa, usa Linux/WSL con los pasos de abajo.
- Instalar Python 3.11 no cambia el intérprete global de VS Code: este proyecto debe usar explícitamente `.venv\Scripts\python.exe`.

## Instalación en Linux (Debian/Ubuntu)

1. Instala compilador y librerías de desarrollo:

   ```bash
   sudo apt update
   sudo apt install -y python3 python3-venv python3-dev build-essential cmake libopenblas-dev liblapack-dev libx11-dev
   ```

2. Desde la carpeta `ProyectoGestion de asistencia`, crea un entorno e instala:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```

3. Comprueba paquetes e inicia desde la carpeta del proyecto con `python app.py`. El modo HTTPS ad-hoc está habilitado por defecto; para clientes móviles se recomienda configurar `FLASK_SSL_CERT` y `FLASK_SSL_KEY` con un certificado confiable. Publica el servidor solamente en una red confiable.

## Seguridad, precisión y operación

- El procesamiento corre en el servidor donde se ejecuta Flask y las capturas transitorias del escáner no se escriben en disco; únicamente se almacena el embedding si hay consentimiento. La foto de perfil sí continúa guardándose en la ubicación habitual `static/uploads/`.
- La cámara debe ser accesible por HTTPS en móvil; `localhost` es una excepción de navegador. La cámara pertenece al dispositivo cliente; las capturas se transmiten al backend Flask del equipo que aloja la aplicación para procesarse de manera local en esa red.
- El umbral `0.48` es inicial y debe validarse con las condiciones reales de cámara/luz. Un valor más bajo reduce falsos positivos, pero puede aumentar rechazos.
- No hay prueba de vida (liveness): una foto impresa o una pantalla podría engañar a un reconocedor 2D. Para uso institucional, conservá verificación humana alternativa y no uses el reconocimiento facial como único mecanismo ante desacuerdos.
- El consentimiento no reemplaza la revisión de las leyes locales sobre datos biométricos, especialmente tratándose de estudiantes menores. Restringí los roles habilitados, protegé SQLite y sus backups, y definí un procedimiento de revocación/eliminación.
- Cambiar el horario oficial de entrada modifica cómo se clasifican las nuevas marcaciones; los registros de asistencia existentes no se recalculan.

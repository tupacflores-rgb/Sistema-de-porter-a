# Reconocimiento facial retirado

## Estado actual

El reconocimiento facial fue retirado de la aplicación. La asistencia se registra mediante QR, carga manual y las consultas existentes. Las fotos de perfil pueden seguir cargándose, pero se almacenan únicamente como imágenes y no generan datos biométricos.

Se conservaron las columnas SQLite `face_encoding` y `face_consent` únicamente para mantener la compatibilidad con bases creadas por versiones anteriores. La aplicación ya no las lee, escribe ni utiliza.

## Motivo técnico

Durante la revisión se comprobó lo siguiente:

1. El entorno original de VS Code utilizaba Python 3.14.7 y no tenía instalados `cv2`, `face_recognition` ni `numpy`.
2. Se instaló Python 3.11 x64 y se creó `ProyectoGestion de asistencia/.venv`.
3. `numpy`, OpenCV, Pillow y los modelos de `face_recognition` podían instalarse, pero `dlib` debía compilarse desde código fuente.
4. La primera compilación falló porque CMake no estaba disponible.
5. Después de instalar CMake, la compilación seguía necesitando un compilador C++ de Visual Studio.
6. El equipo utiliza un Intel Celeron N4020 sin AVX. Las ruedas binarias probadas de `dlib` fallaron al cargar `_dlib_pybind11` con `DLL load failed`.

Por estas incompatibilidades nativas y para evitar mantener una función que no podía ejecutarse de forma reproducible en este equipo, se decidió retirar el reconocimiento facial. No se modificó el flujo QR.

## Cambios realizados

- Se eliminaron las rutas backend de detección, comparación y asistencia facial.
- El escáner de entrada y preceptor ahora procesa exclusivamente códigos QR.
- El formulario de usuarios conserva la carga de foto de perfil, sin cámara facial, consentimiento biométrico ni embeddings.
- Se eliminaron `face_service.py` y sus pruebas específicas.
- Se quitaron `opencv-python-headless`, `dlib` y `face-recognition` de `requirements.txt`.
- Se mantuvieron las columnas faciales antiguas de SQLite para no romper bases existentes.

## Verificación

Después de los cambios se validó la sintaxis y la importación de `app.py`. La alternativa operativa vigente es QR, que no depende de CMake, dlib ni de instrucciones AVX.

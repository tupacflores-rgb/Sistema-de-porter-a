# HTTPS para usar la cámara desde un teléfono

Al iniciar la aplicación con `python app.py`, Flask sirve el sitio por HTTPS en el puerto 5000. El certificado temporal permite comprobar la conexión, pero los navegadores del teléfono pueden mostrar una advertencia y bloquear la cámara. Para un uso normal, genera un certificado local confiable para la IP de la computadora.

## Preparar un certificado confiable en Windows

1. Instala [mkcert](https://github.com/FiloSottile/mkcert) y abre PowerShell en la carpeta del proyecto.
2. Ejecuta `ipconfig` y anota la dirección IPv4 de la red Wi-Fi o Ethernet, por ejemplo `192.168.1.25`.
3. Crea e instala la autoridad local en la computadora y genera el certificado para la IP. Sustituye la IP de ejemplo por la tuya:

   ```powershell
   mkcert -install
   New-Item -ItemType Directory -Force certs
   mkcert -cert-file certs/local-cert.pem -key-file certs/local-key.pem 192.168.1.25 localhost 127.0.0.1
   $env:FLASK_SSL_CERT = (Resolve-Path certs/local-cert.pem).Path
   $env:FLASK_SSL_KEY = (Resolve-Path certs/local-key.pem).Path
   python app.py
   ```

4. Para que el teléfono confíe en el certificado, instala en él el certificado raíz público que muestra `mkcert -CAROOT` (archivo `rootCA.pem`) siguiendo los ajustes de certificados de confianza del sistema. No copies ni compartas `rootCA-key.pem`; esa es la clave privada de la autoridad.
5. Conecta ambos dispositivos a la misma red Wi-Fi y abre `https://192.168.1.25:5000` en el teléfono. Acepta la solicitud de cámara del navegador. Si Windows Firewall lo solicita, permite Python en la red privada.

Si solo se quiere probar, basta con ejecutar `python app.py` y abrir la dirección HTTPS indicada en la terminal; el certificado temporal generará una advertencia. Para volver a HTTP en la computadora, establece `$env:FLASK_HTTPS = '0'` antes de ejecutar la aplicación.

La dirección IP del certificado debe coincidir con la dirección que se escribe en el teléfono. Si cambia la IP local, vuelve a generar el certificado con la nueva dirección.
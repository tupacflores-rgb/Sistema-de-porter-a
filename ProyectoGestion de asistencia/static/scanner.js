/* Escáner de QR compartido (portería y preceptor). Requiere bootstrap y jsQR. */
(() => {
  const modalElement = document.getElementById('scannerModal');
  if (!modalElement) return;

  const scannerModal = new bootstrap.Modal(modalElement);
  const video = document.getElementById('video');
  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d', { willReadFrequently: true });
  const statusElement = document.getElementById('scanStatus');
  const retryButton = document.getElementById('scannerRetry');
  const resultElement = document.getElementById('scannerResult');
  const validateUrl = modalElement.dataset.validateUrl;
  let scanning = false;
  let stream = null;
  let retryTimer = null;

  function setStatus(text, isError) {
    statusElement.textContent = text;
    statusElement.classList.toggle('is-error', Boolean(isError));
  }

  function openScanner() {
    scannerModal.show();
    startCamera();
  }

  async function startCamera() {
    stopScanner();
    clearTimeout(retryTimer);
    setStatus('Iniciando cámara…');
    retryButton.hidden = true;
    try {
      if (!navigator.mediaDevices?.getUserMedia) {
        throw new Error('La cámara necesita una conexión segura (HTTPS). Pedí ayuda a quien administra el sistema.');
      }
      stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }, audio: false });
      video.srcObject = stream;
      await video.play();
      scanning = true;
      setStatus('Listo. Mostrá el QR a la cámara.');
      requestAnimationFrame(tick);
    } catch (error) {
      const message = error.name === 'NotAllowedError'
        ? 'No hay permiso para usar la cámara. Tocá el candado de la barra de direcciones y permití la cámara.'
        : error.name === 'NotFoundError'
          ? 'No se encontró ninguna cámara en este dispositivo.'
          : (error.message || 'No se pudo abrir la cámara.');
      setStatus(message, true);
      retryButton.hidden = false;
    }
  }

  function stopScanner() {
    scanning = false;
    if (stream) stream.getTracks().forEach(track => track.stop());
    stream = null;
    video.srcObject = null;
  }

  function tick() {
    if (!scanning) return;
    if (video.readyState === video.HAVE_ENOUGH_DATA) {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const code = jsQR(imageData.data, imageData.width, imageData.height);
      if (code) {
        stopScanner();
        if (navigator.vibrate) navigator.vibrate(80);
        setStatus('Código leído. Buscando al alumno…');
        validateToken(code.data);
        return;
      }
    }
    requestAnimationFrame(tick);
  }

  async function validateToken(token) {
    try {
      const response = await fetch(validateUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token }),
        credentials: 'same-origin'
      });
      const data = await response.json();
      if (data.ok) {
        window.location.href = '/qr/' + encodeURIComponent(token);
        return;
      }
      throw new Error('Ese código no corresponde a ningún alumno. Probá con otro.');
    } catch (error) {
      setStatus(error.message || 'No se pudo leer el código.', true);
      retryButton.hidden = false;
      // Vuelve a escanear solo, para no frenar la fila de ingreso.
      retryTimer = setTimeout(startCamera, 2500);
    }
  }

  document.getElementById('btnScan')?.addEventListener('click', openScanner);
  document.getElementById('btnStop').addEventListener('click', () => {
    clearTimeout(retryTimer);
    stopScanner();
    scannerModal.hide();
  });
  retryButton.addEventListener('click', startCamera);
  modalElement.addEventListener('hidden.bs.modal', () => { clearTimeout(retryTimer); stopScanner(); });
  window.addEventListener('pagehide', stopScanner);

  // El resultado del último ingreso se muestra unos segundos y se oculta solo.
  if (resultElement) {
    if (navigator.vibrate) navigator.vibrate(resultElement.classList.contains('scanner-result-success') ? 120 : [120, 80, 120]);
    setTimeout(() => resultElement.classList.add('is-hidden'), 5000);
  }

  const params = new URLSearchParams(window.location.search);
  if (params.get('scan') === '1' || modalElement.dataset.autoOpen === 'true') openScanner();
})();

"""Utilidades locales para detectar, registrar y comparar rostros.

El módulo carga face_recognition/OpenCV bajo demanda para que el resto del
sistema siga funcionando si todavía no se instalaron los componentes faciales.
Los embeddings de face_recognition son vectores de 128 dimensiones.
"""

from __future__ import annotations

import base64
import binascii
import io
import json
import os
import re
from typing import Any

from PIL import Image, UnidentifiedImageError

MAX_IMAGE_BYTES = 4 * 1024 * 1024
MAX_IMAGE_PIXELS = 4_000_000
MAX_FRAME_SIDE = 960


class FaceRecognitionUnavailable(RuntimeError):
    """Señala que faltan las dependencias nativas del reconocedor facial."""


class FaceImageError(ValueError):
    """Señala que una imagen facial no es válida o no es utilizable."""


def _libraries() -> tuple[Any, Any, Any]:
    """Importa las bibliotecas de forma diferida y comunica cómo habilitarlas."""
    try:
        import cv2
        import face_recognition
        import numpy as np
    except ImportError as error:
        raise FaceRecognitionUnavailable(
            "La función de reconocimiento facial no está disponible en este momento."
        ) from error
    return cv2, face_recognition, np


def _read_image_bytes(image_bytes: bytes) -> Any:
    """Decodifica y limita una imagen antes de entregarla a dlib."""
    cv2, _face_recognition, np = _libraries()
    if not image_bytes or len(image_bytes) > MAX_IMAGE_BYTES:
        raise FaceImageError("La imagen está vacía o supera el tamaño permitido.")
    try:
        with Image.open(io.BytesIO(image_bytes)) as image_header:
            width, height = image_header.size
            if width < 96 or height < 96 or width * height > MAX_IMAGE_PIXELS:
                raise FaceImageError("La imagen debe medir al menos 96×96 y no superar 4 megapíxeles.")
            if image_header.format not in ('JPEG', 'PNG'):
                raise FaceImageError("Usá una imagen JPEG o PNG.")
    except (OSError, UnidentifiedImageError) as error:
        raise FaceImageError("No se pudo leer la imagen. Usá una foto JPEG o PNG.") from error
    encoded = np.frombuffer(image_bytes, dtype=np.uint8)
    image_bgr = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    if image_bgr is None:
        raise FaceImageError("No se pudo leer la imagen. Usá una foto JPEG o PNG.")
    height, width = image_bgr.shape[:2]
    longest_side = max(height, width)
    if longest_side > MAX_FRAME_SIDE:
        scale = MAX_FRAME_SIDE / longest_side
        image_bgr = cv2.resize(
            image_bgr,
            (round(width * scale), round(height * scale)),
            interpolation=cv2.INTER_AREA,
        )
    return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)


def image_data_url_to_bytes(image_data_url: str) -> bytes:
    """Valida y decodifica un Data URL JPEG/PNG recibido desde la cámara."""
    if not isinstance(image_data_url, str) or len(image_data_url) > 6 * 1024 * 1024:
        raise FaceImageError("La captura no es válida o supera el tamaño permitido.")
    match = re.fullmatch(
        r"data:image/(?:jpeg|png);base64,([A-Za-z0-9+/=]+)", image_data_url
    )
    if not match:
        raise FaceImageError("La captura debe ser una imagen JPEG o PNG en base64.")
    try:
        image_bytes = base64.b64decode(match.group(1), validate=True)
    except (binascii.Error, ValueError) as error:
        raise FaceImageError("La captura base64 está dañada.") from error
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise FaceImageError("La captura supera el máximo de 4 MB.")
    return image_bytes


def extract_encodings(image_bytes: bytes) -> list[list[float]]:
    """Devuelve un embedding de 128 dimensiones por rostro detectado."""
    _cv2, face_recognition, np = _libraries()
    rgb_image = _read_image_bytes(image_bytes)
    try:
        locations = face_recognition.face_locations(
            rgb_image, number_of_times_to_upsample=0, model="hog"
        )
        encodings = face_recognition.face_encodings(
            rgb_image, known_face_locations=locations, num_jitters=1, model="small"
        )
    except Exception as error:
        raise FaceImageError("No se pudo analizar la imagen facial.") from error
    results: list[list[float]] = []
    for encoding in encodings:
        vector = np.asarray(encoding, dtype=np.float64)
        if vector.shape != (128,) or not np.isfinite(vector).all():
            raise FaceImageError("El reconocedor devolvió un vector facial inválido.")
        results.append(vector.tolist())
    return results


def extract_single_encoding_from_data_url(image_data_url: str) -> list[float]:
    """Extrae el vector de una toma de registro que debe contener un rostro."""
    encodings = extract_encodings(image_data_url_to_bytes(image_data_url))
    if not encodings:
        raise FaceImageError("No se detectó un rostro. Mejorá la luz y mirá de frente.")
    if len(encodings) != 1:
        raise FaceImageError("La captura debe mostrar a una sola persona.")
    return encodings[0]


def extract_single_encoding_from_file(image_path: str) -> list[float]:
    """Extrae el embedding desde una foto que ya está guardada en uploads."""
    try:
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read(MAX_IMAGE_BYTES + 1)
    except OSError as error:
        raise FaceImageError("No se pudo abrir la foto de perfil guardada.") from error
    encodings = extract_encodings(image_bytes)
    if not encodings:
        raise FaceImageError("No se detectó un rostro en la foto de perfil.")
    if len(encodings) != 1:
        raise FaceImageError("La foto de perfil debe mostrar a una sola persona.")
    return encodings[0]


def serialize_encoding(encoding: list[float]) -> str:
    """Serializa el vector facial para guardarlo como JSON en SQLite."""
    if len(encoding) != 128:
        raise FaceImageError("El embedding facial debe tener 128 dimensiones.")
    return json.dumps(encoding, separators=(",", ":"))


def closest_match(
    probe: list[float], candidates: list[Any], tolerance: float = 0.48
) -> tuple[Any, float] | None:
    """Busca el embedding euclidiano más cercano dentro del umbral indicado."""
    _cv2, _face_recognition, np = _libraries()
    probe_array = np.asarray(probe, dtype=np.float64)
    if probe_array.shape != (128,):
        raise FaceImageError("El vector del rostro detectado no tiene 128 dimensiones.")
    closest_user = None
    closest_distance = float("inf")
    for candidate in candidates:
        try:
            known = np.asarray(json.loads(candidate["face_encoding"]), dtype=np.float64)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            continue
        if known.shape != (128,) or not np.isfinite(known).all():
            continue
        distance = float(np.linalg.norm(known - probe_array))
        if distance < closest_distance:
            closest_user = candidate
            closest_distance = distance
    if closest_user is None or closest_distance > tolerance:
        return None
    return closest_user, closest_distance

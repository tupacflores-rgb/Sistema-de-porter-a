"""Pruebas unitarias sin necesitar cámara ni cargar el modelo dlib."""

import base64
import json
import unittest

from face_service import (
    FaceImageError,
    image_data_url_to_bytes,
    serialize_encoding,
)


class FaceServiceValidationTests(unittest.TestCase):
    def test_decodifica_data_url_jpeg_valido(self):
        original = b"contenido de prueba"
        image_data_url = "data:image/jpeg;base64," + base64.b64encode(original).decode("ascii")
        self.assertEqual(image_data_url_to_bytes(image_data_url), original)

    def test_rechaza_data_url_sin_formato_permitido(self):
        with self.assertRaises(FaceImageError):
            image_data_url_to_bytes("data:image/gif;base64,AAAA")

    def test_rechaza_base64_malformado(self):
        with self.assertRaises(FaceImageError):
            image_data_url_to_bytes("data:image/png;base64,%%%%")

    def test_serializa_vector_de_128_dimensiones(self):
        encoded = serialize_encoding([0.0] * 128)
        self.assertEqual(len(json.loads(encoded)), 128)

    def test_rechaza_vector_con_dimensiones_incorrectas(self):
        with self.assertRaises(FaceImageError):
            serialize_encoding([0.0] * 127)


if __name__ == "__main__":
    unittest.main()

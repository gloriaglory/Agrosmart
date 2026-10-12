import json
from pathlib import Path

import numpy as np
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from . import utils

ML_DIR = Path(__file__).parent / "ml_models"
TEST_IMAGES = Path(__file__).parent / "test_images"  # labelled PlantVillage photos


class DiseaseInfoTests(APITestCase):
    def test_every_class_has_complete_information(self):
        classes = json.loads((ML_DIR / "class_indices.json").read_text())
        info = json.loads((ML_DIR / "disease_info.json").read_text())
        for name in classes:
            with self.subTest(disease=name):
                entry = info.get(name)
                self.assertIsNotNone(entry, f"{name} has no information")
                for field in ("name", "crop", "type", "description"):
                    self.assertTrue(str(entry.get(field, "")).strip(), f"{name} is missing {field}")
                for field in ("treatment", "prevention"):
                    self.assertTrue(entry.get(field), f"{name} is missing {field}")
                    self.assertTrue(all(step.strip() for step in entry[field]))


class BuildResultTests(APITestCase):
    def scores(self, best_class, confidence):
        p = np.full(len(utils.CLASS_NAMES), (1 - confidence) / (len(utils.CLASS_NAMES) - 1))
        p[utils.CLASS_NAMES.index(best_class)] = confidence
        return p

    def test_confident_result_has_readable_name_and_paragraphs(self):
        result = utils.build_result(self.scores("Tomato___Late_blight", 0.9))
        self.assertEqual(result["disease"], "Tomato late blight")
        self.assertFalse(result["uncertain"])
        self.assertIsInstance(result["treatment"], str)
        self.assertIn("TPHPA", result["treatment"])
        self.assertEqual(len(result["top_predictions"]), 3)

    def test_low_confidence_says_not_sure(self):
        result = utils.build_result(self.scores("MLN", 0.3))
        self.assertEqual(result["disease"], "Not sure")
        self.assertTrue(result["uncertain"])
        self.assertIn("Maize lethal necrosis", result["description"])


class DetectEndpointTests(APITestCase):
    url = "/detector/detect"

    def upload(self, path):
        return SimpleUploadedFile(path.name, path.read_bytes(), content_type="image/jpeg")

    def test_real_photos_are_diagnosed(self):
        expected = {
            "Tomato___Late_blight.jpg": "Tomato late blight",
            "Corn_maize___Common_rust_.jpg": "Maize common rust",
            "Potato___Early_blight.jpg": "Potato early blight",
        }
        for filename, disease in expected.items():
            with self.subTest(photo=filename):
                res = self.client.post(self.url, {"image": self.upload(TEST_IMAGES / filename)})
                self.assertEqual(res.status_code, 200, res.content)
                data = res.json()
                self.assertEqual(data["disease"], disease)
                for field in ("description", "treatment", "preventive_measures"):
                    self.assertNotIn("No ", data[field][:3])

    def test_missing_image(self):
        self.assertEqual(self.client.post(self.url, {}).status_code, 400)

# crop_predictor/tests.py
from django.test import AsyncTestCase
import httpx
from django.urls import reverse
from rest_framework import status

class CropRecommendationTestCase(AsyncTestCase):

    async def test_recommend_crop(self):
        url = reverse('recommend_crop')  # Ensure this is a valid URL in your urls.py
        data = {
            'address': 'Dodoma, Tanzania',  # Adjust test data as needed
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Add additional assertions if needed (e.g., checking the response body)


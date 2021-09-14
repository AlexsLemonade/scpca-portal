import json

from django.urls import reverse
from rest_framework.test import APITestCase

# from scpca_portal.models import APII

API_VERSION = "v1"


class APITestCases(APITestCase):
    def test_create_token_one_request(self):
        response = self.client.post(
            reverse("tokens-list"),
            json.dumps({"is_activated": True, "email": "hi@example.com"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        activated_token = response.json()
        self.assertEqual(activated_token["is_activated"], True)

    def test_create_token_two_requests(self):
        response = self.client.post(
            reverse("tokens-list"),
            json.dumps({"email": "hi@example.com"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        token = response.json()

        self.assertEqual(token["is_activated"], False)

        token["is_activated"] = True
        token_id = token["id"]
        response = self.client.put(
            reverse("tokens-detail", kwargs={"id": token_id}),
            json.dumps(token),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        activated_token = response.json()
        self.assertEqual(activated_token["id"], token_id)
        self.assertEqual(activated_token["is_activated"], True)

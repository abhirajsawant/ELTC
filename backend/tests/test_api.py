
"""TC-API: Integration tests for the ELTC HTTP API.

Run with the backend API already running:
    python -m pytest backend/tests/test_api.py -v
"""

import json
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_URL = "http://127.0.0.1:8000"


def get_json(path):
    with urlopen(f"{BASE_URL}{path}", timeout=5) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def post_json(path, payload):
    request = Request(
        f"{BASE_URL}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=5) as response:
            return response.status, json.loads(
                response.read().decode("utf-8")
            )
    except HTTPError as error:
        body = error.read().decode("utf-8")
        return error.code, json.loads(body)


class TestELTCAPI(unittest.TestCase):
    """API integration tests; the backend must be running."""

    def test_01_health_endpoint(self):
        status, data = get_json("/api/health")

        self.assertEqual(status, 200)
        self.assertIsInstance(data, dict)

    def test_02_valid_shipment_plan(self):
        payload = {
            "origin": "Delhi",
            "destination": "Mumbai",
            "commodity_type": "agricultural",
            "weight_tonnes": 40,
            "volume_m3": 50,
            "loading_method": "top_loading",
        }

        status, data = post_json("/api/plan", payload)

        self.assertEqual(status, 200)
        self.assertEqual(data.get("status"), "success")
        self.assertTrue(data.get("route"))
        self.assertTrue(data.get("wagon_options"))
        self.assertIsNotNone(data.get("freight_estimate"))

    def test_03_invalid_cargo_is_rejected(self):
        payload = {
            "origin": "Delhi",
            "destination": "Mumbai",
            "commodity_type": "agricultural",
            "weight_tonnes": -10,
            "volume_m3": 50,
            "loading_method": "top_loading",
        }

        status, data = post_json("/api/plan", payload)

        self.assertEqual(status, 400)
        self.assertEqual(data.get("status"), "invalid_input")

    def test_04_missing_required_fields(self):
        status, data = post_json("/api/plan", {"origin": "Delhi"})

        self.assertEqual(status, 400)
        self.assertIsInstance(data, dict)


if __name__ == "__main__":
    unittest.main()

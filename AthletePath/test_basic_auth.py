"""Basic Auth tests (mocked MongoDB; no real credentials required)."""
import base64
import unittest
from unittest.mock import patch
from werkzeug.security import generate_password_hash
from app import app

class BasicAuthTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def header(self, password):
        token = base64.b64encode(("student@example.com:" + password).encode()).decode()
        return {"Authorization": "Basic " + token}

    @patch("basic_auth.db")
    def test_correct_basic_credentials(self, mock_db):
        mock_db.__getitem__.return_value.find_one.return_value = {
            "email": "student@example.com",
            "password_hash": generate_password_hash("demo-password"),
            "account_status": "active",
        }
        with patch("blueprints.goals.routes.db") as goals_db:
            goals_db.__getitem__.return_value.find.return_value = []
            response = self.client.get("/api/goals", headers=self.header("demo-password"))
        self.assertEqual(response.status_code, 200)

    @patch("basic_auth.db")
    def test_wrong_basic_password(self, mock_db):
        mock_db.__getitem__.return_value.find_one.return_value = {
            "password_hash": generate_password_hash("demo-password"),
            "account_status": "active",
        }
        response = self.client.get("/api/goals", headers=self.header("wrong-password"))
        self.assertEqual(response.status_code, 401)

    def test_no_credentials(self):
        response = self.client.get("/api/goals")
        self.assertEqual(response.status_code, 401)

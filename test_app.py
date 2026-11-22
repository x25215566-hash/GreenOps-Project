"""The below code is for the Unit tests for Greenops Flask Application"""

import unittest
from unittest.mock import MagicMock, patch
import app as greenops_app

class FlaskCrudTestCase(unittest.TestCase):
    """Test suite for health and task CRUD routes"""

    def setUp(self):
        self.client = greenops_app.app.test_client()
        self.client.testing = True

    def test_health_check(self):
        """Test the root health check endpoint"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    @patch("app.get_table")
    def test_create_and_list_tasks(self, mock_get_table):
        """Test creating and listing tasks with a DynamoDB table"""
        mock_table = MagicMock()
        mock_table.scan.return_value = {
            "Items": [{"id": "1", "title": "Eco Note", "completed": False}]
        }
        mock_get_table.return_value = mock_table

        create_resp = self.client.post(
            "/tasks", json={"id": "1", "title": "Eco Note"}
        )
        self.assertEqual(create_resp.status_code, 201)

        list_resp = self.client.get("/tasks")
        self.assertEqual(list_resp.status_code, 200)
        self.assertEqual(len(list_resp.get_json()["tasks"]), 1)

if __name__ == "__main__":
    unittest.main()
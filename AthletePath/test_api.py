import unittest
from app import app

class AthletePathAPITests(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)

    def test_goals_requires_login(self):
        response = self.client.get("/api/goals")
        self.assertEqual(response.status_code, 401)

    def test_tasks_requires_login(self):
        response = self.client.get("/api/tasks")
        self.assertEqual(response.status_code, 401)
    def test_events_requires_login(self):
        response = self.client.post(
            "/api/events",
            json={"title": "Test Event"}
        )
        self.assertEqual(response.status_code, 401)

    def test_bookings_requires_login(self):
        response = self.client.post(
            "/api/bookings",
            json={"event_id": "EVENT001"}
        )
        self.assertEqual(response.status_code, 401)

    def test_training_plans_requires_login(self):
        response = self.client.post(
            "/api/training-plans",
            json={"title": "Test Plan"}
        )
        self.assertEqual(response.status_code, 401)
        
    def test_performance_stats_requires_login(self):
        response = self.client.get("/api/performance/stats")
        self.assertEqual(response.status_code, 401)
        
        
    def test_delete_task_requires_login(self):
        response = self.client.delete("/api/tasks/not-a-valid-id")
        self.assertEqual(response.status_code, 401)
        
        
        
        
if __name__ == "__main__":
    unittest.main(verbosity=2)
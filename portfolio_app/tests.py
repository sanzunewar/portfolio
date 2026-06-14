from django.test import TestCase
from django.urls import reverse


class PortfolioPagesTests(TestCase):
    def test_home_loads(self):
        response = self.client.get(reverse("portfolio:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sanjeev")

    def test_projects_loads(self):
        response = self.client.get(reverse("portfolio:projects"))
        self.assertEqual(response.status_code, 200)

    def test_about_loads(self):
        response = self.client.get(reverse("portfolio:about"))
        self.assertEqual(response.status_code, 200)

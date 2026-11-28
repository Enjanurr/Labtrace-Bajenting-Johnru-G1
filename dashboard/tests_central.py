from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class CentralDashboardAccessTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="central-admin",
            email="central-admin@cit.edu",
            password="SecurePass123!",
            role=User.Role.ADMIN,
        )
        self.student = User.objects.create_user(
            username="central-student",
            email="central-student@cit.edu",
            password="SecurePass123!",
            role=User.Role.STUDENT,
        )

    def test_staff_can_open_dashboard_and_live_data(self):
        self.client.force_login(self.admin)

        page = self.client.get(reverse("dashboard:central"))
        data = self.client.get(reverse("dashboard:central_data"))

        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, "dashboard/central.html")
        self.assertEqual(data.status_code, 200)
        self.assertIn("occupancy", data.json())

    def test_student_cannot_open_staff_dashboard_or_live_data(self):
        self.client.force_login(self.student)

        self.assertEqual(
            self.client.get(reverse("dashboard:central")).status_code,
            403,
        )
        self.assertEqual(
            self.client.get(reverse("dashboard:central_data")).status_code,
            403,
        )

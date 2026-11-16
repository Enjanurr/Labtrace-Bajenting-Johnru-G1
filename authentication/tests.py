from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class LoginBehaviorTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="labuser",
            email="labuser@cit.edu",
            password="SecurePass123!",
        )

    def test_login_template_resolves_and_accepts_email(self):
        response = self.client.get(reverse("authentication:login"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")

        response = self.client.post(
            reverse("authentication:login"),
            {"username": self.user.email, "password": "SecurePass123!"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("dashboard:home"))
        self.assertEqual(
            self.client.session.get("_auth_user_id"), str(self.user.pk)
        )

    def test_inactive_user_cannot_log_in(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        response = self.client.post(
            reverse("authentication:login"),
            {"username": self.user.username, "password": "SecurePass123!"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

from django.test import SimpleTestCase
from django.urls import reverse


class PasswordResetRoutingTests(SimpleTestCase):
    def test_login_page_links_to_reset_form(self):
        response = self.client.get("/accounts/login/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/users/password-reset/"')

    def test_reset_form_is_available_without_authentication(self):
        response = self.client.get("/users/password-reset/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reset your password")


class UserManagementRoutingTests(SimpleTestCase):
    def test_management_urls_are_registered(self):
        self.assertEqual(reverse("users:manage_list"), "/users/manage/")
        self.assertEqual(
            reverse("users:manage_role", kwargs={"pk": 12}),
            "/users/manage/12/role/",
        )
        self.assertEqual(
            reverse("users:manage_toggle", kwargs={"pk": 12}),
            "/users/manage/12/toggle-active/",
        )

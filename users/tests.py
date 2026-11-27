from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

User = get_user_model()


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


class ProfileBehaviorTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="labuser",
            email="labuser@cit.edu",
            password="SecurePass123!",
        )
        self.client.force_login(self.user)

    def test_profile_and_edit_templates_resolve(self):
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile.html")

        response = self.client.get(reverse("users:profile_edit"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile_edit.html")
        self.assertContains(response, "Institution / Department")
        self.assertContains(response, "institutional department or affiliation")
        self.assertContains(
            response,
            'placeholder="e.g., Engineering or Student Affairs"',
        )
        self.assertContains(response, "Institutional ID")
        self.assertContains(
            response,
            "Enter your student or employee institutional ID.",
        )

    def test_profile_shows_fallback_for_missing_institutional_detail(self):
        response = self.client.get(reverse("users:profile"))

        self.assertContains(response, "Institution / Department")
        self.assertContains(response, "Not provided")
        self.assertContains(response, "Institutional ID")
        self.assertContains(response, "—")

    def test_profile_update_changes_only_the_signed_in_user(self):
        response = self.client.post(
            reverse("users:profile_edit"),
            {
                "first_name": "Lab",
                "last_name": "Member",
                "email": "newaddress@cit.edu",
                "contact_number": "555-0100",
                "department": "  Chemistry  ",
                "institutional_id": "  STU-12345  ",
            },
        )

        self.assertRedirects(response, reverse("users:profile"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Lab")
        self.assertEqual(self.user.email, "newaddress@cit.edu")
        self.assertEqual(self.user.username, "newaddress@cit.edu")
        self.assertEqual(self.user.department, "Chemistry")
        self.assertEqual(self.user.institutional_id, "STU-12345")

        profile_response = self.client.get(reverse("users:profile"))
        self.assertContains(profile_response, "Institution / Department")
        self.assertContains(profile_response, "Chemistry")
        self.assertContains(profile_response, "Institutional ID")
        self.assertContains(profile_response, "STU-12345")

    def test_password_change_template_and_route_resolve(self):
        response = self.client.get(reverse("users:password_change"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/password_change.html")

        response = self.client.post(
            reverse("users:password_change"),
            {
                "old_password": "SecurePass123!",
                "new_password1": "A-different-password-234!",
                "new_password2": "A-different-password-234!",
            },
        )

        self.assertRedirects(response, reverse("users:profile"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("A-different-password-234!"))

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from equipment.models import Room

from .models import LabVisit

User = get_user_model()


class VisitBehaviorTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="labuser",
            email="labuser@cit.edu",
            password="SecurePass123!",
        )
        self.client.force_login(self.user)
        self.room = Room.objects.create(
            name="Computer Lab 1",
            building="NGE",
        )

    def test_check_in_and_visit_history_templates_resolve(self):
        response = self.client.get(reverse("access_logging:check_in"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "access_logging/check_in.html")

        response = self.client.get(reverse("access_logging:my_visits"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "access_logging/my_visits.html")

    def test_check_in_creates_a_single_active_visit(self):
        response = self.client.post(
            reverse("access_logging:check_in"),
            {"room": self.room.pk, "purpose": LabVisit.Purpose.CLASS},
        )

        self.assertRedirects(response, reverse("access_logging:my_visits"))
        self.assertEqual(
            LabVisit.objects.filter(
                user=self.user, status=LabVisit.Status.ACTIVE
            ).count(),
            1,
        )

        response = self.client.post(
            reverse("access_logging:check_in"),
            {"room": self.room.pk, "purpose": LabVisit.Purpose.RESEARCH},
        )
        self.assertRedirects(response, reverse("access_logging:my_visits"))
        self.assertEqual(
            LabVisit.objects.filter(
                user=self.user, status=LabVisit.Status.ACTIVE
            ).count(),
            1,
        )

    def test_students_cannot_view_staff_active_visits(self):
        response = self.client.get(reverse("access_logging:active"))

        self.assertEqual(response.status_code, 403)

    def test_staff_active_visit_template_and_ajax_partial_resolve(self):
        self.user.role = User.Role.INSTRUCTOR
        self.user.save(update_fields=["role"])

        response = self.client.get(reverse("access_logging:active"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "access_logging/active_visits.html")

        response = self.client.get(
            reverse("access_logging:active"),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("html", response.json())

    def test_check_out_completes_the_active_visit(self):
        visit = LabVisit.objects.create(
            user=self.user,
            lab_location="Computer Lab 1",
            purpose=LabVisit.Purpose.CLASS,
        )

        response = self.client.post(
            reverse("access_logging:check_out", kwargs={"pk": visit.pk}),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        visit.refresh_from_db()
        self.assertEqual(visit.status, LabVisit.Status.COMPLETED)
        self.assertIsNotNone(visit.check_out_time)

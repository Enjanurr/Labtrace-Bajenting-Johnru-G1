from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Incident, IncidentStatusHistory

User = get_user_model()


def make_user(email, role):
    return User.objects.create_user(
        username=email, email=email, password="pass12345!", role=role,
        first_name="Test", last_name=role.title(),
    )


class IncidentTests(TestCase):
    def setUp(self):
        self.student = make_user("s1@cit.edu", "STUDENT")
        self.other = make_user("s2@cit.edu", "STUDENT")
        self.instructor = make_user("i1@cit.edu", "INSTRUCTOR")
        self.admin = make_user("a1@cit.edu", "ADMIN")
        self.incident = Incident.objects.create(
            reporter=self.student, title="Broken mouse", description="Scroll wheel stuck.",
        )

    def post_status(self, user, status, note=""):
        self.client.force_login(user)
        return self.client.post(
            reverse("incidents:status", args=[self.incident.pk]), {"status": status, "note": note}
        )

    # --- access control ---
    def test_anonymous_redirected_to_login(self):
        r = self.client.get(reverse("incidents:list"))
        self.assertEqual(r.status_code, 302)
        self.assertIn("login", r.url)

    def test_student_sees_only_own_incidents(self):
        Incident.objects.create(reporter=self.other, title="Other's", description="x")
        self.client.force_login(self.student)
        r = self.client.get(reverse("incidents:list"))
        self.assertContains(r, "Broken mouse")
        self.assertNotContains(r, "Other&#x27;s")

    def test_student_cannot_open_others_incident(self):
        self.client.force_login(self.other)
        r = self.client.get(reverse("incidents:detail", args=[self.incident.pk]))
        self.assertEqual(r.status_code, 403)

    def test_staff_can_open_any_incident(self):
        self.client.force_login(self.instructor)
        r = self.client.get(reverse("incidents:detail", args=[self.incident.pk]))
        self.assertEqual(r.status_code, 200)

    def test_student_cannot_change_status(self):
        r = self.post_status(self.student, "INVESTIGATION")
        self.assertEqual(r.status_code, 403)
        self.incident.refresh_from_db()
        self.assertEqual(self.incident.status, "REPORTED")

    # --- submission ---
    def test_student_can_submit_incident(self):
        self.client.force_login(self.student)
        r = self.client.post(reverse("incidents:new"), {
            "title": "Cracked screen", "category": "DAMAGE", "severity": "HIGH",
            "description": "Monitor 4 is cracked.",
        })
        inc = Incident.objects.get(title="Cracked screen")
        self.assertRedirects(r, reverse("incidents:detail", args=[inc.pk]))
        self.assertEqual(inc.reporter, self.student)
        self.assertEqual(inc.status, "REPORTED")
        self.assertEqual(inc.history.count(), 1)

    def test_submission_requires_title_and_description(self):
        self.client.force_login(self.student)
        r = self.client.post(reverse("incidents:new"), {"title": "", "description": ""})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Incident.objects.count(), 1)

    # --- status engine ---
    def test_instructor_can_start_investigation(self):
        self.post_status(self.instructor, "INVESTIGATION")
        self.incident.refresh_from_db()
        self.assertEqual(self.incident.status, "INVESTIGATION")
        self.assertEqual(self.incident.assigned_to, self.instructor)
        self.assertEqual(self.incident.history.last().to_status, "INVESTIGATION")

    def test_instructor_cannot_resolve(self):
        self.incident.status = "INVESTIGATION"
        self.incident.save()
        self.post_status(self.instructor, "RESOLVED", "done")
        self.incident.refresh_from_db()
        self.assertEqual(self.incident.status, "INVESTIGATION")

    def test_cannot_skip_states(self):
        self.post_status(self.admin, "CLOSED")
        self.incident.refresh_from_db()
        self.assertEqual(self.incident.status, "REPORTED")

    def test_resolve_requires_notes(self):
        self.incident.status = "INVESTIGATION"
        self.incident.save()
        self.post_status(self.admin, "RESOLVED", "")
        self.incident.refresh_from_db()
        self.assertEqual(self.incident.status, "INVESTIGATION")

    def test_full_lifecycle_by_admin(self):
        self.post_status(self.admin, "INVESTIGATION")
        self.post_status(self.admin, "RESOLVED", "Replaced the mouse.")
        self.post_status(self.admin, "CLOSED", "")
        self.incident.refresh_from_db()
        self.assertEqual(self.incident.status, "CLOSED")
        self.assertIsNotNone(self.incident.resolved_at)
        self.assertIsNotNone(self.incident.closed_at)
        self.assertEqual(self.incident.resolution_notes, "Replaced the mouse.")
        self.assertEqual(IncidentStatusHistory.objects.filter(incident=self.incident).count(), 3)

    def test_closed_is_terminal(self):
        self.incident.status = "CLOSED"
        self.incident.save()
        self.post_status(self.admin, "INVESTIGATION")
        self.incident.refresh_from_db()
        self.assertEqual(self.incident.status, "CLOSED")
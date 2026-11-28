from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from equipment.models import Room
from .models import LabVisit

User = get_user_model()


class RoomCheckInTests(TestCase):
    def setUp(self):
        self.u = User.objects.create_user(
            username="room-picker-student",
            email="s@cit.edu",
            password="SecurePass123!",
            role=User.Role.STUDENT,
        )
        self.cl1 = Room.objects.create(name="Computer Lab 1", building="NGE")
        self.inactive = Room.objects.create(name="Old Lab", code_prefix="OLD", building="GLE", is_active=False)
        self.client.force_login(self.u)
        self.url = reverse("access_logging:check_in")   # adjust to your URL name

    def test_picker_lists_only_active_rooms(self):
        r = self.client.get(self.url)
        self.assertContains(r, "Computer Lab 1")
        self.assertNotContains(r, "Old Lab")
        self.assertEqual(r.context["buildings"], ["NGE"])
        self.assertEqual(
            r.context["rooms_data"],
            [{
                "id": self.cl1.pk,
                "name": "Computer Lab 1",
                "code_prefix": self.cl1.code_prefix,
                "lab_type": self.cl1.lab_type,
                "lab_type_display": self.cl1.get_lab_type_display(),
                "building": "NGE",
            }],
        )

    def test_buildings_are_distinct_and_only_include_active_rooms(self):
        Room.objects.create(name="Computer Lab 2", building="NGE")
        Room.objects.create(name="Electronics Lab", building="GLE")

        response = self.client.get(self.url)

        self.assertEqual(response.context["buildings"], ["GLE", "NGE"])

    def test_valid_room_checks_in_and_syncs_location(self):
        response = self.client.post(
            self.url,
            {"room": self.cl1.pk, "purpose": LabVisit.Purpose.CLASS},
        )
        self.assertRedirects(response, reverse("access_logging:my_visits"))
        v = LabVisit.objects.get(user=self.u)
        self.assertEqual(v.room, self.cl1)
        self.assertEqual(v.lab_location, "Computer Lab 1")

    def test_inactive_room_rejected(self):
        r = self.client.post(
            self.url,
            {"room": self.inactive.pk, "purpose": LabVisit.Purpose.CLASS},
        )
        self.assertEqual(r.status_code, 200)
        self.assertFalse(LabVisit.objects.filter(user=self.u).exists())

    def test_missing_room_rejected(self):
        r = self.client.post(self.url, {"purpose": LabVisit.Purpose.CLASS})
        self.assertEqual(r.status_code, 200)
        self.assertFalse(LabVisit.objects.exists())

    def test_active_visits_filter_by_room_and_show_building(self):
        other_room = Room.objects.create(name="Electronics Lab", building="GLE")
        LabVisit.objects.create(
            user=self.u,
            room=self.cl1,
            purpose=LabVisit.Purpose.CLASS,
        )
        other_user = User.objects.create_user(
            username="other-room-student",
            email="other@cit.edu",
            password="SecurePass123!",
            role=User.Role.STUDENT,
        )
        LabVisit.objects.create(
            user=other_user,
            room=other_room,
            purpose=LabVisit.Purpose.RESEARCH,
        )
        self.u.role = User.Role.INSTRUCTOR
        self.u.save(update_fields=["role"])

        response = self.client.get(
            reverse("access_logging:active"),
            {"location": self.cl1.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "NGE")
        self.assertContains(response, "Computer Lab 1")
        self.assertEqual(len(response.context["visits"]), 1)
        self.assertEqual(response.context["visits"][0].room, self.cl1)
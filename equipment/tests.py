from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from access_logging.models import LabVisit

from .models import Asset, Condition, EquipmentLog

User = get_user_model()


class EquipmentBehaviorTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="labuser",
            email="labuser@cit.edu",
            password="SecurePass123!",
        )
        self.client.force_login(self.user)
        self.visit = LabVisit.objects.create(
            user=self.user,
            lab_location="Computer Lab 1",
            purpose=LabVisit.Purpose.CLASS,
        )
        self.asset = Asset.objects.create(asset_code="EQ-001", name="Microscope")

    def test_inventory_and_borrow_templates_resolve(self):
        response = self.client.get(reverse("equipment:inventory"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "equipment/inventory.html")

        response = self.client.get(reverse("equipment:borrow"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "equipment/borrow.html")

    def test_history_return_and_staff_asset_templates_resolve(self):
        log = EquipmentLog.objects.create(
            visit=self.visit,
            asset=self.asset,
            pre_condition=Condition.GOOD,
        )
        self.asset.availability_status = Asset.Availability.BORROWED
        self.asset.save(update_fields=["availability_status"])

        response = self.client.get(reverse("equipment:mine"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "equipment/my_equipment.html")

        response = self.client.get(
            reverse("equipment:return", kwargs={"pk": log.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "equipment/return.html")

        self.user.role = User.Role.INSTRUCTOR
        self.user.save(update_fields=["role"])
        response = self.client.get(reverse("equipment:asset_new"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "equipment/asset_form.html")

    def test_borrow_and_return_update_equipment_availability(self):
        response = self.client.post(
            reverse("equipment:borrow"),
            {"asset": self.asset.pk, "pre_condition": Condition.GOOD},
        )

        self.assertRedirects(response, reverse("equipment:mine"))
        log = EquipmentLog.objects.get(asset=self.asset)
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.availability_status, Asset.Availability.BORROWED)
        self.assertIsNone(log.returned_at)

        response = self.client.post(
            reverse("equipment:return", kwargs={"pk": log.pk}),
            {"post_condition": Condition.GOOD},
        )

        self.assertRedirects(response, reverse("equipment:mine"))
        log.refresh_from_db()
        self.asset.refresh_from_db()
        self.assertIsNotNone(log.returned_at)
        self.assertEqual(self.asset.availability_status, Asset.Availability.AVAILABLE)

    def test_borrowing_requires_an_active_visit(self):
        self.visit.status = LabVisit.Status.COMPLETED
        self.visit.save(update_fields=["status"])

        response = self.client.get(reverse("equipment:borrow"))

        self.assertRedirects(response, reverse("access_logging:check_in"))
        self.assertFalse(EquipmentLog.objects.exists())

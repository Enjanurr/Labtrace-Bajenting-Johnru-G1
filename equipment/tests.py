from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from access_logging.models import LabVisit

from .forms import AssetForm, BorrowForm, ReturnForm, RoomForm
from .models import (
    Asset,
    CONDITION_CHOICES,
    Condition,
    EquipmentLog,
    Room,
)

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

    def test_defective_asset_is_blocked_and_return_defect_updates_status(self):
        for status in (
            Asset.Availability.MAINTENANCE,
            Asset.Availability.MISSING,
        ):
            self.asset.availability_status = status
            self.asset.save(update_fields=["availability_status"])
            response = self.client.post(
                reverse("equipment:borrow"),
                {"asset": self.asset.pk, "pre_condition": Condition.GOOD},
            )
            self.assertEqual(response.status_code, 200)
            self.assertFalse(EquipmentLog.objects.filter(asset=self.asset).exists())

        self.asset.availability_status = Asset.Availability.BORROWED
        self.asset.save(update_fields=["availability_status"])
        log = EquipmentLog.objects.create(
            visit=self.visit,
            asset=self.asset,
            pre_condition=Condition.GOOD,
        )
        response = self.client.post(
            reverse("equipment:return", kwargs={"pk": log.pk}),
            {"post_condition": Condition.DAMAGED},
        )
        self.asset.refresh_from_db()
        self.assertEqual(
            self.asset.availability_status,
            Asset.Availability.MAINTENANCE,
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("incidents:new"), response["Location"])

    def test_borrow_and_return_forms_use_the_shared_condition_choices(self):
        borrow_form = BorrowForm()
        return_form = ReturnForm()
        expected = [choice[0] for choice in CONDITION_CHOICES]
        self.assertEqual(
            [choice[0] for choice in borrow_form.fields["pre_condition"].choices
             if choice[0]],
            expected,
        )
        self.assertEqual(
            [choice[0] for choice in return_form.fields["post_condition"].choices
             if choice[0]],
            expected,
        )


class RoomAndAssetCodeTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="roomadmin",
            email="roomadmin@cit.edu",
            password="SecurePass123!",
            role=User.Role.ADMIN,
        )
        self.client.force_login(self.admin)

    def test_room_form_derives_unique_prefix(self):
        form = RoomForm(
            data={
                "name": "Computer Lab 1",
                "code_prefix": "",
                "lab_type": Room.LabType.COMPUTER,
                "building": "Main",
                "capacity": 30,
                "is_active": True,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        room = form.save()
        self.assertEqual(room.code_prefix, "CL1")

    def test_asset_form_generates_sequential_codes_and_filters_by_room(self):
        room = Room.objects.create(
            name="Computer Lab 1",
            code_prefix="CL1",
        )
        other_room = Room.objects.create(
            name="Computer Lab 2",
            code_prefix="CL2",
        )

        first_form = AssetForm(
            data={
                "room": room.pk,
                "name": "Microscope",
                "availability_status": Asset.Availability.AVAILABLE,
            }
        )
        self.assertTrue(first_form.is_valid(), first_form.errors)
        first = first_form.save()

        second_form = AssetForm(
            data={
                "room": room.pk,
                "name": "Projector",
                "availability_status": Asset.Availability.AVAILABLE,
            }
        )
        self.assertTrue(second_form.is_valid(), second_form.errors)
        second = second_form.save()

        other = Asset.objects.create(
            asset_code="CL2-001",
            name="Router",
            room=other_room,
        )

        self.assertEqual(first.asset_code, "CL1-001")
        self.assertEqual(second.asset_code, "CL1-002")
        response = self.client.get(
            reverse("equipment:inventory"),
            {"room": str(room.pk)},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Microscope")
        self.assertContains(response, "Projector")
        self.assertNotContains(response, other.name)

    def test_invalid_room_filter_is_safe(self):
        response = self.client.get(
            reverse("equipment:inventory"),
            {"room": "not-a-room"},
        )
        self.assertEqual(response.status_code, 200)

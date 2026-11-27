from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, SimpleTestCase, TestCase
from django.urls import reverse

from access_logging.models import LabVisit

from .models import Asset, Condition, EquipmentLog, Room
from .room_scope import BorrowScope, borrow_scope

from . import views


class InventoryViewTests(SimpleTestCase):
    def test_inventory_renders_html_template(self):
        request = RequestFactory().get("/equipment/")
        request.user = SimpleNamespace(is_authenticated=True)
        open_logs = Mock()
        open_logs.select_related.return_value = []
        scope = BorrowScope(restricted=False)

        with (
            patch("equipment.views.Asset.objects.all", return_value=[]),
            patch("equipment.views.EquipmentLog.objects.filter", return_value=open_logs),
            patch("equipment.views.borrow_scope", return_value=scope),
            patch("equipment.views.filter_assets", side_effect=lambda request, qs, scope=None: qs),
            patch("equipment.views.filter_context", return_value={}),
            patch("equipment.views.render") as render_mock,
        ):
            views.inventory_view(request)

        self.assertEqual(render_mock.call_args.args[1], "equipment/inventory.html")


class RoomBorrowScopeTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="student",
            email="student@cit.edu",
            password="testpass",
            role=user_model.Role.STUDENT,
        )
        self.room = Room.objects.create(
            name="Computer Lab 1",
            code_prefix="CL1",
        )
        self.visit = LabVisit.objects.create(
            user=self.user,
            lab_location=self.room.name,
            purpose=LabVisit.Purpose.CLASS,
            room=self.room,
        )
        self.asset = Asset.objects.create(
            asset_code="CL1-001",
            name="Microscope",
            room=self.room,
        )
        self.client.force_login(self.user)

    def test_borrow_scope_limits_asset_to_active_visit_room(self):
        other_room = Room.objects.create(
            name="Electronics Lab",
            code_prefix="EL",
        )
        other_asset = Asset.objects.create(
            asset_code="EL-001",
            name="Oscilloscope",
            room=other_room,
        )

        response = self.client.get(reverse("equipment:inventory"))

        self.assertContains(response, self.asset.name)
        self.assertNotContains(response, other_asset.name)

    def test_borrow_rejects_asset_from_another_room(self):
        other_room = Room.objects.create(
            name="Electronics Lab",
            code_prefix="EL",
        )
        other_asset = Asset.objects.create(
            asset_code="EL-001",
            name="Oscilloscope",
            room=other_room,
        )

        response = self.client.post(
            reverse("equipment:borrow"),
            {
                "asset": other_asset.pk,
                "pre_condition": Condition.GOOD,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            EquipmentLog.objects.filter(asset=other_asset).exists()
        )


class EquipmentReturningTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="returner",
            email="returner@cit.edu",
            password="testpass",
            role=user_model.Role.STUDENT,
        )
        self.room = Room.objects.create(
            name="Computer Lab 1",
            code_prefix="CL1",
        )
        self.visit = LabVisit.objects.create(
            user=self.user,
            lab_location=self.room.name,
            purpose=LabVisit.Purpose.CLASS,
            room=self.room,
        )
        self.asset = Asset.objects.create(
            asset_code="CL1-001",
            name="Microscope",
            room=self.room,
            availability_status=Asset.Availability.BORROWED,
        )
        self.log = EquipmentLog.objects.create(
            visit=self.visit,
            asset=self.asset,
            pre_condition=Condition.GOOD,
        )
        self.client.force_login(self.user)

    def test_owner_can_return_asset_with_notes(self):
        response = self.client.post(
            reverse("equipment:return", kwargs={"pk": self.log.pk}),
            {
                "post_condition": Condition.GOOD,
                "post_condition_notes": "Returned in good condition.",
            },
        )

        self.assertRedirects(response, reverse("equipment:mine"))
        self.log.refresh_from_db()
        self.asset.refresh_from_db()
        self.assertIsNotNone(self.log.returned_at)
        self.assertEqual(
            self.log.post_condition_notes,
            "Returned in good condition.",
        )
        self.assertEqual(
            self.asset.availability_status,
            Asset.Availability.AVAILABLE,
        )

    def test_damaged_return_moves_asset_to_maintenance(self):
        response = self.client.post(
            reverse("equipment:return", kwargs={"pk": self.log.pk}),
            {
                "post_condition": Condition.DAMAGED,
                "post_condition_notes": "Cracked casing.",
            },
        )

        self.assertRedirects(response, reverse("equipment:mine"))
        self.asset.refresh_from_db()
        self.assertEqual(
            self.asset.availability_status,
            Asset.Availability.MAINTENANCE,
        )

from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import RequestFactory, SimpleTestCase

from . import views


class InventoryViewTests(SimpleTestCase):
    def test_inventory_renders_html_template(self):
        request = RequestFactory().get("/equipment/")
        request.user = SimpleNamespace(is_authenticated=True)
        open_logs = Mock()
        open_logs.select_related.return_value = []

        with (
            patch("equipment.views.Asset.objects.all", return_value=[]),
            patch("equipment.views.EquipmentLog.objects.filter", return_value=open_logs),
            patch("equipment.views.render") as render_mock,
        ):
            views.inventory_view(request)

        self.assertEqual(render_mock.call_args.args[1], "equipment/inventory.html")

from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from access_logging.models import LabVisit
from equipment.models import EquipmentLog
from incidents.models import Incident

User = get_user_model()


def seed(*extra):
    call_command("seed_demo_data", "--force", *extra, stdout=StringIO())


class SeedCommandTests(TestCase):
    def test_creates_all_roles_and_data(self):
        seed()
        roles = set(User.objects.filter(email__startswith="demo.").values_list("role", flat=True))
        self.assertEqual(roles, {"ADMIN", "INSTRUCTOR", "RESEARCHER", "STUDENT"})
        self.assertEqual(LabVisit.objects.filter(check_out_time__isnull=True).count(), 4)
        self.assertEqual(EquipmentLog.objects.filter(returned_at__isnull=True).count(), 2)
        self.assertEqual(
            set(Incident.objects.values_list("status", flat=True)),
            {"REPORTED", "INVESTIGATION", "RESOLVED", "CLOSED"},
        )

    def test_second_run_does_not_duplicate(self):
        seed()
        before = (User.objects.count(), LabVisit.objects.count(), Incident.objects.count())
        seed()
        self.assertEqual(before, (User.objects.count(), LabVisit.objects.count(), Incident.objects.count()))

    def test_reset_rebuilds_cleanly(self):
        seed()
        seed("--reset")
        self.assertEqual(User.objects.filter(email__startswith="demo.").count(), 7)
        self.assertEqual(Incident.objects.count(), 4)
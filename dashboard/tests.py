from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from access_logging.models import LabVisit
from equipment.models import Asset, EquipmentLog
from incidents.models import Incident, IncidentStatusHistory

from . import fieldmap as fm

User = get_user_model()

# ---------------------------------------------------------------------------
# ADJUST HERE if your models need more required fields to be created.
# Example: VISIT_EXTRA = {"purpose": "CLASS"}, LOG_EXTRA = {"pre_condition": "GOOD"}
VISIT_EXTRA = {"purpose": "CLASS"}
ASSET_EXTRA = {}
LOG_EXTRA = {"pre_condition": "GOOD"}
AVAILABLE, BORROWED = "AVAILABLE", "BORROWED"   # any two status strings
# If the lab is a ForeignKey, change make_visit() to create/get the lab object.
# ---------------------------------------------------------------------------


def make_user(email, role="STUDENT", first="Test"):
    return User.objects.create_user(
        username=email, email=email, password="pass12345!", role=role,
        first_name=first, last_name=role.title(),
    )


def make_visit(user, lab="Lab A", out=False, when=None):
    v = LabVisit.objects.create(**{fm.VISIT_USER: user, fm.VISIT_LAB: lab, **VISIT_EXTRA})
    updates = {}
    if when:
        updates[fm.VISIT_IN] = when
    if out:
        updates[fm.VISIT_OUT] = when or timezone.now()
    if updates:
        LabVisit.objects.filter(pk=v.pk).update(**updates)
        v.refresh_from_db()
    return v


def make_asset(name, status=AVAILABLE):
    return Asset.objects.create(**{fm.ASSET_NAME: name, fm.ASSET_STATUS: status, **ASSET_EXTRA})


def make_log(visit, asset, returned=False):
    log = EquipmentLog.objects.create(**{fm.LOG_VISIT: visit, fm.LOG_ASSET: asset, **LOG_EXTRA})
    if returned:
        EquipmentLog.objects.filter(pk=log.pk).update(**{fm.LOG_RETURNED: timezone.now()})
        log.refresh_from_db()
    return log


class BaseDashboardTest(TestCase):
    def setUp(self):
        self.student = make_user("student@cit.edu", "STUDENT")
        self.researcher = make_user("researcher@cit.edu", "RESEARCHER")
        self.instructor = make_user("instructor@cit.edu", "INSTRUCTOR")
        self.admin = make_user("admin@cit.edu", "ADMIN")
        self.alice = make_user("alice@cit.edu", first="Alice")
        self.bob = make_user("bob@cit.edu", first="Bob")
        self.carol = make_user("carol@cit.edu", first="Carol")
        self.dave = make_user("dave@cit.edu", first="Dave")

    def get(self, name, user=None, **params):
        if user:
            self.client.force_login(user)
        return self.client.get(reverse(name), params)


class AccessTests(BaseDashboardTest):
    URLS = ("dashboard:central", "dashboard:central_data", "dashboard:audit")

    def test_anonymous_redirected_to_login(self):
        for name in self.URLS:
            r = self.client.get(reverse(name))
            self.assertEqual(r.status_code, 302, name)
            self.assertIn("login", r.url)

    def test_students_and_researchers_forbidden(self):
        for user in (self.student, self.researcher):
            for name in self.URLS:
                self.assertEqual(self.get(name, user).status_code, 403, f"{user.role} {name}")

    def test_instructor_and_admin_allowed(self):
        for user in (self.instructor, self.admin):
            for name in self.URLS:
                self.assertEqual(self.get(name, user).status_code, 200, f"{user.role} {name}")


class CentralDashboardTests(BaseDashboardTest):
    def test_occupancy_counts_only_active_visits(self):
        make_visit(self.alice, "Lab A")
        make_visit(self.bob, "Lab A")
        make_visit(self.carol, "Lab B")
        make_visit(self.dave, "Lab A", out=True)   # checked out: must not count
        r = self.get("dashboard:central", self.instructor)
        occ = {row["lab"]: row["count"] for row in r.context["occupancy"]}
        self.assertEqual(occ, {"Lab A": 2, "Lab B": 1})
        self.assertEqual(r.context["total_inside"], 3)
        self.assertEqual(len(r.context["visits"]), 3)

    def test_json_endpoint_matches_dashboard(self):
        make_visit(self.alice, "Lab A")
        make_visit(self.bob, "Lab B")
        data = self.get("dashboard:central_data", self.admin).json()
        self.assertEqual(data["total_inside"], 2)
        self.assertEqual({r["lab"] for r in data["occupancy"]}, {"Lab A", "Lab B"})
        self.assertEqual(data["unresolved"], 0)

    def test_equipment_and_current_borrowers_visible(self):
        out_asset = make_asset("Projector X", BORROWED)
        make_log(make_visit(self.alice, "Lab A"), out_asset)
        back_asset = make_asset("Returned Cam", AVAILABLE)
        make_log(make_visit(self.bob, "Lab A", out=True), back_asset, returned=True)

        r = self.get("dashboard:central", self.admin)
        borrowers = r.context["borrowers"]
        self.assertEqual(len(borrowers), 1)
        self.assertEqual(borrowers[0]["borrower"], self.alice)
        self.assertEqual(borrowers[0]["asset_name"], "Projector X")
        self.assertContains(r, "Projector X")
        self.assertNotContains(r, "Returned Cam")   # returned items are not "currently borrowed"

        counts = {row["status"]: row["count"] for row in r.context["asset_summary"]}
        self.assertEqual(counts, {BORROWED: 1, AVAILABLE: 1})

    def test_unresolved_incident_count(self):
        for status in ("REPORTED", "INVESTIGATION", "RESOLVED", "CLOSED"):
            Incident.objects.create(reporter=self.alice, title=f"{status} case", description="x", status=status)
        r = self.get("dashboard:central", self.instructor)
        summary = r.context["incidents"]
        self.assertEqual(summary["total"], 2)        # Reported + Investigation only
        self.assertEqual(summary["reported"], 1)
        self.assertEqual(summary["investigation"], 1)
        self.assertContains(r, "REPORTED case")
        self.assertNotContains(r, "CLOSED case")


class AuditTrailTests(BaseDashboardTest):
    def setUp(self):
        super().setUp()
        # Alice: current check-in + a laptop loan in Lab A
        self.visit_a = make_visit(self.alice, "Lab A")
        self.laptop = make_asset("Laptop 1", BORROWED)
        self.log = make_log(self.visit_a, self.laptop)
        # Bob: an old visit in Lab B (January 2026)
        self.old = timezone.make_aware(datetime(2026, 1, 10, 9, 0))
        self.visit_b = make_visit(self.bob, "Lab B", out=False, when=self.old)
        # Incidents: one reported by Alice about the laptop, one investigated by the instructor
        self.inc1 = Incident.objects.create(
            reporter=self.alice, visit=self.visit_a, equipment_log=self.log,
            title="Laptop screen cracked", description="x",
        )
        IncidentStatusHistory.objects.create(
            incident=self.inc1, from_status="", to_status="REPORTED", changed_by=self.alice,
        )
        self.inc2 = Incident.objects.create(
            reporter=self.carol, title="Noisy fan", description="x", status="INVESTIGATION",
        )
        IncidentStatusHistory.objects.create(
            incident=self.inc2, from_status="REPORTED", to_status="INVESTIGATION", changed_by=self.instructor,
        )

    def events(self, **params):
        r = self.get("dashboard:audit", self.admin, **params)
        self.assertEqual(r.status_code, 200)
        return list(r.context["page_obj"].object_list)

    def test_no_filters_returns_every_event_type(self):
        types = {e["type"] for e in self.events()}
        self.assertTrue({"Check-in", "Borrowed", "Incident"} <= types)

    def test_filter_by_user(self):
        events = self.events(user="alice")
        self.assertTrue(events)
        self.assertTrue(all(e["user"] == self.alice for e in events))

    def test_filter_by_lab(self):
        events = self.events(lab="Lab B")
        self.assertTrue(events)
        self.assertTrue(all(str(e["lab"]) == "Lab B" for e in events))
        self.assertTrue(all(e["user"] == self.bob for e in events))

    def test_filter_by_asset(self):
        events = self.events(asset="Laptop")
        self.assertTrue(events)
        self.assertTrue(all(e["asset"] == "Laptop 1" for e in events))
        self.assertNotIn("Check-in", {e["type"] for e in events})

    def test_filter_by_incident_status(self):
        events = self.events(incident_status="INVESTIGATION")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["type"], "Incident")
        self.assertEqual(events[0]["status"], "Under Investigation")
        self.assertIn("Noisy fan", events[0]["detail"])

    def test_filter_by_date_range(self):
        events = self.events(date_from="2026-01-01", date_to="2026-01-31")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["user"], self.bob)
        self.assertEqual(events[0]["type"], "Check-in")

    def test_filters_combine(self):
        events = self.events(user="alice", lab="Lab A", asset="Laptop")
        self.assertTrue(events)
        self.assertTrue(all(e["user"] == self.alice and e["asset"] == "Laptop 1" for e in events))

    def test_invalid_filter_values_do_not_crash(self):
        self.assertEqual(len(self.events(date_from="garbage", incident_status="NOPE")), len(self.events()))

    def test_newest_events_first(self):
        stamps = [e["when"] for e in self.events()]
        self.assertEqual(stamps, sorted(stamps, reverse=True))
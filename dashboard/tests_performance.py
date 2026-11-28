import math
import time
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from access_logging.models import LabVisit
from equipment.models import Asset, EquipmentLog
from incidents.models import Incident, IncidentStatusHistory

from . import fieldmap as fm
from .choices import pick
from .tests import ASSET_EXTRA, LOG_EXTRA, VISIT_EXTRA, make_user

User = get_user_model()
N = 150                      # rows per table: ~600 audit events in total
QUERY_BUDGET = 12            # session + user + 5 event queries + headroom


class AuditPerformanceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        now = timezone.now()
        cls.admin = make_user("perf-admin@cit.edu", "ADMIN")
        labs = ["Lab A", "Lab B", "Lab C"]

        users = User.objects.bulk_create([
            User(username=f"perf{i}@cit.edu", email=f"perf{i}@cit.edu",
                 first_name="Perf", last_name=str(i), role="STUDENT", password="!")
            for i in range(N)
        ])
        visits = LabVisit.objects.bulk_create([
            LabVisit(**{
                fm.VISIT_USER: u, fm.VISIT_LAB: labs[i % 3],
                fm.VISIT_IN: now - timedelta(hours=i + 2),
                fm.VISIT_OUT: now - timedelta(hours=i + 1) if i % 2 else None,
                **VISIT_EXTRA,
            })
            for i, u in enumerate(users)
        ])
        status = pick(Asset, fm.ASSET_STATUS, "avail")
        assets = Asset.objects.bulk_create([
            Asset(**{fm.ASSET_NAME: f"Perf Asset {i}", fm.ASSET_STATUS: status,
                     "asset_code": f"PERF-{i:04d}", **ASSET_EXTRA})
            for i in range(N)
        ])
        logs = EquipmentLog.objects.bulk_create([
            EquipmentLog(**{
                fm.LOG_VISIT: visits[i], fm.LOG_ASSET: assets[i],
                fm.LOG_BORROWED: now - timedelta(hours=i + 1),
                fm.LOG_RETURNED: now - timedelta(minutes=i) if i % 2 else None,
                **LOG_EXTRA,
            })
            for i in range(N)
        ])
        incidents = Incident.objects.bulk_create([
            Incident(reporter=users[i], visit=visits[i], equipment_log=logs[i],
                     title=f"Perf incident {i}", description="x", status="REPORTED")
            for i in range(N)
        ])
        IncidentStatusHistory.objects.bulk_create([
            IncidentStatusHistory(incident=inc, from_status="", to_status="REPORTED",
                                  changed_by=users[i])
            for i, inc in enumerate(incidents)
        ])

    def api(self, **params):
        self.client.force_login(self.admin)
        return self.client.get(reverse("dashboard:audit_api"), params)

    # ---- pagination ----------------------------------------------------
    def test_pagination_contract(self):
        first = self.api(page_size=25).json()
        self.assertGreater(first["count"], 500)
        self.assertEqual(first["num_pages"], math.ceil(first["count"] / 25))
        self.assertEqual(len(first["results"]), 25)
        self.assertTrue(first["has_next"])
        self.assertFalse(first["has_previous"])

        second = self.api(page_size=25, page=2).json()
        key = lambda e: (e["type"], e["user"], e["asset"], e["detail"], e["when"])
        self.assertFalse({key(e) for e in first["results"]} & {key(e) for e in second["results"]})

    def test_page_beyond_last_returns_last_page(self):
        data = self.api(page_size=25, page=99999).json()
        self.assertEqual(data["page"], data["num_pages"])
        self.assertFalse(data["has_next"])

    def test_page_size_is_capped(self):
        data = self.api(page_size=9999).json()
        self.assertEqual(data["page_size"], 100)
        self.assertLessEqual(len(data["results"]), 100)

    def test_bad_page_size_falls_back(self):
        self.assertEqual(self.api(page_size="abc").json()["page_size"], 25)

    # ---- query efficiency ----------------------------------------------
    def count_queries(self, **params):
        with CaptureQueriesContext(connection) as ctx:
            self.assertEqual(self.api(**params).status_code, 200)
        return len(ctx)

    def test_query_count_does_not_grow_with_page_size(self):
        """A constant count proves there is no N+1 on related rows."""
        small = self.count_queries(page_size=5)
        large = self.count_queries(page_size=100)
        self.assertEqual(small, large)
        self.assertLessEqual(large, QUERY_BUDGET)

    def test_filtered_queries_stay_within_budget(self):
        self.assertLessEqual(
            self.count_queries(user="perf1", lab="Lab B", date_from="2020-01-01"), QUERY_BUDGET)
        self.assertLessEqual(self.count_queries(incident_status="REPORTED"), QUERY_BUDGET)
        self.assertLessEqual(self.count_queries(asset="Perf Asset 7"), QUERY_BUDGET)

    def test_response_time_is_reasonable(self):
        started = time.perf_counter()
        self.assertEqual(self.api(page_size=25).status_code, 200)
        self.assertLess(time.perf_counter() - started, 3.0)

    # ---- indexes -------------------------------------------------------
    def assertIndexed(self, model, field_name):
        column = model._meta.get_field(field_name).column
        with connection.cursor() as cursor:
            constraints = connection.introspection.get_constraints(cursor, model._meta.db_table)
        self.assertTrue(
            any(c["columns"] and c["columns"][0] == column and (c.get("index") or c.get("primary_key"))
                for c in constraints.values()),
            f"No index starting with {model._meta.db_table}.{column}",
        )

    def test_audit_filter_columns_are_indexed(self):
        self.assertIndexed(LabVisit, fm.VISIT_IN)
        self.assertIndexed(LabVisit, fm.VISIT_OUT)
        self.assertIndexed(LabVisit, fm.VISIT_LAB)
        self.assertIndexed(EquipmentLog, fm.LOG_BORROWED)
        self.assertIndexed(EquipmentLog, fm.LOG_RETURNED)
        self.assertIndexed(IncidentStatusHistory, "changed_at")
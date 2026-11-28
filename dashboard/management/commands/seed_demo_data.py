from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from access_logging.models import LabVisit
from dashboard.choices import pick
from equipment.models import Asset, EquipmentLog, Room
from incidents.models import Incident
from incidents.services import change_status, open_incident

User = get_user_model()

DOMAIN = "cit.edu"
ASSET_PREFIX = "DEMO-"
LAB_NAMES = ["Computer Lab 1", "Computer Lab 2", "Research Lab"]

USERS = [  # (local part, role, first, last, department)
    ("demo.admin", "ADMIN", "Alex", "Admin", "Administration"),
    ("demo.instructor", "INSTRUCTOR", "Ines", "Villanueva", "CCS"),
    ("demo.student1", "STUDENT", "Sofia", "Santos", "CCS"),
    ("demo.student2", "STUDENT", "Miguel", "Reyes", "CCS"),
    ("demo.student3", "STUDENT", "Ana", "Cruz", "CCS"),
    ("demo.student4", "STUDENT", "Luis", "Garcia", "CCS"),
]

ASSETS = [
    "Laptop Dell 5420", "Projector Epson X06", "Arduino Starter Kit", "Oscilloscope Rigol",
    "Raspberry Pi 4", "Network Switch 24-port", "Webcam Logitech C920", "Soldering Station",
    "Multimeter Fluke", "HDMI Cable Set",
]


def demo_emails():
    return [f"{u[0]}@{DOMAIN}" for u in USERS]


class Command(BaseCommand):
    help = "Create demo users, assets, visits, loans and incidents for presentations."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true",
                            help="Delete existing demo data first, then re-create it.")
        parser.add_argument("--password", default="Demo12345!",
                            help="Password for every demo account.")
        parser.add_argument("--force", action="store_true",
                            help="Allow running when DEBUG is off.")

    def handle(self, *args, **opts):
        if not settings.DEBUG and not opts["force"]:
            raise CommandError("Refusing to run with DEBUG off. Use --force if you really mean it.")

        with transaction.atomic():
            if opts["reset"]:
                self.wipe()
            users = self.ensure_users(opts["password"])
            if Asset.objects.filter(asset_code__startswith=ASSET_PREFIX).exists():
                self.stdout.write(self.style.WARNING(
                    "Demo operational data already exists. Use --reset to rebuild it."))
            else:
                self.build_operational_data(users)

        self.report(opts["password"])

    # ---- cleanup -------------------------------------------------------
    def wipe(self):
        demo_users = User.objects.filter(email__in=demo_emails())
        Incident.objects.filter(reporter__in=demo_users).delete()
        EquipmentLog.objects.filter(asset__asset_code__startswith=ASSET_PREFIX).delete()
        LabVisit.objects.filter(user__in=demo_users).delete()
        Asset.objects.filter(asset_code__startswith=ASSET_PREFIX).delete()
        demo_users.delete()

    # ---- users ---------------------------------------------------------
    def ensure_users(self, password):
        users = {}
        for i, (local, role, first, last, dept) in enumerate(USERS, start=1):
            email = f"{local}@{DOMAIN}"
            user = User.objects.filter(email=email).first()
            if not user:
                user = User.objects.create_user(
                    username=email, email=email, password=password, role=role,
                    first_name=first, last_name=last, department=dept,
                    institutional_id=f"DEMO-{i:04d}",
                )
            users[local] = user
        return users

    # ---- visits / loans / incidents -----------------------------------
    def build_operational_data(self, u):
        now = timezone.now()
        labs = self.ensure_rooms()
        purposes = [pick(LabVisit, "purpose", k, default=k.title())
                    for k in ("class", "research", "project", "test")]
        closed = pick(LabVisit, "status", "out", "clos", "complet", "done", "end")

        available = pick(Asset, "availability_status", "avail")
        borrowed = pick(Asset, "availability_status", "borrow", "loan", "in use")
        repair = pick(Asset, "availability_status", "repair", "maint", "damag")
        good = pick(EquipmentLog, "pre_condition", "good")
        post_good = pick(EquipmentLog, "post_condition", "good")
        post_damaged = pick(EquipmentLog, "post_condition", "damag", "broken")

        assets = {}
        for i, name in enumerate(ASSETS, start=1):
            assets[name] = Asset.objects.create(
                name=name,
                asset_code=f"{ASSET_PREFIX}{i:03d}",
                availability_status=available,
                room=labs[(i - 1) % len(labs)],
            )

        def visit(user, lab, purpose, started, ended=None):
            v = LabVisit.objects.create(
                user=user,
                lab_location=lab.name,
                room=lab,
                purpose=purpose,
            )
            fields = {"check_in_time": started}
            if ended:
                fields.update(check_out_time=ended,
                              duration_minutes=int((ended - started).total_seconds() // 60))
                if closed is not None:
                    fields["status"] = closed
            LabVisit.objects.filter(pk=v.pk).update(**fields)
            v.refresh_from_db()
            return v

        def loan(vis, asset, borrowed_at, returned_at=None, post=None):
            log = EquipmentLog.objects.create(visit=vis, asset=asset, pre_condition=good)
            fields = {"borrowed_at": borrowed_at}
            if returned_at:
                fields.update(returned_at=returned_at, post_condition=post)
            EquipmentLog.objects.filter(pk=log.pk).update(**fields)
            log.refresh_from_db()
            return log

        # History first (closed), so the "one active visit per user" rule is never in the way.
        h1 = visit(u["demo.student1"], labs[0], purposes[0], now - timedelta(days=3, hours=3), now - timedelta(days=3, hours=1))
        h2 = visit(u["demo.student2"], labs[1], purposes[2], now - timedelta(days=2, hours=5), now - timedelta(days=2, hours=2))
        h3 = visit(u["demo.student3"], labs[0], purposes[0], now - timedelta(days=1, hours=4), now - timedelta(days=1, hours=2))
        visit(u["demo.student4"], labs[1], purposes[3], now - timedelta(hours=30), now - timedelta(hours=28))

        loan(h1, assets["Webcam Logitech C920"], now - timedelta(days=3, hours=3),
             now - timedelta(days=3, hours=1), post_good)
        loan(h2, assets["Soldering Station"], now - timedelta(days=2, hours=5),
             now - timedelta(days=2, hours=2), post_good)
        damaged_log = loan(h3, assets["Multimeter Fluke"], now - timedelta(days=1, hours=4),
                           now - timedelta(days=1, hours=2), post_damaged)
        assets["Multimeter Fluke"].availability_status = repair
        assets["Multimeter Fluke"].save(update_fields=["availability_status"])

        # Active visits: this is what the live dashboard shows.
        a1 = visit(u["demo.student1"], labs[0], purposes[0], now - timedelta(minutes=95))
        a2 = visit(u["demo.student2"], labs[0], purposes[2], now - timedelta(minutes=40))
        a3 = visit(u["demo.student3"], labs[1], purposes[0], now - timedelta(minutes=20))
        # Active loans.
        laptop_log = loan(a1, assets["Laptop Dell 5420"], now - timedelta(minutes=85))
        loan(a3, assets["Arduino Starter Kit"], now - timedelta(minutes=15))
        for name in ("Laptop Dell 5420", "Arduino Starter Kit"):
            assets[name].availability_status = borrowed
            assets[name].save(update_fields=["availability_status"])

        # Incidents, one per status.
        admin, instructor = u["demo.admin"], u["demo.instructor"]
        S, C, V = Incident.Status, Incident.Category, Incident.Severity

        def incident(reporter, title, text, cat, sev, vis=None, log=None, steps=()):
            inc = Incident.objects.create(reporter=reporter, title=title, description=text,
                                          category=cat, severity=sev, visit=vis, equipment_log=log)
            open_incident(inc, reporter)
            for actor, status, note in steps:
                change_status(inc, actor, status, note)
            return inc

        incident(u["demo.student3"], "Multimeter reads incorrectly after use",
                 "Display shows random values and the probe cable is frayed.",
                 C.DAMAGE, V.HIGH, h3, damaged_log)
        incident(u["demo.student1"], "Laptop screen flickers",
                 "Screen flickers every few minutes on battery power.",
                 C.MALFUNCTION, V.MEDIUM, a1, laptop_log,
                 steps=[(instructor, S.INVESTIGATION, "Checking the display cable.")])
        incident(u["demo.student2"], "Mouse scroll wheel stuck",
                 "Scroll wheel does not turn on workstation 6.",
                 C.MALFUNCTION, V.LOW, a2,
                 steps=[(instructor, S.INVESTIGATION, ""),
                        (admin, S.RESOLVED, "Replaced the mouse with a spare.")])
        incident(
            u["demo.student4"],
            "Aircon too loud in Research Lab",
            "Rattling noise from the ceiling unit.",
            C.OTHER,
            V.LOW,
            steps=[
                (instructor, S.INVESTIGATION, ""),
                (admin, S.RESOLVED, "Maintenance tightened the unit."),
                (admin, S.CLOSED, "Confirmed fixed."),
            ],
        )

    def lab_values(self):
        values = [v for v, _ in LabVisit._meta.get_field("lab_location").flatchoices]
        return values[:3] or LAB_NAMES

    def ensure_rooms(self):
        rooms = []
        for name in self.lab_values():
            prefix = "".join(part[0] for part in name.split() if part).upper()[:8]
            room, _ = Room.objects.get_or_create(
                name=name,
                defaults={"code_prefix": prefix},
            )
            rooms.append(room)
        return rooms

    def report(self, password):
        self.stdout.write(self.style.SUCCESS("\nDemo data ready.\n"))
        self.stdout.write(f"{'Role':<12} {'Email':<28} Password")
        for local, role, *_ in USERS:
            self.stdout.write(f"{role:<12} {local + '@' + DOMAIN:<28} {password}")
        self.stdout.write(
            f"\nActive visits: {LabVisit.objects.filter(check_out_time__isnull=True).count()}"
            f" | Active loans: {EquipmentLog.objects.filter(returned_at__isnull=True).count()}"
            f" | Incidents: {Incident.objects.count()}\n")
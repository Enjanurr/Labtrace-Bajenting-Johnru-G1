import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from incidents.models import Incident, IncidentAttachment

from .tests import make_asset, make_log, make_user, make_visit

MEDIA = tempfile.mkdtemp()
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 32


@override_settings(MEDIA_ROOT=MEDIA)
class SecureDownloadTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        self.owner = make_user("owner@cit.edu", "STUDENT")
        self.other = make_user("other@cit.edu", "STUDENT")
        self.instructor = make_user("ins@cit.edu", "INSTRUCTOR")
        self.admin = make_user("adm@cit.edu", "ADMIN")

        incident = Incident.objects.create(reporter=self.owner, title="Cracked", description="x")
        self.attachment = IncidentAttachment.objects.create(
            incident=incident, original_name="proof.png", uploaded_by=self.owner,
            file=SimpleUploadedFile("proof.png", PNG, content_type="image/png"),
        )
        self.visit = make_visit(self.owner, "Lab A")
        self.log = make_log(self.visit, make_asset("Camera"))
        self.log.pre_condition_img.save("pre.png", SimpleUploadedFile("pre.png", PNG), save=True)

    def fetch_attachment(self, user=None):
        if user:
            self.client.force_login(user)
        return self.client.get(reverse("incidents:attachment_download", args=[self.attachment.pk]))

    def fetch_condition(self, user=None, kind="pre"):
        if user:
            self.client.force_login(user)
        return self.client.get(reverse("equipment:condition_image", args=[self.log.pk, kind]))

    # ---- incident evidence ----
    def test_anonymous_is_sent_to_login(self):
        r = self.fetch_attachment()
        self.assertEqual(r.status_code, 302)
        self.assertIn("login", r.url)

    def test_unrelated_student_is_forbidden(self):
        self.assertEqual(self.fetch_attachment(self.other).status_code, 403)

    def test_reporter_instructor_and_admin_can_download(self):
        for user in (self.owner, self.instructor, self.admin):
            r = self.fetch_attachment(user)
            self.assertEqual(r.status_code, 200, user.role)
            self.assertEqual(b"".join(r.streaming_content)[:4], PNG[:4])

    def test_safe_headers(self):
        r = self.fetch_attachment(self.owner)
        self.assertEqual(r["Content-Type"], "image/png")
        self.assertEqual(r["X-Content-Type-Options"], "nosniff")
        self.assertIn("private", r["Cache-Control"])

    def test_missing_file_on_disk_is_404(self):
        self.attachment.file.delete(save=False)
        self.assertEqual(self.fetch_attachment(self.owner).status_code, 404)

    # ---- equipment condition photos ----
    def test_condition_image_permissions(self):
        self.assertEqual(self.fetch_condition(self.other).status_code, 403)
        for user in (self.owner, self.instructor, self.admin):
            self.assertEqual(self.fetch_condition(user).status_code, 200, user.role)

    def test_condition_image_bad_kind_and_empty_field(self):
        self.assertEqual(self.fetch_condition(self.owner, kind="nope").status_code, 404)
        self.assertEqual(self.fetch_condition(self.owner, kind="post").status_code, 404)  # no post photo
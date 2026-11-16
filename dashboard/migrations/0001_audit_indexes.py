from django.db import migrations

INDEXES = [
    ("lt_visit_checkin_idx",  "access_logging_labvisit",         "(check_in_time)"),
    ("lt_visit_checkout_idx", "access_logging_labvisit",         "(check_out_time)"),
    ("lt_visit_lab_idx",      "access_logging_labvisit",         "(lab_location)"),
    ("lt_loan_borrowed_idx",  "equipment_equipmentlog",          "(borrowed_at)"),
    ("lt_loan_returned_idx",  "equipment_equipmentlog",          "(returned_at)"),
    ("lt_hist_changed_idx",   "incidents_incidentstatushistory", "(changed_at)"),
    ("lt_hist_status_idx",    "incidents_incidentstatushistory", "(to_status, changed_at)"),
]


class Migration(migrations.Migration):
    dependencies = [
        ("access_logging", "0001_initial"),
        ("equipment", "0001_initial"),
        ("incidents", "0001_initial"),
    ]
    operations = [
        migrations.RunSQL(
            sql=f"CREATE INDEX IF NOT EXISTS {name} ON {table} {cols};",
            reverse_sql=f"DROP INDEX IF EXISTS {name};",
        )
        for name, table, cols in INDEXES
    ]
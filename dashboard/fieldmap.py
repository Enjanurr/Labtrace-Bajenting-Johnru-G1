# access_logging.LabVisit
VISIT_USER = "user"
VISIT_LAB = "lab_location"
VISIT_IN = "check_in_time"
VISIT_OUT = "check_out_time"    # NULL while the visit is still active
VISIT_PURPOSE = "purpose"

# equipment.EquipmentLog
LOG_VISIT = "visit"
LOG_ASSET = "asset"
LOG_BORROWED = "borrowed_at"
LOG_RETURNED = "returned_at"    # NULL while the item is still out

# equipment.Asset
ASSET_NAME = "name"
ASSET_STATUS = "availability_status"

LOG_PRE = "pre_condition"
LOG_POST = "post_condition"
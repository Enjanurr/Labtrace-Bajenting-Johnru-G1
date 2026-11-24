# System Enhancement & Feature Suggestions

## 1. Room-Centric Architecture & Auto-Generated Asset Codes `[IMPLEMENTED]`
* **Status:** Implemented on `feature/enhanced-ui`.
* **What Was Built:**
  * Added the `Room` model (e.g., `Computer Lab 1`) and Admin room creation workflow.
  * Connected `Equipment` to `Room` and implemented auto-generated prefixed asset codes upon creation (e.g., selecting *Computer Lab 1* generates `CL1-001`, `CL1-002`, etc.).
  * Added room search/filtering on Student and Instructor equipment views.
* **Remaining Verification:**
  * Confirm `access_logging` (lab visits) and `incidents` also reference `Room` consistently where needed, and verify edge cases when creating multiple rooms with similar prefixes.

---

## 2. Borrowing Restrictions & Incident Redirection for Defective Equipment `[PENDING]`
* **Current Issue:** Equipment marked as `Damaged` or `Malfunctioning` can still be borrowed and returned normally without triggering any warning or workflow change.
* **Expected Behavior:**
  * Block checkout/borrowing for any equipment whose status is `Damaged`, `Malfunctioning`, `Missing`, or `Under Maintenance` (disable the borrow button in the UI and enforce validation in the backend view/form).
  * Automatically transition items flagged as `Damaged` or `Malfunctioning` to **Under Maintenance** (unavailable for borrowing) and prompt or redirect the user/admin to submit an **Incident Report** before the item can return to `Available` status.

---

## 3. Standardized Condition Dropdown Options (Borrow vs. Return) `[PENDING]`
* **Current Issue:** The condition dropdown on the borrowing form only includes `Good`, `Damaged`, and `Malfunctioning`, whereas the return form includes `Missing`.
* **Expected Behavior:**
  * Define a single shared `CONDITION_CHOICES` tuple in `equipment/models.py` (or a constants module) and reuse it across both borrowing/inspection and return forms so all options match:
    * `Good`
    * `Damaged`
    * `Malfunctioning`
    * `Missing`

---

## 4. Logout Guard for Active Lab Sessions & Unreturned Equipment `[PENDING]`
* **Expected Behavior:**
  * Intercept logout attempts for **Students** (and **Instructors** if applicable) when they still have:
    1. An **active (unchecked-out) lab visit session**, OR
    2. Any **unreturned borrowed equipment**.
  * Cancel the sign-out, redirect back to the dashboard, and display a clear warning banner listing the active session/unreturned items with direct links to check out or return equipment first.

---

## 5. Color-Coded Severity Badges on User Equipment & Incident Views `[PENDING]`
* **Expected Behavior:**
  * Render standardized Tailwind CSS severity badges across **Student** and **Instructor** equipment and incident views:
    * **Green:** `Good` / `Available`
    * **Yellow / Amber:** `Malfunctioning` / `Under Maintenance`
    * **Red:** `Damaged` / `Missing`

---

## 6. Role Selection During Registration & Role Management `[PENDING]`
* **Current Issue:** New users need a clear way to select their role during account creation without compromising system security.
* **Expected Behavior:**
  * **Self-Service Registration (`Student` vs. `Instructor`):**
    * Add a **Role** selector (`Student` or `Instructor`) on the user registration form.
    * Optionally require an **Instructor Verification / Invite Code** (or Admin approval flag `is_approved`) when a user selects `Instructor` so students cannot impersonate faculty.
  * **Security Guardrail for `Admin` Role:**
    * Exclude `Admin` from public self-registration—only existing Admins can promote a user to `Admin` via Django Admin or an in-app User Management panel.
  * **Post-Login Redirect:**
    * Automatically route the user to their respective role dashboard (`Student`, `Instructor`, or `Admin`) immediately after registration/login.
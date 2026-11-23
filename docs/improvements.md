# System Enhancement & Feature Suggestions

## 1. Room-Centric Architecture & Auto-Generated Asset Codes
* **Concept:** Treat the **Lab / Room** as the central entity connecting students, instructors, and equipment.
* **Admin Workflow:**
  * Add a **Room** model/type (e.g., `Computer Lab 1`).
  * When an Admin selects a room while adding a new asset, automatically generate a prefixed asset code based on the room (e.g., selecting *Computer Lab 1* generates `CL1-001`, `CL1-002`, etc.).
* **User Workflow (Student & Instructor):**
  * Provide a room filter/search selector so users can pick a specific lab/room and view only the equipment assigned to that room.

---

## 2. Borrowing Restrictions & Incident Redirection for Defective Equipment
* **Current Issue:** Equipment marked as `Damaged` or `Malfunctioning` can still be borrowed and returned normally without triggering any warning or workflow change.
* **Expected Behavior:**
  * Block borrowing for any equipment whose status is `Damaged`, `Malfunctioning`, `Missing`, or `Under Maintenance`.
  * Automatically flag defective items as **Under Maintenance** (or unavailable for checkout) and prompt/redirect the user or admin to file an **Incident Report** before the item can return to circulation.

---

## 3. Standardized Condition Dropdown Options (Borrow vs. Return)
* **Current Issue:** The condition dropdown on the borrowing form only includes `Good`, `Damaged`, and `Malfunctioning`, whereas the return form includes `Missing`.
* **Expected Behavior:**
  * Synchronize condition dropdown choices across both borrowing/inspection and return forms so all statuses match consistently:
    * `Good`
    * `Damaged`
    * `Malfunctioning`
    * `Missing`

---

## 4. Logout Guard for Active Lab Sessions & Unreturned Equipment
* **Expected Behavior:**
  * Prevent Students from logging out if they currently have:
    1. An **active (unchecked-out) lab visit session**, OR
    2. Any **unreturned borrowed equipment**.
  * Display a clear warning banner/toast listing the pending items/sessions and direct them to complete their equipment return or lab check-out before signing out.

---

## 5. Color-Coded Severity Badges on User Equipment & Incident Views
* **Expected Behavior:**
  * Display color-coded status badges on the **Student** and **Instructor** equipment/incident views to visually reflect condition severity:
    * **Green:** `Good` / `Available`
    * **Yellow / Amber:** `Malfunctioning` / `Under Maintenance`
    * **Red:** `Damaged` / `Missing`


    ## 6. User can choose their roles ???
* **Expected Behavior:**
  * Prevent Students from logging out if they currently have:
    1. An **active (unchecked-out) lab visit session**, OR
    2. Any **unreturned borrowed equipment**.
  * Display a clear warning banner/toast listing the pending items/sessions and direct them to complete their equipment return or lab check-out before signing out.

---
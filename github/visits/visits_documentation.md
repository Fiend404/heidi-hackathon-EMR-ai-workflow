OpenEMR Visits Category - Automation Documentation

Overview

The Visits module provides three reusable async functions for managing patient encounters in OpenEMR using Camoufox browser automation.

Files

    visits/
    ├── create_visit.py      # Create new encounters
    ├── current.py           # View active encounter
    ├── visit_history.py     # List all encounters
    └── visits_documentation.md


Prerequisites

    - Patient must be selected (via Finder)
    - For "Current": encounter must be selected from dropdown
    - OpenEMR demo: https://demo.openemr.io/openemr
    - Credentials: admin / pass


1. create_visit.py

Creates a new encounter/visit for a selected patient.

Usage:

    uv run python visits/create_visit.py --patient "Belford"
    uv run python visits/create_visit.py --patient "Belford" --reason "Routine checkup"

Arguments:

    --patient       Required. Patient name to search
    --category      Visit category
    --reason        Reason for visit
    --username      OpenEMR username (default: admin)
    --password      OpenEMR password (default: pass)
    --headless      Run browser headless
    --screenshot-dir Screenshot output directory

Programmatic Usage:

    from visits.create_visit import create_visit, VisitData

    visit_data = VisitData(
        visit_category="Office Visit",
        reason="Annual checkup"
    )

    result = await create_visit(
        patient_name="Belford",
        visit_data=visit_data
    )

    if result.success:
        print(f"Created: {result.message}")

Returns:

    CreateVisitResult:
        success: bool
        encounter_id: str (if available)
        message: str
        screenshot_path: str


2. current.py

Views the currently open encounter with SOAP notes and visit summary.

Usage:

    uv run python visits/current.py --patient "Belford"
    uv run python visits/current.py --patient "Belford" --encounter "2014-02-01"

Arguments:

    --patient       Required. Patient name to search
    --encounter     Specific encounter date (optional)
    --username      OpenEMR username (default: admin)
    --password      OpenEMR password (default: pass)
    --headless      Run browser headless
    --screenshot-dir Screenshot output directory

Programmatic Usage:

    from visits.current import get_current_visit

    result = await get_current_visit(
        patient_name="Belford",
        encounter_date="2014-02-01"
    )

    if result.success:
        print(f"SOAP: {result.soap_notes}")
        print(f"Summary: {result.visit_summary}")

Returns:

    CurrentVisitResult:
        success: bool
        encounter_date: str
        visit_summary: dict
            - provider: str
            - patientType: str
            - reason: str
        soap_notes: dict
            - subjective: str
            - objective: str
            - assessment: str
            - plan: str
        message: str
        screenshot_path: str

Example Output:

    Encounter: 2014-02-01
    Visit Summary: {'provider': 'Billy Smith', 'patientType': 'Established Patient'}
    SOAP Notes: {'subjective': 'sad', 'objective': 'crying', 'assessment': 'depression', 'plan': 'psych eval'}


3. visit_history.py

Retrieves complete visit history for a patient.

Usage:

    uv run python visits/visit_history.py --patient "Belford"
    uv run python visits/visit_history.py --patient "Belford" --output visits.json

Arguments:

    --patient       Required. Patient name to search
    --username      OpenEMR username (default: admin)
    --password      OpenEMR password (default: pass)
    --headless      Run browser headless
    --screenshot-dir Screenshot output directory
    --output        JSON file to save results

Programmatic Usage:

    from visits.visit_history import get_visit_history

    result = await get_visit_history(patient_name="Belford")

    if result.success:
        for visit in result.visits:
            print(f"{visit.date}: {visit.provider} - {visit.reason_form}")

Returns:

    VisitHistoryResult:
        success: bool
        patient_name: str
        total_visits: int
        visits: List[VisitRecord]
            - date: str
            - issue: str
            - reason_form: str
            - provider: str
            - billing: str
        message: str
        screenshot_path: str

JSON Output Example:

    {
      "patient": "Belford",
      "total_visits": 5,
      "visits": [
        {
          "date": "2025-11-28",
          "issue": "",
          "reason_form": "Document: CCDA_Belford_Phil_2025-11-28.xml-60 (CCDA)",
          "provider": "",
          "billing": ""
        },
        {
          "date": "2014-02-01",
          "issue": "",
          "reason_form": "Sad\nVitalsSOAP",
          "provider": "Smith, Billy",
          "billing": "CPT4 - 99202ICD9 - 296.20"
        }
      ]
    }


Common Patterns

Selecting a Patient:

    await page.click('text=Finder')
    await asyncio.sleep(5)

    for frame in page.frames:
        link = await frame.query_selector(f'a:has-text("{patient_name}")')
        if link:
            await link.click()
            break

Selecting an Encounter:

    enc_btn = await page.query_selector('button:has-text("Select Encounter")')
    await enc_btn.click()
    await asyncio.sleep(1)

    options = await page.query_selector_all('.dropdown-item')
    await options[0].click()

Navigating Visits Submenu:

    await page.click('text=Patient')
    await asyncio.sleep(0.5)

    visits_pos = await page.evaluate("""
        () => {
            const el = Array.from(document.querySelectorAll('.menuLabel'))
                .find(e => e.textContent.trim() === 'Visits');
            if (el) {
                const r = el.getBoundingClientRect();
                return {x: r.x + r.width/2, y: r.y + r.height/2};
            }
            return null;
        }
    """)

    await page.mouse.move(visits_pos['x'], visits_pos['y'])
    await asyncio.sleep(0.5)


CSS Selectors Reference

    Menu Items:
        .menuLabel                     # All menu labels
        .menuLabel.menuDisabled        # Disabled items
        .menuLabel.dropdown-toggle     # Dropdown parents

    Patient Header:
        button:has-text("Select Encounter")  # Encounter dropdown

    Forms (in frames):
        #save-form, input[name="form_save"]  # Save button
        select[name*="category"]              # Visit category
        textarea[name*="reason"]              # Reason field

    Visit History Table:
        table th:has-text("Date")            # Identify correct table
        tbody tr td                          # Table cells


Error Handling

All functions return a result object with:
    - success: boolean indicating operation result
    - message: human-readable status/error message

Common errors:
    - "Login failed" - Invalid credentials
    - "Patient not found" - No matching patient in Finder
    - "Current menu item not available" - No encounter selected
    - "Visit History menu item not available" - No patient selected


Screenshots

All functions support screenshot capture:

    result = await get_visit_history(
        patient_name="Belford",
        screenshot_dir="visits_screenshots"
    )

    print(result.screenshot_path)  # visits_screenshots/visit_history.png

Profile Management Module

Target URL: https://demo.openemr.io/openemr/
Credentials: admin / pass
Navigation: Admin > Address Book

Module Overview

This module provides automation functions for managing contacts in the OpenEMR Address Book. It supports adding individual entries and bulk importing from external data files.

Shared Helpers

async def login(page, username="admin", password="pass") -> bool

Logs into OpenEMR and returns success status.
- page: Playwright page object
- username: Login username (default: "admin")
- password: Login password (default: "pass")
- Returns: True if login successful, False otherwise

async def navigate_to(page, menu_path: list, timeout=15000) -> bool

Navigates through OpenEMR menu items using JavaScript clicks.
- page: Playwright page object
- menu_path: List of menu items, e.g. ["Admin", "Address Book"]
- timeout: Wait timeout in milliseconds
- Returns: True if navigation successful

async def find_content_frame(page, keyword: str) -> Frame

Finds an iframe containing the keyword in its URL.
- page: Playwright page object
- keyword: String to match in frame URL (e.g. "addrbook_list")
- Returns: Frame object or None

async def fill_form(frame, field_data: dict, selectors: dict = None)

Fills form fields in an iframe using frame.fill() method.
- frame: Playwright frame object
- field_data: Dict of field_name -> value
- selectors: Optional custom selectors dict

def map_profile_to_address(profile: dict) -> dict

Maps external profile data to Address Book form fields.
- profile: Dict with external profile fields
- Returns: Dict with Address Book form field names

Field Mapping:
- first_name -> form_fname
- last_name -> form_lname
- phone -> form_phonecell (normalized)
- email -> form_email
- gender -> form_title (male=Mr., female=Ms.)
- additional_context + medications + allergies + history -> form_notes

AddAddressEntry Class

Creates a new entry in the OpenEMR Address Book.

class AddAddressEntry:
    def __init__(self, page, frame=None)
    async def execute(self, data: dict) -> dict

execute() Parameters

- form_abook_type: Entry type (oth, spe, vendor, ord_lab, etc.)
- form_title: Title (Mr., Mrs., Ms., Dr.)
- form_fname: First name
- form_lname: Last name
- form_mname: Middle name (optional)
- form_suffix: Suffix (optional)
- form_specialty: Specialty or role
- form_organization: Organization name
- form_phone: Home phone
- form_phonecell: Mobile phone
- form_phonew1: Work phone
- form_fax: Fax number
- form_email: Email address
- form_email_direct: Trusted email (for Direct messaging)
- form_street: Address line 1
- form_streetb: Address line 2
- form_city: City
- form_state: State code (CA, NY, TX, etc.)
- form_zip: Postal code
- form_notes: Notes/comments

Returns

{
    "success": true,
    "message": "Added entry: John Doe",
    "data": { ... submitted form data ... }
}

Usage Example

from profile_management import login, navigate_to
from profile_management.add_address_entry import AddAddressEntry

async with AsyncCamoufox(headless=False) as browser:
    page = await browser.new_page()

    await login(page)
    await navigate_to(page, ["Admin", "Address Book"])

    op = AddAddressEntry(page)
    result = await op.execute({
        "form_abook_type": "oth",
        "form_title": "Mr.",
        "form_fname": "John",
        "form_lname": "Doe",
        "form_email": "john@example.com",
        "form_phonecell": "555-123-4567"
    })

ImportProfiles Class

Bulk imports profiles from external data to Address Book.

class ImportProfiles:
    def __init__(self, page)
    async def import_single(self, data: dict) -> dict
    async def import_all(self, profiles: list) -> dict

import_all() Parameters

- profiles: List of raw profile dicts (mapped internally using map_profile_to_address)

Returns

{
    "total": 3,
    "success": 3,
    "failed": 0,
    "details": [
        {"profile_id": "hp_001", "name": "John Doe", "result": {...}},
        ...
    ]
}

Usage Example

from profile_management import login, navigate_to
from profile_management.import_profiles import ImportProfiles
import json

with open("sample-profile-data.json") as f:
    profiles = json.load(f)

async with AsyncCamoufox(headless=False) as browser:
    page = await browser.new_page()

    await login(page)
    await navigate_to(page, ["Admin", "Address Book"])

    importer = ImportProfiles(page)
    results = await importer.import_all(profiles)

    print(f"Imported {results['success']}/{results['total']}")

Standalone Run Commands

Test add single entry:
uv run python -m profile_management.add_address_entry

Run bulk import:
uv run python -m profile_management.import_profiles

External Data Format

Expected format for sample-profile-data.json:

[
  {
    "id": "hp_001",
    "first_name": "John",
    "last_name": "Doe",
    "gender": "male",
    "birth_date": "1990-01-15",
    "phone": "+61 400 111 111",
    "email": "john.doe@example.com",
    "additional_context": "Works in construction",
    "current_medications": "Ventolin PRN",
    "allergies": "Penicillin",
    "past_medical_history": "Asthma"
  }
]

Files Structure

profile_management/
  __init__.py          - Shared helpers and data mapping
  add_address_entry.py - Single entry creation
  import_profiles.py   - Bulk import functionality
  selectors.json       - Form field selectors
  operations.json      - Operation definitions
  data_mapping_plan.json - Field mapping documentation
  documentation.md     - This file
  html/                - Captured HTML pages
  screenshot/          - Captured screenshots

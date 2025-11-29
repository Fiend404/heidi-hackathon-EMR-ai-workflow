Profile Management Module

Target URL: https://demo.openemr.io/openemr
Credentials: admin / pass

This module provides automation for the OpenEMR Address Book (Admin > Address Book).


Shared Helpers (profile_management/__init__.py)

    async def login(page, username="admin", password="pass") -> bool
    Logs into OpenEMR and returns success status.
    - page: Playwright page object
    - username: Login username (default: "admin")
    - password: Login password (default: "pass")
    - Returns: True if login successful, False otherwise

    async def navigate_to(page, menu_path: list, timeout=15000) -> bool
    Navigate through menu items to reach a page.
    - page: Playwright page object
    - menu_path: List of menu item texts (e.g., ["Admin", "Address Book"])
    - timeout: Timeout for each click in ms
    - Returns: True if navigation successful

    async def find_content_frame(page, keyword) -> Frame or None
    Find iframe containing keyword in URL.
    - page: Playwright page object
    - keyword: Keyword to search for in frame URLs (e.g., "addrbook")
    - Returns: Frame object or None

    async def fill_form(frame, field_data: dict, use_fill=True) -> dict
    Fill form fields using frame.fill() method.
    - frame: Playwright frame object
    - field_data: Dict mapping field names to values
    - Returns: {"filled": [...], "errors": [...]}

    async def extract_table_data(frame, table_selector="table") -> list
    Extract table rows as list of dicts.
    - frame: Playwright frame object
    - table_selector: CSS selector for table
    - Returns: List of dicts with table data

    def map_profile_to_address(profile: dict) -> dict
    Map external profile data to address book form fields.
    - profile: Dict from sample-profile-data.json
    - Returns: Form field data ready for fill_form()


AddContact Class (profile_management/add_contact.py)

    class AddContact:
        def __init__(self, page, frame=None)
        - page: Playwright page object
        - frame: Optional frame (will find automatically)

        async def execute(self, data: dict) -> dict
        Add a new contact to the address book.

        Parameters (data dict):
        - form_abook_type (optional): Contact type. Valid values:
            - "oth" (Other)
            - "spe" (Specialist)
            - "vendor" (Vendor)
            - "ord_lab" (Lab Service)
            - "ord_img" (Imaging Service)
            - "ord_imm" (Immunization Service)
        - form_fname (required): First name
        - form_lname (required): Last name
        - form_mname (optional): Middle name
        - form_phonecell (optional): Mobile phone
        - form_phone (optional): Home phone
        - form_phonew1 (optional): Work phone
        - form_email (optional): Email address
        - form_specialty (optional): Specialty
        - form_organization (optional): Organization
        - form_notes (optional): Notes textarea
        - form_street (optional): Street address line 1
        - form_city (optional): City
        - form_state (optional): State code
        - form_zip (optional): Postal code

        Returns:
        {
            "success": bool,
            "message": str,
            "data": {
                "name": "First Last",
                "fields_filled": [...]
            }
        }

    Usage Example:

        from profile_management.add_contact import AddContact
        from profile_management import login, navigate_to

        async with AsyncCamoufox(headless=False) as browser:
            ctx = await browser.new_context()
            page = await ctx.new_page()
            page.set_default_timeout(30000)

            await login(page)
            await navigate_to(page, ["Admin", "Address Book"])

            op = AddContact(page)
            result = await op.execute({
                "form_abook_type": "oth",
                "form_fname": "John",
                "form_lname": "Doe",
                "form_email": "john@example.com",
                "form_phonecell": "0400111111"
            })

            print(result)


SearchContacts Class (profile_management/search_contacts.py)

    class SearchContacts:
        def __init__(self, page, frame=None)
        - page: Playwright page object
        - frame: Optional frame (will find automatically)

        async def execute(self, search_params: dict = None) -> dict
        Search for contacts in the address book.

        Parameters (search_params dict):
        - form_organization (optional): Organization filter
        - form_fname (optional): First name filter
        - form_lname (optional): Last name filter
        - form_specialty (optional): Specialty filter
        - form_npi (optional): NPI filter
        - form_abook_type (optional): Type filter
        - form_external (optional): External only checkbox (bool)

        Returns:
        {
            "success": bool,
            "message": "Found X contacts",
            "data": {
                "count": int,
                "contacts": [
                    {"Organization": "", "Name": "", "Email": "", ...},
                    ...
                ]
            }
        }

    Usage Example:

        from profile_management.search_contacts import SearchContacts
        from profile_management import login, navigate_to

        async with AsyncCamoufox(headless=False) as browser:
            ctx = await browser.new_context()
            page = await ctx.new_page()
            page.set_default_timeout(30000)

            await login(page)
            await navigate_to(page, ["Admin", "Address Book"])

            op = SearchContacts(page)

            # Search all
            result = await op.execute()
            print(f"Total contacts: {result['data']['count']}")

            # Search by name
            result = await op.execute({"form_lname": "Doe"})
            for contact in result['data']['contacts']:
                print(f"  - {contact['Name']}")


Complete End-to-End Example

    import asyncio
    import json
    from pathlib import Path
    from camoufox.async_api import AsyncCamoufox

    from profile_management import login, navigate_to, map_profile_to_address
    from profile_management.add_contact import AddContact
    from profile_management.search_contacts import SearchContacts

    async def main():
        # Load external profiles
        with open("sample-profile-data.json") as f:
            profiles = json.load(f)

        async with AsyncCamoufox(headless=False, humanize=0.5) as browser:
            ctx = await browser.new_context()
            page = await ctx.new_page()
            page.set_default_timeout(30000)

            # Login
            await login(page)

            # Navigate to Address Book
            await navigate_to(page, ["Admin", "Address Book"])

            # Add each profile
            add_op = AddContact(page)
            for profile in profiles:
                data = map_profile_to_address(profile)
                result = await add_op.execute(data)
                print(f"Added {profile['first_name']} {profile['last_name']}: {result['success']}")

            # Search to verify
            search_op = SearchContacts(page)
            result = await search_op.execute()
            print(f"\nTotal contacts: {result['data']['count']}")

            await ctx.close()

    asyncio.run(main())


Standalone Run Commands

    # Test add contact (uses sample-profile-data.json)
    uv run python profile_management/add_contact.py

    # Test search contacts
    uv run python profile_management/search_contacts.py

    # Run bulk import
    uv run python profile_management/import_profiles.py


Data Mapping

External profile fields map to EMR fields as follows:

    first_name    -> form_fname
    last_name     -> form_lname
    phone         -> form_phonecell (formatted as 04XXXXXXXX)
    email         -> form_email

Combined into form_notes:
    - additional_context
    - current_medications (prefixed "Medications: ")
    - allergies (prefixed "Allergies: ")
    - past_medical_history (prefixed "PMH: ")

Default values:
    form_abook_type = "oth" (Other)
    form_specialty = "Patient Contact"

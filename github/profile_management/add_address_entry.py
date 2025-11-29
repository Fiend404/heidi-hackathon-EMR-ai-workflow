"""
Profile Management - Add Address Entry
Auto-generated from EMR analysis

Creates a new entry in the OpenEMR Address Book
"""
import asyncio
import json
from pathlib import Path
from camoufox.async_api import AsyncCamoufox

BASE_DIR = Path(__file__).parent
SELECTORS = json.loads((BASE_DIR / "selectors.json").read_text())
OPERATIONS = json.loads((BASE_DIR / "operations.json").read_text())

from . import (
    login,
    navigate_to,
    find_content_frame,
    fill_form,
    map_profile_to_address
)


class AddAddressEntry:
    """Add a new entry to the Address Book"""

    def __init__(self, page, frame=None):
        self.page = page
        self.frame = frame
        self.operation = next(
            o for o in OPERATIONS["operations"] if o["name"] == "add_address_entry"
        )

    async def execute(self, data: dict) -> dict:
        """
        Execute add_address_entry operation

        Args:
            data: Dict containing form fields:
                - form_abook_type: Type of entry (oth, spe, vendor, etc.)
                - form_title: Title (Mr., Mrs., Ms., Dr.)
                - form_fname: First name
                - form_lname: Last name
                - form_mname: Middle name (optional)
                - form_suffix: Suffix (optional)
                - form_specialty: Specialty
                - form_organization: Organization name
                - form_phone: Home phone
                - form_phonecell: Mobile phone
                - form_phonew1: Work phone
                - form_fax: Fax number
                - form_email: Email address
                - form_email_direct: Trusted email
                - form_street: Address line 1
                - form_streetb: Address line 2
                - form_city: City
                - form_state: State code (CA, NY, etc.)
                - form_zip: Postal code
                - form_notes: Notes/comments

        Returns:
            dict with success status and result data
        """
        try:
            # 1. Find the address book list frame
            list_frame = await find_content_frame(self.page, "addrbook_list")
            if not list_frame:
                return {"success": False, "message": "Address book list frame not found", "data": None}

            # 2. Click Add New button
            add_btn = await list_frame.query_selector("input[value='Add New']")
            if not add_btn:
                return {"success": False, "message": "Add New button not found", "data": None}

            await add_btn.click()
            await asyncio.sleep(2)

            # 3. Find the add form frame
            add_frame = await find_content_frame(self.page, "addrbook_edit")
            if not add_frame:
                return {"success": False, "message": "Add form frame not found", "data": None}

            # 4. Fill the form
            await fill_form(add_frame, data)
            await asyncio.sleep(0.5)

            # 5. Submit the form
            save_btn = await add_frame.query_selector("input[name='form_save']")
            if not save_btn:
                return {"success": False, "message": "Save button not found", "data": None}

            await save_btn.click()
            await asyncio.sleep(2)

            # 6. Check for success - should return to list page
            # Refresh frame reference
            list_frame = await find_content_frame(self.page, "addrbook_list")
            if list_frame:
                # Verify entry exists in list
                name_check = f"{data.get('form_lname', '')}"
                content = await list_frame.content()
                if name_check and name_check in content:
                    return {
                        "success": True,
                        "message": f"Added entry: {data.get('form_fname', '')} {data.get('form_lname', '')}",
                        "data": data
                    }

            # Check for error in add frame
            add_frame = await find_content_frame(self.page, "addrbook_edit")
            if add_frame:
                error_el = await add_frame.query_selector(".error-message, .alert-danger")
                if error_el:
                    error_text = await error_el.text_content()
                    return {"success": False, "message": f"Form error: {error_text}", "data": None}

            return {
                "success": True,
                "message": f"Entry likely added: {data.get('form_fname', '')} {data.get('form_lname', '')}",
                "data": data
            }

        except Exception as e:
            return {"success": False, "message": str(e), "data": None}


async def main():
    """Test execution with external data"""
    # Load external data for validation
    external_file = BASE_DIR.parent / "sample-profile-data.json"

    if external_file.exists():
        with open(external_file) as f:
            external_data = json.load(f)

        # Use first record for testing
        sample = external_data[0]

        # Map external fields to function parameters
        test_data = map_profile_to_address(sample)

        print(f"Testing with external data: {sample.get('first_name')} {sample.get('last_name')}")
        print(f"Mapped data: {json.dumps(test_data, indent=2)}")
    else:
        # Fallback to generated test data
        import time
        suffix = int(time.time()) % 10000
        test_data = {
            "form_abook_type": "oth",
            "form_title": "Mr.",
            "form_fname": f"Test{suffix}",
            "form_lname": f"User{suffix}",
            "form_phonecell": "555-123-4567",
            "form_email": f"test{suffix}@example.com",
            "form_specialty": "Test Contact",
            "form_notes": "Auto-generated test entry"
        }
        print("Testing with generated data")

    async with AsyncCamoufox(headless=False, humanize=0.5) as browser:
        ctx = await browser.new_context()
        page = await ctx.new_page()
        page.set_default_timeout(30000)

        # Login
        print("\n[1] Logging in...")
        success = await login(page)
        if not success:
            print("    Login failed!")
            await ctx.close()
            return

        print("    Login successful")

        # Navigate to Address Book
        print("\n[2] Navigating to Address Book...")
        success = await navigate_to(page, ["Admin", "Address Book"])
        if not success:
            print("    Navigation failed!")
            await ctx.close()
            return

        print("    Navigation successful")

        # Execute operation
        print("\n[3] Adding address entry...")
        op = AddAddressEntry(page, None)
        result = await op.execute(test_data)

        # Print result
        print("\n[4] Result:")
        print(json.dumps(result, indent=2))

        await asyncio.sleep(3)
        await ctx.close()


if __name__ == "__main__":
    asyncio.run(main())

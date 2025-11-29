"""
Profile Management - Bulk Import Profiles
Auto-generated from EMR analysis

Imports multiple profiles from external data file to OpenEMR Address Book
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


class ImportProfiles:
    """Bulk import profiles to Address Book"""

    def __init__(self, page):
        self.page = page

    async def import_single(self, data: dict) -> dict:
        """
        Import a single profile to Address Book

        Args:
            data: Mapped profile data for Address Book form

        Returns:
            dict with success status and result
        """
        try:
            # Find list frame
            list_frame = await find_content_frame(self.page, "addrbook_list")
            if not list_frame:
                return {"success": False, "message": "List frame not found", "data": None}

            # Click Add New
            add_btn = await list_frame.query_selector("input[value='Add New']")
            if not add_btn:
                return {"success": False, "message": "Add button not found", "data": None}

            await add_btn.click()
            await asyncio.sleep(2)

            # Find add form frame
            add_frame = await find_content_frame(self.page, "addrbook_edit")
            if not add_frame:
                return {"success": False, "message": "Add form not found", "data": None}

            # Fill form
            await fill_form(add_frame, data)
            await asyncio.sleep(0.5)

            # Submit
            save_btn = await add_frame.query_selector("input[name='form_save']")
            if save_btn:
                await save_btn.click()
                await asyncio.sleep(2)

            return {
                "success": True,
                "message": f"Added: {data.get('form_fname', '')} {data.get('form_lname', '')}",
                "data": data
            }

        except Exception as e:
            return {"success": False, "message": str(e), "data": None}

    async def import_all(self, profiles: list) -> dict:
        """
        Import all profiles from list

        Args:
            profiles: List of raw profile dicts (will be mapped internally)

        Returns:
            dict with success count, failure count, and details
        """
        results = {
            "total": len(profiles),
            "success": 0,
            "failed": 0,
            "details": []
        }

        for i, profile in enumerate(profiles):
            print(f"  [{i+1}/{len(profiles)}] Importing {profile.get('first_name', '')} {profile.get('last_name', '')}...")

            # Map profile to Address Book format
            mapped_data = map_profile_to_address(profile)

            # Import
            result = await self.import_single(mapped_data)

            if result["success"]:
                results["success"] += 1
                print(f"    SUCCESS")
            else:
                results["failed"] += 1
                print(f"    FAILED: {result['message']}")

            results["details"].append({
                "profile_id": profile.get("id", f"row_{i}"),
                "name": f"{profile.get('first_name', '')} {profile.get('last_name', '')}",
                "result": result
            })

            # Small delay between imports
            await asyncio.sleep(1)

        return results


async def main():
    """Run bulk import with sample data"""
    # Load external data
    external_file = BASE_DIR.parent / "sample-profile-data.json"

    if not external_file.exists():
        print(f"ERROR: External data file not found: {external_file}")
        return

    with open(external_file) as f:
        profiles = json.load(f)

    print(f"Loaded {len(profiles)} profiles from {external_file}")

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

        # Bulk import
        print("\n[3] Starting bulk import...")
        importer = ImportProfiles(page)
        results = await importer.import_all(profiles)

        # Print summary
        print("\n" + "=" * 70)
        print("IMPORT SUMMARY")
        print("=" * 70)
        print(f"  Total: {results['total']}")
        print(f"  Success: {results['success']}")
        print(f"  Failed: {results['failed']}")
        print("=" * 70)

        await asyncio.sleep(3)
        await ctx.close()


if __name__ == "__main__":
    asyncio.run(main())

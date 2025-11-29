#!/usr/bin/env python3
"""
OpenEMR Create Visit - Reusable Camoufox Automation

Creates a new encounter/visit for a selected patient.

Usage:
    uv run python visits/create_visit.py --patient "Belford" --category "Office Visit"
    uv run python visits/create_visit.py --patient "Belford"  # Uses defaults
"""

import asyncio
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from camoufox.async_api import AsyncCamoufox


@dataclass
class VisitData:
    """Data structure for new visit/encounter"""
    visit_category: str = ""
    visit_class: str = "Outpatient"
    visit_type: str = ""
    sensitivity: str = "normal"
    facility: str = ""
    reason: str = ""


@dataclass
class CreateVisitResult:
    """Result of create visit operation"""
    success: bool
    encounter_id: Optional[str] = None
    message: str = ""
    screenshot_path: Optional[str] = None


class OpenEMRSession:
    """Manages OpenEMR browser session"""

    def __init__(self, base_url: str = "https://demo.openemr.io/openemr"):
        self.base_url = base_url
        self.login_url = f"{base_url}/interface/login/login.php?site=default"
        self.browser = None
        self.page = None

    async def login(self, username: str = "admin", password: str = "pass") -> bool:
        """Login to OpenEMR"""
        await self.page.goto(self.login_url)
        await asyncio.sleep(2)
        await self.page.fill('#authUser', username)
        await asyncio.sleep(0.3)
        await self.page.fill('#clearPass', password)
        await asyncio.sleep(0.3)
        await self.page.click('#login-button')
        await asyncio.sleep(4)
        return 'login' not in self.page.url.lower()

    async def select_patient(self, patient_name: str) -> bool:
        """Select a patient via Finder"""
        await self.page.click('text=Finder')
        await asyncio.sleep(5)

        # Wait for finder to load, retry checking frames
        for attempt in range(3):
            for frame in self.page.frames:
                try:
                    link = await frame.query_selector(f'a:has-text("{patient_name}")')
                    if link:
                        await link.click()
                        await asyncio.sleep(4)
                        return True
                except:
                    pass
            await asyncio.sleep(2)

        return False

    async def navigate_to_menu(self, *menu_path: str) -> bool:
        """Navigate through menu hierarchy"""
        for i, item in enumerate(menu_path):
            if i == 0:
                await self.page.click(f'text={item}')
                await asyncio.sleep(0.5)
            else:
                # Hover and click for submenus
                pos = await self.page.evaluate(f"""
                    () => {{
                        const el = Array.from(document.querySelectorAll('.menuLabel'))
                            .find(e => e.textContent.trim() === '{item}');
                        if (el) {{
                            const r = el.getBoundingClientRect();
                            return {{x: r.x + r.width/2, y: r.y + r.height/2, disabled: el.classList.contains('menuDisabled')}};
                        }}
                        return null;
                    }}
                """)
                if pos and not pos.get('disabled'):
                    await self.page.mouse.move(pos['x'], pos['y'])
                    await asyncio.sleep(0.5)
                    await self.page.mouse.click(pos['x'], pos['y'])
                    await asyncio.sleep(2)
                else:
                    return False
        return True


async def create_visit(
    patient_name: str,
    visit_data: Optional[VisitData] = None,
    username: str = "admin",
    password: str = "pass",
    headless: bool = False,
    screenshot_dir: Optional[Path] = None
) -> CreateVisitResult:
    """
    Create a new visit/encounter for a patient.

    Args:
        patient_name: Name or partial name to search for patient
        visit_data: Optional VisitData with encounter details
        username: OpenEMR username
        password: OpenEMR password
        headless: Run browser in headless mode
        screenshot_dir: Directory to save screenshots

    Returns:
        CreateVisitResult with success status and details
    """
    if visit_data is None:
        visit_data = VisitData()

    result = CreateVisitResult(success=False)

    async with AsyncCamoufox(headless=headless) as browser:
        page = await browser.new_page()
        page.set_default_timeout(10000)

        session = OpenEMRSession()
        session.page = page

        # Login
        print(f"[1] Logging in...")
        if not await session.login(username, password):
            result.message = "Login failed"
            return result

        # Select patient
        print(f"[2] Selecting patient: {patient_name}")
        if not await session.select_patient(patient_name):
            result.message = f"Patient '{patient_name}' not found"
            return result

        # Navigate to Create Visit
        print(f"[3] Opening Create Visit form...")
        await page.click('text=Patient')
        await asyncio.sleep(0.5)

        # Hover on Visits submenu
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

        if visits_pos:
            await page.mouse.move(visits_pos['x'], visits_pos['y'])
            await asyncio.sleep(0.5)

        # Click Create Visit
        create_pos = await page.evaluate("""
            () => {
                const el = Array.from(document.querySelectorAll('.menuLabel'))
                    .find(e => e.textContent.trim() === 'Create Visit');
                if (el && !el.classList.contains('menuDisabled')) {
                    const r = el.getBoundingClientRect();
                    return {x: r.x + r.width/2, y: r.y + r.height/2};
                }
                return null;
            }
        """)

        if not create_pos:
            result.message = "Create Visit menu item not available"
            return result

        await page.mouse.click(create_pos['x'], create_pos['y'])
        await asyncio.sleep(4)

        # Wait for form to load in iframe
        print(f"[4] Waiting for encounter form to load...")
        await asyncio.sleep(2)

        # Find and fill form in iframe
        form_found = False
        for frame in page.frames:
            try:
                # Look for the encounter form by checking for specific fields
                save_btn = await frame.query_selector('#save-form, button:has-text("Save"), input[name="form_save"]')
                if not save_btn:
                    continue

                form_found = True
                print(f"[5] Found encounter form, filling fields...")

                # Fill visit category if provided
                if visit_data.visit_category:
                    cat_select = await frame.query_selector('select[name*="category"], #pc_catid')
                    if cat_select:
                        await cat_select.select_option(label=visit_data.visit_category)
                        await asyncio.sleep(0.3)

                # Fill reason if provided
                if visit_data.reason:
                    reason_input = await frame.query_selector('textarea[name*="reason"], #reason')
                    if reason_input:
                        await reason_input.fill(visit_data.reason)
                        await asyncio.sleep(0.3)

                # Click Save
                print(f"[6] Saving encounter...")
                await save_btn.click()
                await asyncio.sleep(4)

                result.success = True
                result.message = "Encounter created successfully"
                break

            except Exception as e:
                print(f"    Frame error: {str(e)[:50]}")
                continue

        if not form_found:
            result.message = "Encounter form not found in any frame"

        # Take screenshot if directory provided
        if screenshot_dir:
            screenshot_dir = Path(screenshot_dir)
            screenshot_dir.mkdir(exist_ok=True)
            screenshot_path = screenshot_dir / "create_visit_result.png"
            await page.screenshot(path=str(screenshot_path))
            result.screenshot_path = str(screenshot_path)
            print(f"[6] Screenshot saved: {screenshot_path}")

        return result


async def main():
    parser = argparse.ArgumentParser(description="Create a new visit/encounter in OpenEMR")
    parser.add_argument("--patient", required=True, help="Patient name to search for")
    parser.add_argument("--category", default="", help="Visit category")
    parser.add_argument("--reason", default="", help="Reason for visit")
    parser.add_argument("--username", default="admin", help="OpenEMR username")
    parser.add_argument("--password", default="pass", help="OpenEMR password")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--screenshot-dir", default="visits_screenshots", help="Screenshot directory")

    args = parser.parse_args()

    visit_data = VisitData(
        visit_category=args.category,
        reason=args.reason
    )

    print("="*60)
    print("CREATE VISIT - OpenEMR Automation")
    print("="*60)

    result = await create_visit(
        patient_name=args.patient,
        visit_data=visit_data,
        username=args.username,
        password=args.password,
        headless=args.headless,
        screenshot_dir=args.screenshot_dir
    )

    print("\n" + "="*60)
    print(f"Result: {'SUCCESS' if result.success else 'FAILED'}")
    print(f"Message: {result.message}")
    if result.screenshot_path:
        print(f"Screenshot: {result.screenshot_path}")
    print("="*60)

    return result


if __name__ == "__main__":
    asyncio.run(main())

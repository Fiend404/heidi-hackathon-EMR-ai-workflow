#!/usr/bin/env python3
"""
OpenEMR Visit History - Reusable Camoufox Automation

Retrieves the visit history for a selected patient.

Usage:
    uv run python visits/visit_history.py --patient "Belford"
    uv run python visits/visit_history.py --patient "Belford" --output visits.json
"""

import asyncio
import argparse
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, List
from camoufox.async_api import AsyncCamoufox


@dataclass
class VisitRecord:
    """A single visit record from history"""
    date: str
    issue: str = ""
    reason_form: str = ""
    provider: str = ""
    billing: str = ""


@dataclass
class VisitHistoryResult:
    """Result of visit history operation"""
    success: bool
    patient_name: str = ""
    total_visits: int = 0
    visits: List[VisitRecord] = None
    message: str = ""
    screenshot_path: Optional[str] = None

    def __post_init__(self):
        if self.visits is None:
            self.visits = []


async def get_visit_history(
    patient_name: str,
    username: str = "admin",
    password: str = "pass",
    headless: bool = False,
    screenshot_dir: Optional[Path] = None
) -> VisitHistoryResult:
    """
    Get visit history for a patient.

    Args:
        patient_name: Name or partial name to search for patient
        username: OpenEMR username
        password: OpenEMR password
        headless: Run browser in headless mode
        screenshot_dir: Directory to save screenshots

    Returns:
        VisitHistoryResult with list of visits
    """
    result = VisitHistoryResult(success=False, patient_name=patient_name)

    async with AsyncCamoufox(headless=headless) as browser:
        page = await browser.new_page()
        page.set_default_timeout(10000)

        # Login
        print(f"[1] Logging in...")
        await page.goto("https://demo.openemr.io/openemr/interface/login/login.php?site=default")
        await asyncio.sleep(2)
        await page.fill('#authUser', username)
        await page.fill('#clearPass', password)
        await page.click('#login-button')
        await asyncio.sleep(4)

        if 'login' in page.url.lower():
            result.message = "Login failed"
            return result

        # Select patient via Finder
        print(f"[2] Selecting patient: {patient_name}")
        await page.click('text=Finder')
        await asyncio.sleep(5)

        patient_found = False
        for attempt in range(3):
            for frame in page.frames:
                try:
                    link = await frame.query_selector(f'a:has-text("{patient_name}")')
                    if link:
                        await link.click()
                        await asyncio.sleep(4)
                        patient_found = True
                        break
                except:
                    pass
            if patient_found:
                break
            await asyncio.sleep(2)

        if not patient_found:
            result.message = f"Patient '{patient_name}' not found"
            return result

        # Navigate to Visit History
        print(f"[3] Opening Visit History...")
        await page.click('text=Patient')
        await asyncio.sleep(0.5)

        # Hover on Visits
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

        # Click Visit History
        vh_pos = await page.evaluate("""
            () => {
                const el = Array.from(document.querySelectorAll('.menuLabel'))
                    .find(e => e.textContent.trim() === 'Visit History');
                if (el && !el.classList.contains('menuDisabled')) {
                    const r = el.getBoundingClientRect();
                    return {x: r.x + r.width/2, y: r.y + r.height/2};
                }
                return null;
            }
        """)

        if not vh_pos:
            result.message = "Visit History menu item not available"
            return result

        await page.mouse.click(vh_pos['x'], vh_pos['y'])
        await asyncio.sleep(4)

        # Extract visit history from frames
        print(f"[4] Extracting visit history...")
        for frame in page.frames:
            try:
                # Look for table with visits - check for Date column header
                visits_data = await frame.evaluate("""
                    () => {
                        // Find the correct table by looking for 'Date' header
                        const tables = document.querySelectorAll('table');
                        let visitTable = null;

                        for (const table of tables) {
                            const headers = table.querySelectorAll('th');
                            for (const th of headers) {
                                if (th.textContent.trim() === 'Date') {
                                    visitTable = table;
                                    break;
                                }
                            }
                            if (visitTable) break;
                        }

                        if (!visitTable) return null;

                        const visits = [];
                        const rows = visitTable.querySelectorAll('tbody tr, tr:not(:first-child)');

                        for (const row of rows) {
                            const cells = row.querySelectorAll('td');
                            if (cells.length >= 4) {
                                const date = cells[0]?.textContent?.trim() || '';
                                // Skip if date doesn't look like a date (e.g., "M" from calendar)
                                if (date && date.match(/^\\d{4}-\\d{2}-\\d{2}$/)) {
                                    visits.push({
                                        date: date,
                                        issue: cells[1]?.textContent?.trim() || '',
                                        reason_form: cells[2]?.textContent?.trim() || '',
                                        provider: cells[3]?.textContent?.trim() || '',
                                        billing: cells[4]?.textContent?.trim() || ''
                                    });
                                }
                            }
                        }

                        return visits.length > 0 ? visits : null;
                    }
                """)

                if visits_data:
                    result.visits = [VisitRecord(**v) for v in visits_data]
                    result.total_visits = len(result.visits)
                    break

            except Exception as e:
                continue

        result.success = True
        result.message = f"Found {result.total_visits} visit(s)"

        # Take screenshot
        if screenshot_dir:
            screenshot_dir = Path(screenshot_dir)
            screenshot_dir.mkdir(exist_ok=True)
            screenshot_path = screenshot_dir / "visit_history.png"
            await page.screenshot(path=str(screenshot_path))
            result.screenshot_path = str(screenshot_path)
            print(f"[5] Screenshot saved: {screenshot_path}")

        return result


async def main():
    parser = argparse.ArgumentParser(description="Get visit history from OpenEMR")
    parser.add_argument("--patient", required=True, help="Patient name to search for")
    parser.add_argument("--username", default="admin", help="OpenEMR username")
    parser.add_argument("--password", default="pass", help="OpenEMR password")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--screenshot-dir", default="visits_screenshots", help="Screenshot directory")
    parser.add_argument("--output", default=None, help="Output JSON file for visit data")

    args = parser.parse_args()

    print("="*60)
    print("VISIT HISTORY - OpenEMR Automation")
    print("="*60)

    result = await get_visit_history(
        patient_name=args.patient,
        username=args.username,
        password=args.password,
        headless=args.headless,
        screenshot_dir=args.screenshot_dir
    )

    print("\n" + "="*60)
    print(f"Result: {'SUCCESS' if result.success else 'FAILED'}")
    print(f"Message: {result.message}")
    print(f"Patient: {result.patient_name}")
    print(f"Total Visits: {result.total_visits}")

    if result.visits:
        print("\nVisit Records:")
        for i, visit in enumerate(result.visits, 1):
            print(f"  {i}. {visit.date} - {visit.provider} - {visit.reason_form[:30]}")

    if result.screenshot_path:
        print(f"\nScreenshot: {result.screenshot_path}")
    print("="*60)

    # Save to JSON if requested
    if args.output and result.success:
        output_data = {
            "patient": result.patient_name,
            "total_visits": result.total_visits,
            "visits": [asdict(v) for v in result.visits]
        }
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"\nData saved to: {args.output}")

    return result


if __name__ == "__main__":
    asyncio.run(main())

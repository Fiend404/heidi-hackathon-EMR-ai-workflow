#!/usr/bin/env python3
"""
OpenEMR Current Visit - Reusable Camoufox Automation

Views the currently open encounter for a selected patient.
Requires both patient and encounter to be selected.

Usage:
    uv run python visits/current.py --patient "Belford"
    uv run python visits/current.py --patient "Belford" --encounter "2014-02-01"
"""

import asyncio
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List, Dict
from camoufox.async_api import AsyncCamoufox


@dataclass
class EncounterInfo:
    """Information about an encounter"""
    date: str
    provider: Optional[str] = None
    reason: Optional[str] = None


@dataclass
class CurrentVisitResult:
    """Result of current visit operation"""
    success: bool
    encounter_date: Optional[str] = None
    visit_summary: Optional[Dict] = None
    soap_notes: Optional[Dict] = None
    message: str = ""
    screenshot_path: Optional[str] = None


async def get_current_visit(
    patient_name: str,
    encounter_date: Optional[str] = None,
    username: str = "admin",
    password: str = "pass",
    headless: bool = False,
    screenshot_dir: Optional[Path] = None
) -> CurrentVisitResult:
    """
    View the current/active encounter for a patient.

    Args:
        patient_name: Name or partial name to search for patient
        encounter_date: Optional specific encounter date to select
        username: OpenEMR username
        password: OpenEMR password
        headless: Run browser in headless mode
        screenshot_dir: Directory to save screenshots

    Returns:
        CurrentVisitResult with encounter details
    """
    result = CurrentVisitResult(success=False)

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

        # Select encounter from dropdown
        print(f"[3] Selecting encounter...")
        enc_btn = await page.query_selector('button:has-text("Select Encounter")')
        if enc_btn:
            await enc_btn.click()
            await asyncio.sleep(1)

            # Find and click encounter option
            options = await page.query_selector_all('.dropdown-item, .dropdown-menu a')
            if options:
                selected = False
                for opt in options:
                    text = await opt.text_content()
                    if text:
                        text = text.strip()
                        # If specific date requested, match it
                        if encounter_date and encounter_date in text:
                            await opt.click()
                            result.encounter_date = encounter_date
                            selected = True
                            break
                        # Otherwise select first available
                        elif not encounter_date and ('20' in text):  # Year pattern
                            await opt.click()
                            result.encounter_date = text.strip()
                            selected = True
                            break

                if not selected:
                    result.message = "No encounters available to select"
                    return result

                await asyncio.sleep(3)
            else:
                result.message = "No encounter dropdown options found"
                return result
        else:
            result.message = "Select Encounter button not found"
            return result

        # Navigate to Current
        print(f"[4] Opening Current visit...")
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

        # Click Current
        current_pos = await page.evaluate("""
            () => {
                const el = Array.from(document.querySelectorAll('.menuLabel'))
                    .find(e => e.textContent.trim() === 'Current');
                if (el && !el.classList.contains('menuDisabled')) {
                    const r = el.getBoundingClientRect();
                    return {x: r.x + r.width/2, y: r.y + r.height/2};
                }
                return null;
            }
        """)

        if not current_pos:
            result.message = "Current menu item not available (encounter may not be selected)"
            return result

        await page.mouse.click(current_pos['x'], current_pos['y'])
        await asyncio.sleep(4)

        # Extract visit information from frames
        print(f"[5] Extracting visit data...")
        for frame in page.frames:
            try:
                # Look for Visit Summary section
                summary = await frame.evaluate("""
                    () => {
                        const data = {};

                        // Get reason for visit
                        const reason = document.querySelector('[class*="reason"], .visit-reason');
                        if (reason) data.reason = reason.textContent.trim();

                        // Get provider
                        const provider = document.body.innerText.match(/(?:Provider|by)\\s*[:\\-]?\\s*([A-Za-z\\s,]+)/i);
                        if (provider) data.provider = provider[1].trim();

                        // Get patient type
                        const patientType = document.body.innerText.match(/(Established Patient|New Patient)/i);
                        if (patientType) data.patientType = patientType[1];

                        return Object.keys(data).length > 0 ? data : null;
                    }
                """)

                if summary:
                    result.visit_summary = summary

                # Look for SOAP notes
                soap = await frame.evaluate("""
                    () => {
                        const data = {};
                        const text = document.body.innerText;

                        const subj = text.match(/Subjective[:\\s]+([^\\n]+)/i);
                        if (subj) data.subjective = subj[1].trim();

                        const obj = text.match(/Objective[:\\s]+([^\\n]+)/i);
                        if (obj) data.objective = obj[1].trim();

                        const assess = text.match(/Assessment[:\\s]+([^\\n]+)/i);
                        if (assess) data.assessment = assess[1].trim();

                        const plan = text.match(/Plan[:\\s]+([^\\n]+)/i);
                        if (plan) data.plan = plan[1].trim();

                        return Object.keys(data).length > 0 ? data : null;
                    }
                """)

                if soap:
                    result.soap_notes = soap

            except:
                continue

        result.success = True
        result.message = "Current visit loaded successfully"

        # Take screenshot
        if screenshot_dir:
            screenshot_dir = Path(screenshot_dir)
            screenshot_dir.mkdir(exist_ok=True)
            screenshot_path = screenshot_dir / "current_visit.png"
            await page.screenshot(path=str(screenshot_path))
            result.screenshot_path = str(screenshot_path)
            print(f"[6] Screenshot saved: {screenshot_path}")

        return result


async def main():
    parser = argparse.ArgumentParser(description="View current encounter in OpenEMR")
    parser.add_argument("--patient", required=True, help="Patient name to search for")
    parser.add_argument("--encounter", default=None, help="Specific encounter date (e.g., 2014-02-01)")
    parser.add_argument("--username", default="admin", help="OpenEMR username")
    parser.add_argument("--password", default="pass", help="OpenEMR password")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--screenshot-dir", default="visits_screenshots", help="Screenshot directory")

    args = parser.parse_args()

    print("="*60)
    print("CURRENT VISIT - OpenEMR Automation")
    print("="*60)

    result = await get_current_visit(
        patient_name=args.patient,
        encounter_date=args.encounter,
        username=args.username,
        password=args.password,
        headless=args.headless,
        screenshot_dir=args.screenshot_dir
    )

    print("\n" + "="*60)
    print(f"Result: {'SUCCESS' if result.success else 'FAILED'}")
    print(f"Message: {result.message}")
    if result.encounter_date:
        print(f"Encounter: {result.encounter_date}")
    if result.visit_summary:
        print(f"Visit Summary: {result.visit_summary}")
    if result.soap_notes:
        print(f"SOAP Notes: {result.soap_notes}")
    if result.screenshot_path:
        print(f"Screenshot: {result.screenshot_path}")
    print("="*60)

    return result


if __name__ == "__main__":
    asyncio.run(main())

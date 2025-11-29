OpenEMR Two-Phase Browser Automation Workflow

Target URL: https://demo.openemr.io/openemr/interface/login/login.php?site=default
Credentials: admin / pass
Profile Directory: openemr_profile


Phase 1: Login

Using Camoufox with persistent_context and user_data_dir:

1. Navigate to login page
2. Wait for username input to load
3. Click username field, type "admin" with human-like delays
4. Click password field, type "pass" with human-like delays
5. Click submit button
6. Wait for redirect to main interface
7. Save post-login URL to session_state.json


Phase 2: Extract Navigation (with Auto-Login)

Using same persistent profile from Phase 1:

1. Load saved post-login URL from session_state.json
2. Navigate to that URL
3. Check if session expired:
   - URL contains "login"
   - Page contains "Site ID is missing"
   - Page content less than 500 bytes
4. If expired, run auto-login sequence (same as Phase 1)
5. Wait for app to fully load
6. Extract menu items using JavaScript:
   - Query selectors: .menuLabel, [class*="menu"], .nav-link, [role="menuitem"], .dropdown-item
   - Get text, tag, class, href for each element
7. Deduplicate by text content
8. Save results to openemr_navigation.json


Key Patterns:

Persistent Browser Profile:
  - persistent_context=True
  - user_data_dir=PROFILE_DIR

Human-Like Typing:
  - Random delay 50-120ms between characters

Human-Like Clicking:
  - Get element bounding box
  - Move mouse to center with steps
  - Small delay before click

Session Expiry Detection:
  - Check URL for "login"
  - Check page content for error messages
  - Check page size (empty pages indicate redirect)

Target URL: https://demo.openemr.io/openemr/interface/login/login.php?site=default
credentials: admin:pass


Objective: Discover and catalog all accessible EMR pages with menu selectors

You must complete all 4 phases sequentially without stopping.


Phase 1: Login Detection
   - Analyze target URL using curl_cffi and BeautifulSoup
   - Identify form structure (username, password, submit selectors)
   - Return: is_login_page boolean + form selectors if detected

Phase 2: Login Automation (conditional)
   - Skip if Phase 1 detected NOT a login page
   - Use Camoufox to fill form and submit with credentials
   - Retry until login successful
   - Export: screenshot + HTML of post-login page
   - Return: concise success summary

Phase 3: Page Identification and Menu Discovery
   3.1: Screenshot Analysis
      - Read exported screenshot to identify all visible UI elements
      - Document top nav items, dropdowns, user menu
   3.2: BS4 Validation
      - Analyze exported HTML with BeautifulSoup
      - Invoke menu_bs4_analysis directive
      - Output: TREE WITH SELECTORS format
   3.3: HAR Fallback (only if data missing)
      - Analyze HAR file for navigation pages not found in HTML
      - Extract API endpoints if relevant
   - Return: consolidated menu tree with CSS selectors

Phase 4: EMR Classification
   - Invoke emr_classification directive
   - Categorize all menu items into EMR functional areas
   - Return: final summary with category counts

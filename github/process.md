EMR Browser Automation Pipeline

AUTONOMOUS EXECUTION - Do NOT stop between phases

Phase 1: Execute /Users/jasper/Desktop/heidi/browser-automation/phase-prompts/phase-1.md
  - Then IMMEDIATELY proceed to Phase 2

Phase 2: Execute /Users/jasper/Desktop/heidi/browser-automation/phase-prompts/phase-2.md
  - Process EACH category from emr_classification.json sequentially
  - Do NOT stop between categories

Rules:
  - Keep executing until ALL phases and categories complete
  - Fix failures inline, do not stop pipeline

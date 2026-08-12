import os

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
# Base URL of the running Wandora web client.
BASE_URL = os.environ.get("WANDORA_BASE_URL", "http://localhost:3000")

# How long (seconds) Selenium waits for an element before failing.
DEFAULT_TIMEOUT = int(os.environ.get("WANDORA_TIMEOUT", "10"))
# Extra timeout for steps that call the GenAI service (UC02) or any
# other network-bound action -- used where relevant.
AI_TIMEOUT = int(os.environ.get("WANDORA_AI_TIMEOUT", "20"))

# Which local browser to drive.
BROWSER = os.environ.get("WANDORA_BROWSER", "chrome")
HEADLESS = os.environ.get("WANDORA_HEADLESS", "true").lower() == "true"

# ---------------------------------------------------------------------------
# Test accounts
# ---------------------------------------------------------------------------
# Seed these accounts (and one shared trip they belong to) in the test
# environment before running the suite. Nothing here talks to the DB
# directly -- accounts are only ever used through the login form.
ACCOUNTS = {
    "owner": {
        "email": os.environ.get("WANDORA_OWNER_EMAIL", "owner.test@wandora.dev"),
        "password": os.environ.get("WANDORA_OWNER_PASSWORD", "TestPass!123"),
    },
    "editor": {
        "email": os.environ.get("WANDORA_EDITOR_EMAIL", "editor.test@wandora.dev"),
        "password": os.environ.get("WANDORA_EDITOR_PASSWORD", "TestPass!123"),
    },
    "viewer": {
        "email": os.environ.get("WANDORA_VIEWER_EMAIL", "viewer.test@wandora.dev"),
        "password": os.environ.get("WANDORA_VIEWER_PASSWORD", "TestPass!123"),
    },
    "second_editor": {
        "email": os.environ.get("WANDORA_EDITOR2_EMAIL", "editor2.test@wandora.dev"),
        "password": os.environ.get("WANDORA_EDITOR2_PASSWORD", "TestPass!123"),
    },
}

# Trip that owner/editor/viewer/second_editor are ALL already members of.
# Used by the UC08 (Shared Luggage Planning) tests, which need a trip
# with an existing packing list and more than one member.
SHARED_TRIP_ID = os.environ.get("WANDORA_SHARED_TRIP_ID", "trip-shared-demo")

# ---------------------------------------------------------------------------
# Selectors
# ---------------------------------------------------------------------------
# Every selector a test needs, named after the user-facing element it
# points to. Update these to match the real markup -- ideally the
# frontend adds a stable `data-testid` attribute for each one,
# which is why every default below assumes `data-testid`.
SELECTORS = {
    # --- Login page --------------------------------------------------
    "login_email_input": "[data-testid='login-email']",
    "login_password_input": "[data-testid='login-password']",
    "login_submit_button": "[data-testid='login-submit']",
    "login_page_marker": "[data-testid='login-page']",

    # --- Dashboard / navigation ---------------------------------------
    "create_trip_button": "[data-testid='create-new-trip-button']",

    # --- UC01: Trip Creation and Preference Input form -----------------
    "trip_form": "[data-testid='trip-creation-form']",
    "trip_destination_input": "[data-testid='trip-destination']",
    "trip_start_date_input": "[data-testid='trip-start-date']",
    "trip_end_date_input": "[data-testid='trip-end-date']",
    "trip_capacity_select": "[data-testid='trip-capacity']",
    "trip_budget_select": "[data-testid='trip-budget']",
    "trip_style_select": "[data-testid='trip-style']",
    "trip_continue_button": "[data-testid='trip-continue-button']",
    "trip_validation_alert": "[data-testid='trip-validation-alert']",
    "trip_status_badge": "[data-testid='trip-status-badge']",
    "ai_generation_indicator": "[data-testid='ai-generation-indicator']",

    # --- UC08: Shared Luggage Planning (Packing List) -------------------
    "packing_list_nav_link": "[data-testid='nav-packing-list']",
    "packing_item_row": "[data-testid='packing-item-row']",  # use with item name
    "packing_item_checkbox": "[data-testid='packing-item-checkbox']",
    "packing_item_assignee_select": "[data-testid='packing-item-assignee']",
    "packing_item_assignee_avatar": "[data-testid='packing-item-assignee-avatar']",
    "add_custom_item_button": "[data-testid='add-custom-item-button']",
    "custom_item_name_input": "[data-testid='custom-item-name-input']",
    "custom_item_save_button": "[data-testid='custom-item-save-button']",
    "permission_denied_toast": "[data-testid='permission-denied-toast']",
}

import os

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
# Base URL of the running Wandora web client.
BASE_URL = os.environ.get("WANDORA_BASE_URL", "http://127.0.0.1:5173")

# How long (seconds) Selenium waits for an element before failing.
DEFAULT_TIMEOUT = int(os.environ.get("WANDORA_TIMEOUT", "10"))
# Extra timeout for steps that call the GenAI service (UC02) or any
# other network-bound action -- used where relevant.
AI_TIMEOUT = int(os.environ.get("WANDORA_AI_TIMEOUT", "20"))

# Which local browser to drive.
BROWSER = os.environ.get("WANDORA_BROWSER", "chrome")
HEADLESS = os.environ.get("WANDORA_HEADLESS", "true").lower() == "true"

# ---------------------------------------------------------------------------
# Selectors
# ---------------------------------------------------------------------------
# Every selector a test needs, named after the user-facing element it
# points to. Update these to match the real markup -- ideally the
# frontend adds a stable `data-testid` attribute for each one,
# which is why every default below assumes `data-testid`.
SELECTORS = {
    # --- Authentication -------------------------------------------------
    "auth_email_input": "[data-testid='auth-email']",
    "auth_password_input": "[data-testid='auth-password']",
    "signup_name_input": "[data-testid='signup-name']",
    "signup_confirm_password_input": "[data-testid='signup-confirm-password']",
    "signup_submit_button": "[data-testid='signup-submit']",
    "login_submit_button": "[data-testid='login-submit']",
    "trip_dashboard": "[data-testid='trip-dashboard']",
    "dashboard_trip_card": "[data-testid='dashboard-trip-card']",
    "dashboard_signout_button": "[data-testid='dashboard-signout']",
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
    # --- UC02: AI Itinerary Generation ----------------------------------
    "itinerary_view": "[data-testid='itinerary-view']",
    "activity_row": "[data-testid='activity-row']",
    "regenerate_button": "[data-testid='regenerate-itinerary-button']",
}

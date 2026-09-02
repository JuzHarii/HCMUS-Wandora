import os

BASE_URL = os.environ.get("WANDORA_BASE_URL", "http://localhost:5173").rstrip("/")
DEFAULT_TIMEOUT = int(os.environ.get("WANDORA_TIMEOUT", "10"))
AI_TIMEOUT = int(os.environ.get("WANDORA_AI_TIMEOUT", "45"))

BROWSER = os.environ.get("WANDORA_BROWSER", "chrome").lower()
HEADLESS = os.environ.get("WANDORA_HEADLESS", "true").lower() not in {"0", "false", "no"}

SELECTORS = {
    "auth_email_input": "[data-testid='auth-email']",
    "auth_password_input": "[data-testid='auth-password']",
    "signup_name_input": "[data-testid='signup-name']",
    "signup_confirm_password_input": "[data-testid='signup-confirm-password']",
    "signup_submit_button": "[data-testid='signup-submit']",
    "trip_dashboard": "[data-testid='trip-dashboard']",
    "dashboard_trip_card": "[data-testid='dashboard-trip-card']",
    "trip_form": "[data-testid='trip-creation-form']",
    "trip_invitation_continue": "[data-testid='trip-invitation-continue']",
    "trip_destination_input": "[data-testid='trip-destination']",
    "trip_start_date_input": "[data-testid='trip-start-date']",
    "trip_end_date_input": "[data-testid='trip-end-date']",
    "trip_capacity_input": "[data-testid='trip-capacity']",
    "trip_budget_input": "[data-testid='trip-budget']",
    "trip_continue_button": "[data-testid='trip-continue-button']",
    "trip_validation_alert": "[data-testid='trip-validation-alert']",
    "trip_review_ready": "[data-testid='trip-review-ready']",
    "generate_preview_button": "[data-testid='generate-preview-button']",
    "blank_itinerary_button": "[data-testid='blank-itinerary-button']",
    "save_trip_button": "[data-testid='save-trip-button']",
    "open_trip_workspace": "[data-testid='open-trip-workspace']",
    "preview_day_card": "[data-testid='preview-day-card']",
    "preview_activity_row": "[data-testid='preview-activity-row']",
    "itinerary_view": "[data-testid='itinerary-view']",
    "activity_row": "[data-testid='activity-row']",
}

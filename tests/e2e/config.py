import os

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
# Base URL of the running Wandora web client.
BASE_URL = os.environ.get("WANDORA_BASE_URL", "http://localhost:5173")

# How long (seconds) Selenium waits for an element before failing.
DEFAULT_TIMEOUT = int(os.environ.get("WANDORA_TIMEOUT", "10"))
# Extra timeout for steps that call the GenAI service (UC02) or any
# other network-bound action -- used where relevant.
AI_TIMEOUT = int(os.environ.get("WANDORA_AI_TIMEOUT", "20"))

# Which local browser to drive.
BROWSER = os.environ.get("WANDORA_BROWSER", "chrome")
HEADLESS = os.environ.get("WANDORA_HEADLESS", "false").lower() == "false"

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
    "trip_invitation_continue": "[data-testid='trip-invitation-continue']",
    "trip_destination_input": "[data-testid='trip-destination']",
    "trip_start_date_input": "[data-testid='trip-start-date']",
    "trip_end_date_input": "[data-testid='trip-end-date']",
    "trip_capacity_select": "[data-testid='trip-capacity']",
    "trip_budget_select": "[data-testid='trip-budget']",
    "trip_continue_button": "[data-testid='trip-continue-button']",
    "trip_validation_alert": "[data-testid='trip-validation-alert']",
    "trip_status_badge": "[data-testid='trip-status-badge']",
    "ai_generation_indicator": "[data-testid='ai-generation-indicator']",
    "generate_preview_button": "[data-testid='generate-preview-button']",
    "save_trip_button": "[data-testid='save-trip-button']",
    "open_trip_workspace": "[data-testid='open-trip-workspace']",

    # --- UC02: AI Itinerary Generation ----------------------------------
    "itinerary_view": "[data-testid='itinerary-view']",
    "activity_row": "[data-testid='activity-row']",
    "regenerate_button": "[data-testid='regenerate-itinerary-button']",

    # --- UC03: AI Itinerary Adjustment ------------------------------------
    "itinerary_adjustment_input": "[data-testid='itinerary-adjustment-input']",
    "itinerary_adjustment_submit": "[data-testid='itinerary-adjustment-submit']",
    "itinerary_adjustment_preview": "[data-testid='itinerary-adjustment-preview']",
    "itinerary_adjustment_accept": "[data-testid='itinerary-adjustment-accept']",
    "itinerary_adjustment_discard": "[data-testid='itinerary-adjustment-discard']",
    "permission_denied_modal": "[data-testid='permission-denied-modal']",
    "adjustment_conflict_warning": "[data-testid='adjustment-conflict-warning']",
    "adjustment_error_alert": "[data-testid='adjustment-error-alert']",

    # --- UC04: Manual Places and External Links ---------------------------
    "add_activity_button": "[data-testid='add-activity-button']",
    "activity_name_input": "[data-testid='activity-name-input']",
    "activity_category_select": "[data-testid='activity-category-select']",
    "activity_notes_textarea": "[data-testid='activity-notes-textarea']",
    "activity_url_input": "[data-testid='activity-url-input']",
    "activity_save_button": "[data-testid='activity-save-button']",
    "activity_form_validation_alert": "[data-testid='activity-form-validation-alert']",
    "activity_manual_badge": "[data-testid='activity-manual-badge']",
    "delete_activity_button": "[data-testid='delete-activity-button']",

    # --- UC05: Group Collaboration (Screen 2A/2B - Invite Members) -------
    "members_settings_button": "[data-testid='members-settings-button']",
    "member_invite_email_input": "[data-testid='member-invite-email']",
    "member_invite_role_select": "[data-testid='member-invite-role']",
    "member_invite_send_button": "[data-testid='member-invite-send']",
    "member_invite_link_display": "[data-testid='member-invite-link']",
    "member_list_item": "[data-testid='member-list-item']",
    "invite_permission_denied": "[data-testid='invite-permission-denied']",
    "invite_duplicate_warning": "[data-testid='invite-duplicate-warning']",
    "invite_invalid_token_warning": "[data-testid='invite-invalid-token-warning']",

    # --- UC06: Role and Permission Management -----------------------------
    "member_role_select": "[data-testid='member-role-select']",
    "member_role_save_button": "[data-testid='member-role-save']",
    "ownership_transfer_confirm_button": "[data-testid='ownership-transfer-confirm']",
    "rbac_action_denied_alert": "[data-testid='rbac-action-denied-alert']",
    "demote_last_owner_error": "[data-testid='demote-last-owner-error']",

    # --- UC07: AI Packing Suggestions (Screen 5A/5B - Packing List tab) --
    "packing_tab": "[data-testid='packing-tab']",
    "generate_packing_button": "[data-testid='generate-packing-checklist-button']",
    "packing_item_row": "[data-testid='packing-item-row']",
    "packing_offline_warning": "[data-testid='packing-offline-warning']",
    "packing_overwrite_confirm_button": "[data-testid='packing-overwrite-confirm']",
    "packing_missing_metadata_warning": "[data-testid='packing-missing-metadata-warning']",

    # --- UC08: Shared Luggage Planning -------------------------------------
    "luggage_item_assignee_select": "[data-testid='luggage-item-assignee-select']",
    "luggage_item_checkbox": "[data-testid='luggage-item-checkbox']",
    "add_custom_luggage_button": "[data-testid='add-custom-luggage-button']",
    "custom_luggage_name_input": "[data-testid='custom-luggage-name-input']",
    "custom_luggage_save_button": "[data-testid='custom-luggage-save-button']",
    "personal_checklist_view": "[data-testid='personal-checklist-view']",

    # --- UC09: Manual Place Note Input --------------------------------------
    "edit_notes_button": "[data-testid='edit-notes-button']",
    "notes_editor_textarea": "[data-testid='notes-editor-textarea']",
    "notes_save_button": "[data-testid='notes-save-button']",
    "notes_locked_warning": "[data-testid='notes-locked-warning']",
    "notes_permission_denied": "[data-testid='notes-permission-denied']",

    # --- UC10: Place Ratings and Reviews ------------------------------------
    "add_review_button": "[data-testid='add-review-button']",
    "review_text_input": "[data-testid='review-text-input']",
    "review_submit_button": "[data-testid='review-submit-button']",
    "review_validation_alert": "[data-testid='review-validation-alert']",
    "review_display": "[data-testid='review-display']",

    # --- UC11: Share or Export Trip Plan ------------------------------------
    "share_export_button": "[data-testid='share-export-button']",
    "generate_share_link_button": "[data-testid='generate-share-link-button']",
    "share_access_select": "[data-testid='share-access-select']",
    "share_link_display": "[data-testid='share-link-display']",
    "export_pdf_button": "[data-testid='export-pdf-button']",
    "revoke_link_button": "[data-testid='revoke-link-button']",
    "revoked_link_warning": "[data-testid='revoked-link-warning']",
    "export_error_alert": "[data-testid='export-error-alert']",
    "export_empty_itinerary_warning": "[data-testid='export-empty-itinerary-warning']",

    # --- UC13: Review and Save AI Itinerary (preview screen) --------------
    "back_to_details_button": "[data-testid='back-to-details-button']",
    "leave_preview_cancel_button": "[data-testid='leave-preview-cancel-button']",
    "leave_preview_warning": "[data-testid='leave-preview-warning']",
    "leave_preview_confirm_button": "[data-testid='leave-preview-confirm-button']",
    "preview_add_activity_button": "[data-testid='preview-add-activity-button']",
    "preview_activity_row": "[data-testid='preview-activity-row']",

    # --- UC14: Post-Scheduling Feature Access -------------------------------
    "reviews_tab": "[data-testid='reviews-tab']",
    "share_export_tab": "[data-testid='share-export-tab']",
    "feature_locked_warning": "[data-testid='feature-locked-warning']",
    "completion_indicator": "[data-testid='completion-indicator']",

    # --- UC15: Group Member Interaction (Voting and Comments) --------------
    "activity_comment_input": "[data-testid='activity-comment-input']",
    "activity_comment_submit": "[data-testid='activity-comment-submit']",
    "activity_alt_proposal_input": "[data-testid='activity-alt-proposal-input']",
    "activity_alt_proposal_submit": "[data-testid='activity-alt-proposal-submit']",
    "proposal_card": "[data-testid='proposal-card']",
    "proposal_vote_button": "[data-testid='proposal-vote-button']",
    "proposal_vote_count": "[data-testid='proposal-vote-count']",
    "apply_change_button": "[data-testid='apply-change-to-itinerary-button']",
    "apply_decision_button": "[data-testid='apply-decision-button']",
    "consensus_status": "[data-testid='consensus-status']",

    # --- UC16: Duplicate/Similar Trip Detection -----------------------------
    "similar_trip_modal": "[data-testid='similar-trip-modal']",
    "similar_trip_use_template_button": "[data-testid='similar-trip-use-template-button']",
    "similar_trip_open_existing_button": "[data-testid='similar-trip-open-existing-button']",
    "similar_trip_continue_new_button": "[data-testid='similar-trip-continue-new-button']",

    # --- UC17: Trip History ---------------------------------------------------
    "trip_history_link": "[data-testid='trip-history-link']",
    "trip_history_empty_state": "[data-testid='trip-history-empty-state']",
    "version_history_button": "[data-testid='version-history-button']",
    "version_history_item": "[data-testid='version-history-item']",
    "version_restore_button": "[data-testid='version-restore-button']",
    "version_history_empty_message": "[data-testid='version-history-empty-message']",
}
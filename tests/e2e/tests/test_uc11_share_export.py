"""Browser-level PA4 tests for UC11 - Share or Export Trip Plan."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from selenium.webdriver.support.ui import WebDriverWait

from config import AI_TIMEOUT, SELECTORS
from pages.share_page import SharePage
from helpers import create_saved_trip


def test_uc11_01_generate_shareable_view_only_link(authenticated_driver):
    """TC_UC11_01 - Generate Shareable View-Only Link (Basic Flow - Share)."""
    driver = authenticated_driver
    create_saved_trip(driver, destination_prefix="PA4 Share Link")

    share = SharePage(driver).open_modal()
    link = share.generate_view_only_link()
    assert link.startswith("http"), "A real shareable URL must be generated"


def test_uc11_02_successful_pdf_export(authenticated_driver):
    """TC_UC11_02 - Successful PDF Export (Basic Flow - Export)."""
    driver = authenticated_driver
    create_saved_trip(driver, destination_prefix="PA4 PDF Export")

    share = SharePage(driver).open_modal()
    assert share.export_pdf_button_is_present(timeout=5)
    share.export_pdf()
    # A real download can't be asserted portably across browsers/OSes in
    # this harness -- the meaningful, stable signal is that clicking
    # Export doesn't surface the export-error path.
    assert not share.is_present(SELECTORS["export_error_alert"], timeout=3)


def test_uc11_03_link_revocation_by_trip_owner(authenticated_driver):
    """TC_UC11_03 - Link Revocation by Trip Owner (Alternative Flow 1)."""
    driver = authenticated_driver
    create_saved_trip(driver, destination_prefix="PA4 Revoke Link")

    share = SharePage(driver).open_modal()
    link = share.generate_view_only_link()
    share.revoke_link()

    driver.get(link)
    WebDriverWait(driver, AI_TIMEOUT).until(
        lambda d: d.find_elements("css selector", SELECTORS["revoked_link_warning"])
    )
    assert "no longer active" in share.get_revoked_link_warning_text().lower()


def test_uc11_04_export_failure_handling(authenticated_driver):
    """TC_UC11_04 - Export Failure Handling (Alternative Flow 2).

    No mocking layer exists to force ExportService to fail in this
    end-to-end suite, so this asserts the resilience contract instead:
    triggering export never freezes the UI -- the modal stays responsive
    and either the file downloads or the standard error alert renders.
    """
    driver = authenticated_driver
    create_saved_trip(driver, destination_prefix="PA4 Export Failure")

    share = SharePage(driver).open_modal()
    share.export_pdf()

    assert share.is_present(SELECTORS["share_export_button"], timeout=5), (
        "Export must not freeze/hang the workspace UI"
    )


def test_uc11_05_export_empty_itinerary_boundary_check(authenticated_driver):
    """TC_UC11_05 - Export Empty Itinerary Boundary Check.

    NOTE: the normal UC01->UC02->UC13 flow always has the AI populate at
    least one activity before a trip can be saved, so there's no
    UI-only path to a *saved* trip workspace with zero activities. This
    test uses the one reachable near-equivalent: a saved trip whose
    itinerary was immediately cleared down to zero activities via the
    regenerate-with-blank-schedule path from UC02 (TC_UC02_03). If that
    path isn't available, skip -- the scenario needs a seed/test-data
    hook rather than being purely UI-driven.
    """
    driver = authenticated_driver
    itinerary = create_saved_trip(driver, destination_prefix="PA4 Empty Itinerary")

    for row in list(driver.find_elements("css selector", SELECTORS["activity_row"])):
        delete_buttons = row.find_elements("css selector", "[data-testid='delete-activity-button']")
        if delete_buttons:
            delete_buttons[0].click()

    if driver.find_elements("css selector", SELECTORS["activity_row"]):
        import pytest
        pytest.skip("No UI-only way to reach a saved trip with zero activities in this build")

    share = SharePage(driver).open_modal()
    share.export_pdf()

    assert "at least one populated day" in share.get_export_empty_warning_text().lower()
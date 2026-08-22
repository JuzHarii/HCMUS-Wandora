"""Browser-level PA4 tests for UC10 - Place Ratings and Reviews.

Reviews are only allowed on trips that have already happened ("visited"
places on a completed trip). Since a freshly created trip is always in
the future relative to `datetime.now()`, TC_UC10_01/02/05 use a trip
whose dates are in the past so its status naturally resolves to
completed/visited; TC_UC10_04 deliberately keeps a trip in the future to
check the restriction.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from selenium.webdriver.support.ui import WebDriverWait

from config import AI_TIMEOUT, SELECTORS
from pages.review_page import ReviewPage
from helpers import create_saved_trip


def _create_past_trip(driver):
    return create_saved_trip(
        driver,
        destination_prefix="PA4 Completed Trip",
        start_date="2025-01-05",
        end_date="2025-01-10",
    )


def test_uc10_01_submit_star_rating_and_text_review(authenticated_driver):
    """TC_UC10_01 - Submit Star Rating and Text Review (Basic Flow)."""
    driver = authenticated_driver
    _create_past_trip(driver)

    review = ReviewPage(driver).open_review_form(place_index=0)
    review.select_stars(5)
    review.set_review_text("Amazing views at night! Highly recommend.")
    review.submit()

    WebDriverWait(driver, AI_TIMEOUT).until(lambda d: review.get_review_texts())
    assert "Amazing views" in " ".join(review.get_review_texts())


def test_uc10_02_modify_existing_review(authenticated_driver):
    """TC_UC10_02 - Modify Existing Review (Alternative Flow 1)."""
    driver = authenticated_driver
    _create_past_trip(driver)

    review = ReviewPage(driver).open_review_form(place_index=0)
    review.select_stars(5)
    review.set_review_text("Amazing views at night! Highly recommend.")
    review.submit()
    WebDriverWait(driver, AI_TIMEOUT).until(lambda d: review.get_review_texts())

    review.open_review_form(place_index=0)
    review.select_stars(4)
    review.set_review_text("Amazing views, but very crowded.")
    review.submit()

    WebDriverWait(driver, AI_TIMEOUT).until(
        lambda d: "crowded" in " ".join(review.get_review_texts()).lower()
    )
    all_reviews = review.get_review_texts()
    assert len(all_reviews) == 1, "Editing must update the existing record, not create a duplicate"


def test_uc10_03_rating_boundary_check_zero_stars(authenticated_driver):
    """TC_UC10_03 - Rating Boundary Check - Zero Stars."""
    driver = authenticated_driver
    _create_past_trip(driver)

    review = ReviewPage(driver).open_review_form(place_index=0)
    review.set_review_text("Some text but no stars selected.")
    review.submit()

    assert "1 and 5 stars" in review.get_validation_text().lower() or "select a rating" in review.get_validation_text().lower()


def test_uc10_04_precondition_validation_future_trip_restriction(authenticated_driver):
    """TC_UC10_04 - Pre-condition Validation (Future Trip Restriction)."""
    driver = authenticated_driver
    create_saved_trip(driver, destination_prefix="PA4 Future Trip")

    review = ReviewPage(driver)
    assert not review.add_review_button_is_present(timeout=3), (
        "Add Review must be hidden/disabled for trips that haven't happened yet"
    )


def test_uc10_05_empty_text_review_stars_only(authenticated_driver):
    """TC_UC10_05 - Empty Text Review (Stars Only)."""
    driver = authenticated_driver
    _create_past_trip(driver)

    review = ReviewPage(driver).open_review_form(place_index=0)
    review.select_stars(4)
    review.submit()

    WebDriverWait(driver, AI_TIMEOUT).until(lambda d: review.get_review_texts())
    assert review.get_review_texts()
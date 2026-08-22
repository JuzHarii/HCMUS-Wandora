"""Browser-level PA4 tests for UC15 - Group Member Interaction (Voting and Comments)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from selenium.webdriver.support.ui import WebDriverWait

from config import AI_TIMEOUT
from pages.members_page import MembersPage
from helpers import create_saved_trip, join_trip_via_invite


def test_uc15_01_add_comment_and_alternative_proposal(authenticated_driver, second_authenticated_driver):
    """TC_UC15_01 - Add Comment and Alternative Proposal (Basic Flow)."""
    owner_driver = authenticated_driver
    owner_page = create_saved_trip(owner_driver, destination_prefix="PA4 UC15 Comment")
    invite_link = MembersPage(owner_driver).invite(second_authenticated_driver.pa4_email, "Editor").get_invite_link()
    member_b_page = join_trip_via_invite(second_authenticated_driver, invite_link)

    owner_page.add_comment(activity_index=0, comment_text="This museum looks great!")
    owner_page.propose_alternative(activity_index=0, proposal_text="Visit modern art museum instead.")

    WebDriverWait(second_authenticated_driver, AI_TIMEOUT).until(
        lambda d: "modern art museum" in d.page_source.lower()
    )


def test_uc15_02_cast_vote_on_suggestion(authenticated_driver, second_authenticated_driver):
    """TC_UC15_02 - Cast Vote on Suggestion (Basic Flow - Vote)."""
    owner_driver = authenticated_driver
    owner_page = create_saved_trip(owner_driver, destination_prefix="PA4 UC15 Vote")
    invite_link = MembersPage(owner_driver).invite(second_authenticated_driver.pa4_email, "Editor").get_invite_link()
    member_b_page = join_trip_via_invite(second_authenticated_driver, invite_link)

    owner_page.propose_alternative(activity_index=0, proposal_text="Visit modern art museum instead.")
    before = member_b_page.get_vote_count(proposal_index=0)

    member_b_page.vote_on_proposal(proposal_index=0)

    WebDriverWait(second_authenticated_driver, AI_TIMEOUT).until(
        lambda d: member_b_page.get_vote_count(proposal_index=0) != before
    )


def test_uc15_03_viewer_voting_action_boundary(authenticated_driver, second_authenticated_driver):
    """TC_UC15_03 - Viewer Voting Action Boundary (Alternative Flow 1)."""
    owner_driver = authenticated_driver
    owner_page = create_saved_trip(owner_driver, destination_prefix="PA4 UC15 Viewer Boundary")
    invite_link = MembersPage(owner_driver).invite(second_authenticated_driver.pa4_email, "Viewer").get_invite_link()
    viewer_page = join_trip_via_invite(second_authenticated_driver, invite_link)

    owner_page.propose_alternative(activity_index=0, proposal_text="Visit modern art museum instead.")
    WebDriverWait(second_authenticated_driver, AI_TIMEOUT).until(
        lambda d: "modern art museum" in d.page_source.lower()
    )

    viewer_page.add_comment(activity_index=0, comment_text="I like this idea!")
    viewer_page.vote_on_proposal(proposal_index=0)

    assert not viewer_page.apply_change_control_is_visible(proposal_index=0, timeout=3), (
        "Apply Change to Itinerary must be locked/hidden for Viewers"
    )


def test_uc15_04_vote_tie_resolution_by_owner(authenticated_driver, second_authenticated_driver, third_authenticated_driver):
    """TC_UC15_04 - Vote Tie Resolution by Owner (Alternative Flow 2)."""
    owner_driver = authenticated_driver
    owner_page = create_saved_trip(owner_driver, destination_prefix="PA4 UC15 Tie")
    link_b = MembersPage(owner_driver).invite(second_authenticated_driver.pa4_email, "Editor").get_invite_link()
    member_b_page = join_trip_via_invite(second_authenticated_driver, link_b)
    link_c = MembersPage(owner_driver).invite(third_authenticated_driver.pa4_email, "Editor").get_invite_link()
    member_c_page = join_trip_via_invite(third_authenticated_driver, link_c)

    owner_page.propose_alternative(activity_index=0, proposal_text="Option A: Rooftop bar.")
    owner_page.propose_alternative(activity_index=0, proposal_text="Option B: Night market.")
    WebDriverWait(second_authenticated_driver, AI_TIMEOUT).until(lambda d: "option a" in d.page_source.lower())

    # Two votes each -> tie.
    member_b_page.vote_on_proposal(proposal_index=0)
    member_c_page.vote_on_proposal(proposal_index=0)
    owner_page.vote_on_proposal(proposal_index=1)
    member_b_page.vote_on_proposal(proposal_index=1)

    WebDriverWait(owner_driver, AI_TIMEOUT).until(
        lambda d: "no consensus" in owner_page.get_consensus_status_text().lower()
    )

    owner_page.apply_owner_decision(proposal_index=0)
    assert owner_page.is_present("[data-testid='activity-row']", timeout=5)


def test_uc15_05_real_time_vote_sync_over_sockets(authenticated_driver, second_authenticated_driver):
    """TC_UC15_05 - Real-Time Vote Sync Over Sockets."""
    owner_driver = authenticated_driver
    owner_page = create_saved_trip(owner_driver, destination_prefix="PA4 UC15 Sync")
    invite_link = MembersPage(owner_driver).invite(second_authenticated_driver.pa4_email, "Editor").get_invite_link()
    member_b_page = join_trip_via_invite(second_authenticated_driver, invite_link)

    owner_page.propose_alternative(activity_index=0, proposal_text="Visit the night market instead.")
    WebDriverWait(second_authenticated_driver, AI_TIMEOUT).until(
        lambda d: "night market" in d.page_source.lower()
    )
    before = member_b_page.get_vote_count(proposal_index=0)

    owner_page.vote_on_proposal(proposal_index=0)

    # Member B never reloads -- the tally must update live via websocket.
    WebDriverWait(second_authenticated_driver, AI_TIMEOUT).until(
        lambda d: member_b_page.get_vote_count(proposal_index=0) != before
    )
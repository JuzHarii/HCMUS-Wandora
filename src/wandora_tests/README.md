# Wandora Functional Tests — UC01 & UC08

Automated, browser-driven (Selenium + pytest) implementations of the
test cases already designed for:

- **UC01 — Trip Creation and Preference Input** (`TC_UC01_01`–`05`)
- **UC08 — Shared Luggage Planning** (`TC_UC08_01`–`05`)

as listed in `test-cases_template-v1_1.xlsx`.

## Why it's built this way

- **Black-box / UI-level only.** Every test drives a real browser
  through the actual pages a user sees (login → dashboard → forms).
  Nothing here imports backend code or talks to the database directly
  — the app is treated as an opaque system under test, so the suite
  keeps working even if the backend implementation changes.
- **Page Object pattern.** `pages/` holds one small class per screen
  (`LoginPage`, `TripCreationPage`, `PackingListPage`). Test files in
  `tests/` read like the use-case flows themselves — e.g.
  `trip_page.fill_trip_form(...); trip_page.submit()` — with no
  Selenium boilerplate mixed in.
- **One file, one config source.** `config.py` holds the base URL,
  timeouts, test accounts, and every CSS selector. If your teammates'
  markup uses different `data-testid` values, that's the only file to
  edit.

## Project layout

```
wandora_tests/
├── config.py                 # URLs, accounts, timeouts, selectors
├── conftest.py                # pytest fixtures (browser open/close, screenshots)
├── requirements.txt
├── pages/
│   ├── base_page.py            # generic Selenium wait/click/type helpers
│   ├── login_page.py
│   ├── trip_creation_page.py   # UC01
│   └── packing_list_page.py    # UC08
└── tests/
    ├── test_uc01_trip_creation.py
    └── test_uc08_shared_luggage_planning.py
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Install a matching browser driver (Selenium 4 auto-manages this for
   recent Chrome/Edge; if not, install `chromedriver` / `msedgedriver`
   and put it on your `PATH`).
3. Point the suite at your running frontend and seed test accounts:
   ```bash
   export WANDORA_BASE_URL="http://localhost:3000"
   export WANDORA_OWNER_EMAIL="owner.test@wandora.dev"
   export WANDORA_OWNER_PASSWORD="TestPass!123"
   # ...editor / viewer / second_editor, see config.py for full list
   export WANDORA_SHARED_TRIP_ID="trip-shared-demo"
   ```
   `config.py` has sensible defaults for everything, so you only need
   to override what's different in your environment.
4. **Seed data required before running UC08 tests:** a trip
   (`WANDORA_SHARED_TRIP_ID`) that `owner`, `editor`, `viewer`, and
   `second_editor` are all members of, with a packing checklist that
   already contains items named `Tent`, `First Aid Kit`, and `Camera`.

## Running

```bash
# everything
pytest tests/ -v

# just one use case
pytest tests/test_uc01_trip_creation.py -v
pytest tests/test_uc08_shared_luggage_planning.py -v

# a single test case
pytest tests/test_uc01_trip_creation.py::test_uc01_05_end_date_before_start_date_is_rejected -v
```

Run headed (visible browser, useful when you want to grab screenshots
for the test report by hand):
```bash
export WANDORA_HEADLESS=false
pytest tests/ -v
```

Any failing test automatically saves a screenshot to `screenshots/`
(see `conftest.py`) — a quick source for the 2–3 evidence screenshots
the test report needs.

## Matching selectors to the real app

Every selector the tests need is listed once in `config.py`'s
`SELECTORS` dict, named by what it represents (e.g.
`"trip_destination_input"`). Update the CSS selector strings there to
match your team's actual markup; no other file needs to change.

## Traceability

| Test case ID  | Test function                                                    |
| ------------- | ------------------------------------------------------------------ |
| TC_UC01_01    | `test_uc01_01_successful_trip_creation`                           |
| TC_UC01_02    | `test_uc01_02_missing_destination_blocks_submission`              |
| TC_UC01_03    | `test_uc01_03_missing_dates_blocks_submission`                    |
| TC_UC01_04    | `test_uc01_04_guest_is_redirected_to_login`                       |
| TC_UC01_05    | `test_uc01_05_end_date_before_start_date_is_rejected`             |
| TC_UC08_01    | `test_uc08_01_assign_item_to_member`                              |
| TC_UC08_02    | `test_uc08_02_realtime_completion_sync_across_sessions`           |
| TC_UC08_03    | `test_uc08_03_concurrent_assignment_conflict_resolved_by_latest_write` |
| TC_UC08_04    | `test_uc08_04_add_custom_luggage_item`                            |
| TC_UC08_05    | `test_uc08_05_viewer_cannot_modify_other_members_items`           |

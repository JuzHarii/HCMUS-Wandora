# PA5 automated Selenium tests

This suite covers PA5 automated testing for two implemented Wandora use cases:

- UC01 - Trip Creation and Preference Input
- UC02 - AI Itinerary Generator

Each use case has two automated scenarios. Login/sign-up is handled by a pytest
fixture because UC01 and UC02 both require an authenticated user as a
precondition.

## Covered scenarios

| Use case | Test script | Scenario |
| --- | --- | --- |
| UC01 | `tests/e2e/tests/test_uc01_trip_creation.py::test_tc_uc01_01_successful_trip_creation_reaches_review` | Valid trip details are accepted and the user reaches the itinerary review/generation step. |
| UC01 | `tests/e2e/tests/test_uc01_trip_creation.py::test_tc_uc01_03_invalid_date_order_blocks_submission` | End date before start date is rejected with a validation message. |
| UC02 | `tests/e2e/tests/test_uc02_itinerary_generation.py::test_tc_uc02_01_successful_ai_preview_generation` | A valid trip can generate an itinerary preview with activities. |
| UC02 | `tests/e2e/tests/test_uc02_itinerary_generation.py::test_tc_uc02_03_blank_itinerary_can_be_saved` | The user can bypass AI generation by starting with a blank itinerary and saving it. |

## Setup

From the repository root:

```powershell
cd "D:\HCMUS\Year 3\Sem 3\SE"
.\.venv\Scripts\pip.exe install -r src/backend/requirements.txt
.\.venv\Scripts\pip.exe install -r tests/e2e/requirements.txt
npm --prefix src/frontend install
```

Use a test database, not production data. The tests create fresh accounts and
trips through the browser.

## Start the app

Open three PowerShell terminals. Keep Terminal 1 and Terminal 2 running while
Terminal 3 executes the tests.

Terminal 1 - backend:

```powershell
cd "D:\HCMUS\Year 3\Sem 3\SE"
.\.venv\Scripts\alembic.exe -c src/backend/alembic.ini upgrade heads
.\.venv\Scripts\uvicorn.exe --app-dir src/backend main:app --reload --port 8000
```

The backend is ready when you see:

```text
Application startup complete.
Uvicorn running on http://127.0.0.1:8000
```

Terminal 2 - frontend:

```powershell
cd "D:\HCMUS\Year 3\Sem 3\SE"
npm --prefix src/frontend run dev
```

The frontend is ready when you see a local URL such as:

```text
Local: http://localhost:5173/
```

The default Selenium frontend URL is `http://localhost:5173`.

## Run

Terminal 3 - all PA5 E2E tests:

```powershell
cd "D:\HCMUS\Year 3\Sem 3\SE"
.\.venv\Scripts\pytest.exe tests/e2e/tests -v
```

Run one use case:

```powershell
.\.venv\Scripts\pytest.exe tests/e2e/tests/test_uc01_trip_creation.py -v
.\.venv\Scripts\pytest.exe tests/e2e/tests/test_uc02_itinerary_generation.py -v
```

Watch the browser instead of running headless:

```powershell
$env:WANDORA_HEADLESS="false"
.\.venv\Scripts\pytest.exe tests/e2e/tests -v
```

If the frontend runs on another port:

```powershell
$env:WANDORA_BASE_URL="http://localhost:5174"
.\.venv\Scripts\pytest.exe tests/e2e/tests -v
```

Failed test screenshots are saved in `tests/e2e/screenshots/`.

## Troubleshooting

If Selenium fails with `net::ERR_CONNECTION_REFUSED`, the frontend URL used by
the tests is not reachable. Open `http://localhost:5173/` in a normal browser
first. If Vite printed a different port, set `WANDORA_BASE_URL` to that URL.

If Alembic prints `Multiple head revisions are present`, use `upgrade heads`
instead of `upgrade head`.

If Selenium cannot obtain a browser driver, make sure Chrome or Edge is
installed and that the machine has internet access the first time Selenium
Manager resolves the matching driver.

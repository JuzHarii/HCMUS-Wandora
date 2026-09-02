# PA5 Selenium E2E Tests

This folder contains the automated browser tests for PA5. The suite uses Selenium WebDriver with pytest and tests the application as a user would use it through the frontend.

## Assignment Coverage

PA5 requires automated testing for at least two use cases, with at least two scenarios per use case. This suite covers:

| Use case | Scenario | Pytest script | Result |
| --- | --- | --- | --- |
| UC01 - Trip Creation and Preference Input | Valid trip details are accepted and the user reaches the itinerary review/generation step. | `tests/e2e/tests/test_uc01_trip_creation.py::test_tc_uc01_01_successful_trip_creation_reaches_review` | Passed |
| UC01 - Trip Creation and Preference Input | End date before start date is rejected with a validation message. | `tests/e2e/tests/test_uc01_trip_creation.py::test_tc_uc01_03_invalid_date_order_blocks_submission` | Passed |
| UC02 - AI Itinerary Generator | A valid trip can generate an itinerary preview with activities. | `tests/e2e/tests/test_uc02_itinerary_generation.py::test_tc_uc02_01_successful_ai_preview_generation` | Passed |
| UC02 - AI Itinerary Generator | The user can bypass AI generation by starting with a blank itinerary and saving it. | `tests/e2e/tests/test_uc02_itinerary_generation.py::test_tc_uc02_03_blank_itinerary_can_be_saved` | Passed |

The suite also includes two authentication smoke tests in `tests/e2e/tests/test_authentication.py`. They are useful checks, but they are not counted as the two PA5 use cases above.

Login/sign-up is performed automatically by the `authenticated_driver` pytest fixture. UC01 and UC02 require a logged-in user, so authentication is treated as a precondition for those flows.

## Files

```text
tests/e2e/
├── config.py                         Selenium runtime settings and CSS selectors
├── conftest.py                       WebDriver, login, and screenshot fixtures
├── pages/                            Page Object helpers
└── tests/                            Pytest test cases
```

## One-Time Setup

Run these commands from the repository root:

```powershell
git clone https://github.com/JuzHarii/HCMUS-Wandora.git
cd HCMUS-Wandora
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
python -m pip install --upgrade pip
python -m pip install -r src/backend/requirements.txt
python -m pip install -r tests/e2e/requirements.txt
npm --prefix src/frontend install
```

If the repository is already cloned, start from `cd HCMUS-Wandora`.

Use a development/test database. For a simple local run, set `DATABASE_URL=sqlite:///./wandora.db` in the root `.env`. The tests create temporary users and trips through the browser.

## Start The App

Open three PowerShell terminals. Keep Terminal 1 and Terminal 2 running while Terminal 3 executes pytest.

### Terminal 1 - Backend

```powershell
cd HCMUS-Wandora
.\.venv\Scripts\Activate.ps1
python -m alembic -c src/backend/alembic.ini upgrade heads
python -m uvicorn --app-dir src/backend main:app --reload --port 8000
```

The backend is ready when you see:

```text
Application startup complete.
Uvicorn running on http://127.0.0.1:8000
```

Quick checks:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/health/db
```

### Terminal 2 - Frontend

```powershell
cd HCMUS-Wandora
npm --prefix src/frontend run dev
```

The frontend is ready when Vite prints a local URL, usually:

```text
Local: http://localhost:5173/
```

The default Selenium target is `http://localhost:5173`.

## Run The Tests

### Terminal 3 - Full PA5 Selenium Suite

```powershell
cd HCMUS-Wandora
.\.venv\Scripts\Activate.ps1
python -m pytest tests/e2e/tests -v
```

Expected summary:

```text
6 passed
```

### Run Only One PA5 Use Case

```powershell
python -m pytest tests/e2e/tests/test_uc01_trip_creation.py -v
python -m pytest tests/e2e/tests/test_uc02_itinerary_generation.py -v
```

### Run With A Visible Browser

By default the tests run headless. To watch the browser:

```powershell
$env:WANDORA_HEADLESS="false"
python -m pytest tests/e2e/tests -v
```

Reset it when you want headless mode again:

```powershell
Remove-Item Env:\WANDORA_HEADLESS
```

## Runtime Options

| Variable | Default | Purpose |
| --- | --- | --- |
| `WANDORA_BASE_URL` | `http://localhost:5173` | Frontend URL used by Selenium. Set this if Vite runs on another port. |
| `WANDORA_BROWSER` | `chrome` | Browser to use: `chrome`, `edge`, or `firefox`. |
| `WANDORA_HEADLESS` | `true` | Set to `false`, `0`, or `no` to watch the browser. |
| `WANDORA_TIMEOUT` | `10` | Default UI wait timeout in seconds. |
| `WANDORA_AI_TIMEOUT` | `45` | Longer wait timeout for itinerary generation. |
| `WANDORA_CHROMEDRIVER` | unset | Optional explicit ChromeDriver path. |
| `WANDORA_EDGEDRIVER` | unset | Optional explicit EdgeDriver path. |
| `WANDORA_GECKODRIVER` | unset | Optional explicit GeckoDriver path. |
| `WANDORA_CHROME_BINARY` | unset | Optional Chrome binary path. |

Example for a different Vite port:

```powershell
$env:WANDORA_BASE_URL="http://localhost:5174"
python -m pytest tests/e2e/tests -v
```

## Screenshots

When a test fails, the fixture saves a screenshot in:

```text
tests/e2e/screenshots/
```

Use the screenshot together with the pytest error to determine whether the app failed to load, a selector was missing, or a validation/result assertion failed.

## Troubleshooting

### `net::ERR_CONNECTION_REFUSED`

Selenium cannot reach the frontend URL. Keep Terminal 2 running, open the Vite URL manually in a normal browser, and make sure `WANDORA_BASE_URL` matches the URL printed by Vite.

### Browser opens then closes immediately

This is normal when a test fails early or when headless mode is enabled. Re-run with `$env:WANDORA_HEADLESS="false"` if you want to observe the flow.

### Alembic says multiple heads are present

Use:

```powershell
python -m alembic -c src/backend/alembic.ini upgrade heads
```

Do not use `upgrade head` for this repository.

### Backend starts but tests still fail

Confirm both app processes are alive:

```text
http://127.0.0.1:8000/health/db
http://localhost:5173/
```

Also confirm the frontend is calling the backend at `http://127.0.0.1:8000`. If needed, set `VITE_API_BASE_URL` in `src/frontend/.env`.

### Selenium cannot obtain a browser driver

Install or update Chrome/Edge/Firefox. Selenium Manager can resolve the matching driver automatically, but the first run may need internet access.

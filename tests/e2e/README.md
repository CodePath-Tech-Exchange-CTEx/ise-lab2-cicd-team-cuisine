# End-to-End Testing

This folder contains the initial E2E test scaffold for the Team Cuisine app.

## Running the tests

1. Start the local app:

```bash
streamlit run app.py
```

2. In another terminal, install dev dependencies and Playwright browsers if needed:

```bash
pip install -r requirements/base.txt -r requirements/dev.txt
python -m playwright install chromium
```

3. Run the E2E tests:

```bash
E2E_BASE_URL=http://localhost:8080 pytest tests/e2e
```

4. If needed, use a custom URL:

```bash
E2E_BASE_URL=http://127.0.0.1:8080 pytest tests/e2e
```

5. To run all E2E tests with the helper script:

```bash
./run-e2e.sh
```

## Notes

- This folder is now organized by journey flow:
  - `landing/` for homepage and smoke coverage
  - `auth/` for login and authentication flows
  - `navigation/` for logged-in navigation journeys such as Friends Activity
- Future tests can be added under these folders or new journey directories such as `profile/`, `bets/`, and `analytics/`.

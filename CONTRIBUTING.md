# Contributing to Airbets

Guidelines so the whole team stays aligned. Follow these when making changes and before pushing.

---

## 1. Work on a branch (don’t push directly to main)

- **Create a branch for every piece of work.** Don’t push straight to `main`. Open a PR from your branch so others can review and CI can run.
- **Name branches with a type prefix and short description** (kebab-case). Examples:
  - `feature/available-bets-dashboard`
  - `bugfix/login-redirect`
  - `chore/restructure-and-guidelines`
  - `docs/update-readme`
- Use a prefix that fits: `feature/`, `bugfix/`, `chore/`, `docs/`, etc.

---

## 2. Before you push

- **Double-check what you're committing.** Run `git status` and `git diff` (or your IDE’s equivalent). Make sure you're not pushing:
  - **Env files and secrets:** `.env`, `.env.local`, or any file with API keys or credentials.
  - **Non-essential files:** Virtual envs (`.venv`, `venv/`, `env/`), `__pycache__/`, `.pytest_cache/`, IDE/project files (e.g. `.idea/`), OS junk (`.DS_Store`), or other local-only files.
- **Rely on `.gitignore`.** If something shouldn’t be in the repo, add it to `.gitignore` and don’t force-add it.
- **Run tests.** From project root with the project venv: `pytest tests/`. Fix failing tests before pushing.
- **Format and lint your code** so CI passes. From project root with the project venv:
  - Format: `black .` (or format on save in your editor). We use Black for style.
  - Lint: `ruff check .` or `flake8 .` (CI runs flake8). Fix reported errors before pushing.
  - If you’re unsure, run `black .` and `flake8 .` (or `ruff check .`) before committing. The same checks run on push/PR in GitHub Actions.

---

## 3. Static assets: CSS and JS

- **Keep CSS and JavaScript separate from HTML** where possible.
- **Use a dedicated static folder** (e.g. `static/` or `static/css/`, `static/js/`) for styles and scripts. Reference them from HTML instead of inlining.
- For existing Streamlit custom components that use inline CSS/JS, prefer moving styles and scripts into `static/` when you touch those files.

---

## 4. Commit messages

- **Subject (first line):** Short, clear summary of what changed. Required.
  - Example: `Restructure project skeleton: data/, tests/, pages/`
- **Body (description):** Optional. When you add one:
  - Start with one or two sentences on *why* (goal or benefit).
  - Use bullets to say *what is where* or what changed, not “add/remove”. Prefer “data/: hardcoded bets and categories” over “Add data/ with bets.”

Example with body:

```
Restructure project skeleton: data/, tests/, pages/

Restructure so hardcoded data, tests, and Streamlit pages live in dedicated
folders. Keeps data swappable for an API later, tests in one place for pytest,
and pages ready for the available-bets dashboard.

- data/: hardcoded bets (get_available_bets, get_bet_categories) and categories
- tests/: test_modules.py, test_data_fetcher.py (moved from root)
- pages/: .gitkeep for Streamlit multipage (e.g. available-bets dashboard)
```

---

## 5. Where things live

| Purpose | Location | Notes |
|--------|-----------|--------|
| **Mock / hardcoded data** | `data/` | e.g. `data/bets.py` for bets and categories. Replace with API (Kalshi/Polymarket) later. |
| **Tests** | `tests/` | `test_*.py` only. Run with `pytest tests/` from project root. |
| **Streamlit pages** | `pages/` | One file per page, e.g. `1_Available_bets.py`. |
| **Custom HTML components** | `custom_components/` | HTML used by `modules.py` via `internals.create_component()`. |
| **App entrypoint** | `app.py` | Run with `streamlit run app.py`. |
| **Reusable UI logic** | `modules.py` | Display helpers (e.g. bet card). |
| **Dependencies** | `requirements/base.txt`, `requirements/dev.txt` | Root `requirements.txt` points at base. Install dev with `pip install -r requirements/dev.txt` after base. |

- **Always work from the project root** for running the app and tests.
- **Use a virtual environment** and install deps there (`python -m venv .venv`, then `pip install -r requirements.txt` and optionally `-r requirements/dev.txt`).

---

## 6. Stay updated with the project

- **Check the project board** (e.g. GitHub Projects or your team’s board). Pick up or update tasks so everyone knows what’s in progress.
- **Use GitHub Issues** for bugs and feature ideas. Look for open issues before starting work; comment if you’re taking one. Link PRs to issues (e.g. “Fixes #12”) when relevant.
- **Sync with the team:** pull before you start, rebase or merge before opening a PR so your branch is up to date with `main`.

---

## 7. Other principles

- **Streamlit is mandatory** for the app.
- **One place for app data:** Hardcoded/mock data lives under `data/`; fetch functions can live in `data_fetcher.py` and call into `data/`.
- **Don’t commit secrets or env-specific config** that differs per machine (use `.env` and keep it ignored).
- When in doubt, ask in the team channel or open a short PR for review.

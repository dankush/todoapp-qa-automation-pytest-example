# React Cool Todo App QA Automation

A Pytest & Playwright-based automation framework for end-to-end testing of the React Cool Todo App (https://react-cool-todo-app.netlify.app). Implements a Page Object Model (POM) with reusable fixtures and configurations to streamline test development and CI integration.

## Table of Contents
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Running Tests](#running-tests)
- [Fixtures & Configuration](#fixtures--configuration)
- [Design Patterns](#design-patterns)
- [CI/CD Integration](#cicd-integration)
- [Logging & Reports](#logging--reports)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)


## Project Structure
```
├── pages/                # Page Object Models for UI interactions
├── tests/                # Pytest test suites and fixtures
├── config/               # Environment and test data configs
├── utils/                # Helpers (e.g., generators, data factories)
├── pytest.ini            # Pytest settings and base URL
├── requirements.txt      # Python dependencies
└── README.md             # Project overview
```

## Installation & Setup
```bash
# Python 3.9+ recommended
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```
- `ruff` for linting, `pytest` for test execution, `pytest-playwright` for browser automation.
- Optional: create a `.env` with `BASE_URL` or override via `pytest.ini`.

## Running Tests
```bash
# Headless (default)
pytest -v
# Headed with slowmo (ms)
pytest --headed --slowmo=100 -v -s
```
- Run specific tests: `pytest tests/test_todo_app.py::TestTodoApp::test_add_task_success`
- CI: integrate commands in your pipeline; use `--junitxml=report.xml` for JUnit output.

## Fixtures & Configuration
- `conftest.py`: defines `playwright`, `browser`, `context`, `page`, and `browser_context_args` fixtures.
- Base URL and markers configured in `pytest.ini`.
- Environment variables can be loaded via `pytest-dotenv` or custom logic.

## Design Patterns
- **Page Object Model (POM)**: `pages/` encapsulates UI actions and locators.
- **Factory**: dynamic data generation in `utils/` or test helpers.

## CI/CD Integration
- Example: **GitHub Actions** workflow can install dependencies, run `pytest`, and upload artifacts.
- Status badges (e.g., build, coverage) can be added to this README.

## Logging & Reports
- Playwright traces and screenshots configured via `pytest-playwright` flags.
- Use `--html=report.html` or Allure for rich HTML reports.
- Logs are printed to console and can be captured in CI logs.

## Contributing
1. Fork and clone the repo.
2. Create a feature branch and install pre-commit hooks.
3. Write tests under `tests/` and POM classes under `pages/`.
4. Lint with `ruff .` and run `pytest` before PR.

## Troubleshooting
- **Element not found**: verify locators in POM and increase timeouts.
- **Strict mode violations**: use precise locators or disable strict mode selectively.
- **Session errors**: ensure browser fixtures are not reused across tests.
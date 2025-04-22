import pytest
from typing import Dict, Generator
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: Dict) -> Dict:
    """Override browser context args for all browsers."""
    return {
        **browser_context_args,
        "viewport": {
            "width": 1280,
            "height": 720,
        },
        # Video recording is handled by pytest-playwright's --video option
    }

@pytest.fixture(scope="session")
def playwright() -> Generator[Playwright, None, None]:
    """Fixture for creating a Playwright instance."""
    with sync_playwright() as playwright:
        yield playwright

@pytest.fixture(scope="session")
def browser_type(playwright: Playwright) -> str:
    """Return the browser type to use."""
    return "chromium"

@pytest.fixture(scope="session")
def browser(playwright: Playwright, browser_type: str, pytestconfig) -> Generator[Browser, None, None]:
    """Fixture for creating a browser instance respecting --headed and --slowmo."""
    slowmo = pytestconfig.getoption("slowmo")
    headed = pytestconfig.getoption("headed")
    browser_instance = getattr(playwright, browser_type).launch(
        headless=not headed,
        slow_mo=slowmo
    )
    yield browser_instance
    browser_instance.close()

@pytest.fixture
def context(browser: Browser, browser_context_args: Dict) -> Generator[BrowserContext, None, None]:
    """Fixture for creating a browser context."""
    context = browser.new_context(**browser_context_args)
    yield context
    context.close()

@pytest.fixture
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """Fixture for creating a page instance."""
    page = context.new_page()
    yield page
    page.close()
"""Page fixtures for the Todo application tests."""
from typing import Generator
from playwright.sync_api import Page
import pytest
from pages.todo_page import CoolTodoPage
from pages.add_task_page import AddTaskPage
from config.config import BASE_URL

@pytest.fixture
def todo_page(page: Page) -> Generator[CoolTodoPage, None, None]:
    """Fixture that returns a configured CoolTodoPage instance.
    
    Args:
        page: The Playwright page object
        
    Yields:
        CoolTodoPage: A configured todo page object
    """
    page_object = CoolTodoPage(page)
    # Navigate to the app
    page_object.goto(BASE_URL)
    
    # Navigate done, yield for test
    yield page_object
    
    # Reset app state by clearing storage and reloading
    page_object.page.evaluate("() => window.localStorage.clear()")
    page_object.page.reload()

@pytest.fixture
def add_task_page(page: Page) -> Generator[AddTaskPage, None, None]:
    """Fixture that returns a configured AddTaskPage instance.
    
    Args:
        page: The Playwright page object
        
    Yields:
        AddTaskPage: A configured add task page object
    """
    page_object = AddTaskPage(page)
    # Navigate to the add task page
    page_object.goto(BASE_URL)
    
    yield page_object 
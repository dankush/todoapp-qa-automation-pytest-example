import pytest
import sys
import os
from datetime import datetime
from playwright.sync_api import expect

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pages.todo_page import CoolTodoPage
from tests.fixtures.page_fixtures import todo_page, add_task_page



class TestTodoApp:
    """Regression test suite for the React Cool Todo App."""

    def generate_unique_title(self, base: str) -> str:
        """Generates a unique task title based on timestamp."""
        return f"{base} {datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    @pytest.mark.tms("TC_REG_001")
    def test_add_task_success(self, todo_page: CoolTodoPage) -> None:
        """TC_REG_001: Verify successful creation of a basic task"""
        task_title = self.generate_unique_title("Test Task")
        task_description = "This task is created as part of a regression test"

        # Step 1–4: Add task
        todo_page.add_task(task_title, task_description)

        # Step 5: Assert task appears in the list
        expect(todo_page.get_task_locator(task_title)).to_be_visible()

        # Verify task was added successfully by checking visibility
        # (Already verified with the previous assertion)

    @pytest.mark.tms("TC_REG_002")
    def test_delete_task_success(self, todo_page: CoolTodoPage) -> None:
        """ TC_REG_002: Verify deletion of a task via the menu"""
        task_title = self.generate_unique_title("REG_TASK_002_ToDelete")
        task_description = "Task to be deleted"

        # Precondition: Create a task to delete
        todo_page.add_task(task_title, task_description)
        expect(todo_page.get_task_locator(task_title)).to_be_visible()

        # Step 1–4: Delete the task
        todo_page.delete_task(task_title)

        # Expected result: Task should no longer exist
        expect(todo_page.get_task_locator(task_title)).not_to_be_visible()

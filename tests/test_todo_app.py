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

    @pytest.mark.tms("TC_REG_003")
    def test_search_filters_task_correctly(self, todo_page: CoolTodoPage) -> None:
        """TC_REG_003: Verify searching for a specific task filters results accurately"""
        unique_title = self.generate_unique_title("REG_TASK_003_Unique")
        other_title = self.generate_unique_title("REG_TASK_003_Other")

        # Precondition: Create two distinct tasks
        todo_page.add_task(unique_title)
        todo_page.add_task(other_title)

        # Step 1-2: Search for the unique task
        todo_page.search_tasks("Unique")

        # Expected results: Only the matching task is visible
        expect(todo_page.get_task_locator(unique_title)).to_be_visible()
        expect(todo_page.get_task_locator(other_title)).not_to_be_visible()
        assert todo_page.get_visible_task_count() == 1

    @pytest.mark.tms("TC_REG_004")
    def test_clear_search_restores_task_list(self, todo_page: CoolTodoPage) -> None:
        """TC_REG_004: Verify clearing the search term restores full task list"""
        title1 = self.generate_unique_title("REG_TASK_004_One")
        title2 = self.generate_unique_title("REG_TASK_004_Two")

        # Precondition: Create two tasks and apply search filter
        todo_page.add_task(title1)
        todo_page.add_task(title2)
        todo_page.search_tasks("One")
        expect(todo_page.get_task_locator(title1)).to_be_visible()
        expect(todo_page.get_task_locator(title2)).not_to_be_visible()

        # Step 1: Clear the search input
        todo_page.clear_search()

        # Expected results: All tasks are visible again
        expect(todo_page.get_task_locator(title1)).to_be_visible()
        expect(todo_page.get_task_locator(title2)).to_be_visible()
        assert todo_page.get_visible_task_count() >= 2

    @pytest.mark.tms("TC_REG_005")
    def test_search_no_match_shows_empty(self, todo_page: CoolTodoPage) -> None:
        """TC_REG_005: Verify that searching for a non-existent task shows empty state"""
        # Precondition: Create a task to ensure we have content
        title = self.generate_unique_title("REG_TASK_005_Visible")
        todo_page.add_task(title)

        # Step 1: Search for a term that won't match any tasks
        todo_page.search_tasks("XYZ_NOMATCH_ZYX")

        # Expected result: Empty state message is displayed
        todo_page.expect_no_tasks()